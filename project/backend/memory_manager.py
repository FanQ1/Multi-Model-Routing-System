class MemoryManager:
    def __init__(self):
        self.extract = []
        self.work_memory = [{}]
        self.work_memory_limit = 5  # sliding window size
        self.work_memory_exceed_num = 2  # number of memories to extract when exceeding limit
        self.work_memory_len = 0 # current length, if exceed limit + exceed_num, extract exceed_num of memory

    # ============ work memory methods ============
    def store_work_memory(self, key, value):
        """
        store work memory, by using sliding window
        and invoke this after each response from model
        """
        self.work_memory[key] = value

    def retrieve_work_memory(self, value):
        """
        retrieve work memory
        """
        return self.work_memory
    
    # ============ extractor methods ============
    def get_extract(self):
        """
        get extract
        """
        return self.extract
    
    def store_extract(self, value):
        """
        store extract
        """
        self.extract.append(value)

    # ============ long term memory methods ============
    def store_long_term_memory(self, key, value):
        pass

    def retrieve_long_memory(self, key):
        """
        retrieve long term memory from vector db
        """
        return self.work_memory.get(key, None)

    def delete_memory(self, key):
        """
        delete memory from vector db
        """
        if key in self.work_memory:
            del self.work_memory[key]


memory_manager = MemoryManager()