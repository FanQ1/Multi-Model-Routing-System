from urllib import response
import uuid
from ..entity.database import Conversation, ConversationMessageLink, Message,SessionLocal
from router_service import router
from typing import List, Dict
from ..entity.vector_db import vector_orm

class MemoryManager:
    def __init__(self):
        self.conversation_summary = "Conversation started."
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
            return whole_messages
        except Exception as e:
            raise e
        
    # ============ memory methods ============
    def rewrite_query(self, query: str, db):
        """
        rewrite user query based on memory
        """
        try:
            # 1. create context (Summary S, Recent Messages {m-m...}, Query)
            context_prompt = self._build_context_prompt(query)

            # 2. call LLM to rewrite query
            response = router.get_response_from_model(
                user_query=context_prompt,
                best_model=['glm-4']
                )
            
            # 3. update work memory
            self._update_work_memory(user_msg=query, ai_msg=response)

            # 4. update long term memory asynchronously
            self._extract_and_update_memory(query, response)

            return response
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

            return f"{summary}\nRecent Messages:\n{recent_messages}\n{relevant_long_messages}\nUser Query: {query}"
        except Exception as e:
            raise e
        
    def _extract_and_update_memory(self, user_msg: str, ai_msg: str):
        """
        Extraction -> Update (ADD/UPDATE/DELETE/NOOP)
        """
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
        raw_facts = router.get_response_from_model(extract_prompt, best_model=["glm-4"])

        
        # 2. update long term memory based on extracted facts
        for fact in raw_facts:
            # 2.1 retrieve similar memories
            similar_memories = vector_orm.retrieve_memory(
                collection_name="long_term_memory",
                query_vector=vector_orm.get_offline_embedding(fact),
                top_k=self.top_k_similar_memories
            )
            
            # 2.2. use llm to decide operation
            decision_prompt = f"""
            Candidate Fact: {fact}
            Existing Similar Memories: {similar_memories}
            
            Decide operation: ADD, UPDATE, DELETE, or NOOP.
            """
            operation = router.get_response_from_model(decision_prompt, best_model=["glm-4"])
            
            # 2.3. perform operation
            if operation == "ADD":
                vector_orm.add_memory(fact)
            elif operation == "UPDATE":
                vector_orm.update_memory(fact, similar_memories[0].id) 
            elif operation == "DELETE":
                vector_orm.delete_memory(similar_memories[0].id)

        self._async_update_summary()

        
    # ============ helper methods ============
    def _format_work_memory(self):
        return "\n".join([f"{m['role']}: {m['content']}" for m in self.work_memory])
    
    def _update_work_memory(self, user_msg, ai_msg):
        self.work_memory.append({"role": "user", "content": user_msg})
        self.work_memory.append({"role": "assistant", "content": ai_msg})
        # sliding window
        if len(self.work_memory) > self.work_memory_limit * 2: # *2 because each interaction has user and assistant messages
            self.work_memory = self.work_memory[-(self.work_memory_limit * 2):]

    def _async_update_summary(self):
        # TODO: 异步更新摘要
        pass



memory_manager = MemoryManager()