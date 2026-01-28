class Settings:
    def __init__(self):
        self.api_key = "bc96281912324ccb8c22a185c5368a7c.Lk04auavEudR6HrP"
        self.postgresql_url = "postgresql://postgres:Fqysb111@127.0.0.1:5432/chatbot_db"

    def get_api(self):
        return self.api_key

    def get_postgresql_url(self):
        return self.postgresql_url