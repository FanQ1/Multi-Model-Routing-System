import uuid
from entity.database import Conversation, ConversationMessageLink, Message,SessionLocal, async_session_maker
from service.router_service import router
from typing import List, Dict
from entity.vector_db import vector_orm
from logger import logger
import datetime
import asyncio
import uuid

from sqlalchemy import select, delete
class MemoryManager:
    def __init__(self):
        self.conversation_summary = ""
        self.work_memory: List[Dict] = []
        self.work_memory_limit = 10  # sliding window size
        self.top_k_similar_memories = 5

        

    # ============ conversation methods ============
    def get_all_conversations(self, db):
        """
        get all conversations from database
        """
        try:
            conversation_ids = db.query(Conversation).all()
            return [conv.id for conv in conversation_ids]
        except Exception as e:
            raise e
        
    def register_conversation(self, db):

        """
        register a new conversation in database
        """
        try:
            conversation = Conversation(id=uuid.uuid4())
            db.add(conversation)
            db.commit()
            # update work memory
            self.work_memory = []
            
            return str(conversation.id)
        except Exception as e:
            db.rollback()
            raise e

    def load_existing_memories(self, conversation_id, db):
        """
        load existing memories from database
        """
        try:
            # select * from Message where id in (select message_id from ConversationMessageLink where conversation_id=conversation_id)
            tmp = db.query(ConversationMessageLink).filter(ConversationMessageLink.conversation_id == conversation_id).all()
            records = db.query(Message).filter(Message.id.in_([x.message_id for x in tmp])).order_by(Message.timestamp).all()

            whole_messages = []
            for record in records:
                whole_messages.append({
                    "role": record.message_type,
                    "content": record.content
                })
                
            self.work_memory = whole_messages[-(self.work_memory_limit * 2):]  # load into work memory with sliding window
            # return whole messages    
            print("Loaded existing memories:", whole_messages)
            print("Current work memory:", self.work_memory)
            return whole_messages
        except Exception as e:
            raise e
        
    async def delete_conversation(self, conversation_id):
        """
        delete a conversation and its related messages from database
        delete conversation_message_link、conversation and messages
        """
        try:
            async with async_session_maker() as db:
                async with db.begin():
                    # find all message_id by using conversation_id
                    stmt_link = select(ConversationMessageLink.message_id)\
                            .where(ConversationMessageLink.conversation_id == conversation_id)
                    result = await db.execute(stmt_link)
                    message_ids = result.scalars().all()

                    if message_ids:
                        # delete all messages by message_id
                        stmt_del_msg = delete(Message)\
                            .where(Message.id.in_(message_ids))
                        
                        await db.execute(stmt_del_msg)

                    # delete links
                    stmt_del_link = delete(ConversationMessageLink)\
                        .where(ConversationMessageLink.conversation_id == conversation_id)
                    await db.execute(stmt_del_link)

                    # delete conversation
                    stmt_del_conv = delete(Conversation)\
                        .where(Conversation.id == conversation_id)
                    await db.execute(stmt_del_conv)

                logger.info(f"Conversation {conversation_id} deleted")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete conversation {conversation_id}: {str(e)}")
            raise e
        
    # ============ memory methods ============
    async def rewrite_query(self, query: str) -> str:
        """
        rewrite user query based on memory
        """
        try:
            # 1. create context (Summary S, Recent Messages {m-m...}, Query)
            context_prompt = self._build_context_prompt(query)


            # 2. call LLM to rewrite query
            response =await self._rewirte_query_with_llm(
                query=query,
                memory=context_prompt
                )
            print("Rewritten Query:", response)

            return response
        except Exception as e:
            raise e

    async def store_memory(self, user_msg: str, ai_msg: str, conversation_id):
        """
        store work memory and long term memory

        """
        # start a new database session
        # if injected db session is used here, may fail because of life cycle issue

        try:
            # 1. update work memory (in ram)
            self._update_work_memory(user_msg=user_msg, ai_msg=ai_msg)

            # 2. store in database
            await self._update_message_pair_in_database(user_msg=user_msg, ai_msg=ai_msg, conversation_id=conversation_id)

            # 3. update long term memory
            await self._update_long_term_memory(user_msg=user_msg, ai_msg=ai_msg)
        except Exception as e:
            logger.warning(str(e))
            raise e


    async def _update_message_pair_in_database(self, user_msg: str, ai_msg: str, conversation_id):
        db = SessionLocal()
        # create message records
        try:
            db.begin()

            user_message = Message(
                id=uuid.uuid4(),
                message_type="user",
                content=user_msg,
                timestamp=datetime.utcnow()
            )
            ai_message = Message(
                id=uuid.uuid4(),
                message_type="assistant",
                content=ai_msg,
                timestamp=datetime.utcnow()
            )

            db.add(user_message)
            db.add(ai_message)

            db.flush()

            # create conversation message links
            link1 = ConversationMessageLink(
                conversation_id=conversation_id,
                message_id=user_message.id
            )
            link2 = ConversationMessageLink(
                conversation_id=conversation_id,
                message_id=ai_message.id
            )

            db.add(link1)
            db.add(link2)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update message pair in database: {str(e)}")
            raise e
        finally:
            db.close()
            
    async def _update_long_term_memory(self, user_msg: str, ai_msg: str):
        """
        update long term memory
        """
        try:
            # 1. (summary, work_memory) work memory already updated in previous step
            extract_prompt = f"""
            Summary: {self.conversation_summary}
            Recent: {self._format_work_memory()}

            Current Exchange:
            User: {user_msg}
            Assistant: {ai_msg}
            
            Task: Extract salient facts or updates from the current exchange.
            Output as a JSON list of facts.
            """
            
            # use llm to extract facts from user query and ai response
            raw_facts = await router.get_response_from_model(extract_prompt, best_model=["glm-4"])

            async def process_one_fact(fact):
                similar_memories = vector_orm.retrieve_memory(
                    collection_name="long_term_memory",
                    query=fact,
                    top_k=self.top_k_similar_memories
                )

                decision_prompt = f"""
                Candidate Fact: {fact}
                Existing Similar Memories: {similar_memories}
                
                Decide operation: ADD, UPDATE, DELETE, or NOOP.
                """

                operation = await router.get_response_from_model(decision_prompt, best_model=["glm-4"])
                 
                if operation == "ADD":
                    vector_orm.add_memory(fact)
                elif operation == "UPDATE":
                    vector_orm.update_memory(fact, similar_memories[0].id) 
                elif operation == "DELETE":
                    vector_orm.delete_memory(similar_memories[0].id)

                return operation
            
            tasks = [process_one_fact(fact) for fact in raw_facts]
            results = await asyncio.gather(*tasks)
            logger.info(f"Processed {len(results)} facts in parallel.")    

        except Exception as e:
            raise e
        
    def _build_context_prompt(self, query: str) -> str:
        """
        build context prompt from work memory and summary
        """
        try:
            # get Summary S
            summary = f"Conversation Summary: {self.conversation_summary}\n"

            # get Recent Messages {m-m...}
            recent_messages = self._format_work_memory()

            # get long term memory 
            relevant_long_messages = vector_orm.retrieve_memory(
                collection_name="long_term_memory",
                query=query,
                top_k=self.top_k_similar_memories
            )
            long_term_memories_content = []
            if relevant_long_messages and relevant_long_messages.points:
                for point in relevant_long_messages.points:
                    if point.payload and "content" in point.payload:
                        long_term_memories_content.append(point.payload["content"])

            long_term_memories_str = "\n".join(long_term_memories_content) if long_term_memories_content else "No relevant long term memories found."

            print(f"summary:{summary}\nRecent Messages:\n{recent_messages}\nlong_term_memories:{long_term_memories_str}")
            return f"summary:{summary}\nRecent Messages:\n{recent_messages}\nlong_term_memories:{long_term_memories_str}"

        except Exception as e:
            raise e
        

    async def _rewirte_query_with_llm(self, query: str, memory: str) -> str:
        prompt = f"""You are a query rewriting assistant. Your task is to rewrite the user's query based on the conversation context.

            ## Conversation Context:
            {memory}

            ## Original User Query:
            {query}

            ## Instructions:
            1. If the conversation context contains relevant information that helps clarify or complete the user's intent, rewrite the query to incorporate that context.
            2. If the conversation context is NOT relevant to the current query, return the original query as-is (or fix only grammatical errors if needed).
            3. For simple greetings like "hello", "hi", etc., return the original query unchanged.
            4. Do NOT add any explanations, context, or markdown formatting.
            5. Output ONLY the rewritten query.

            ## Rewritten Query:"""     


        response = await router.get_response_from_model(
            user_query=prompt,
            best_model=['glm-4']
            )
        
        return response
    # ============ helper methods ============
    def _format_work_memory(self):
        if not self.work_memory:
            return "No recent messages."
        return "\n".join([f"{m['role']}: {m['content']}" for m in self.work_memory])
    
    def _update_work_memory(self, user_msg, ai_msg):
        self.work_memory.append({"role": "user", "content": user_msg})
        self.work_memory.append({"role": "assistant", "content": ai_msg})
        # sliding window
        if len(self.work_memory) > self.work_memory_limit * 2: # *2 because each interaction has user and assistant messages
            self.work_memory = self.work_memory[-(self.work_memory_limit * 2):]
        print("Updated work memory:", self.work_memory)


    def _async_update_summary(self, user_msg: str, ai_msg: str):
        prompt = f"""
            Old Summary: {self.conversation_summary}
            New Messages:
            User: {user_msg}
            Assistant: {ai_msg}
            
            Task: Update the summary to include new information.
            """

        # use llm to generate new summary
        response = router.get_response_from_model(
            user_query=prompt,
            best_model=['glm-4']
            )
        self.conversation_summary = response

        


memory_manager = MemoryManager()