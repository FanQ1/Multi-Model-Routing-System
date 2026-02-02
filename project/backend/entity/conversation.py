from typing import List, Dict

class ConversationSession:
    def __init__(self, id: str):
        self.conversation_id = id
        self.conversation_summary = ""
        self.work_memory: List[Dict] = []
        self.work_memory_limit = 10  # sliding window size
        self.top_k_similar_memories = 5