from zhipuai import ZhipuAI
from ..settings import Settings
from ..logger import logger

from sentence_transformers import SentenceTransformer 
import torch
import torch.nn as nn
class LLM:
    def __init__(self):
        self.client = ZhipuAI(api_key=Settings().get_api())

        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embedding_model.eval()
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.embedding_model.to(device)

        logger.info("LLM init finished.")
    
    def get_offline_embedding(self, query):
        try:
            response = self.embedding_model.encode(
                query, 
                convert_to_tensor=True,
                show_progress_bar=False 
            )
            return response
        except Exception as e:
            logger.info("embedding error: %s")
            raise e

    
    def get_response(self, message, temperature: float = 0.0, max_tokens: int = 4000):
        if message is None:
            return False
        
        try:
            response = self.client.chat.completions.create(
                model="glm-4",
                messages=message,
                temperature=temperature,
                max_tokens=max_tokens
            )

            return response.choices[0].message.content
        except Exception as e:
            logger.info("calling LLM error: %s")
            raise e


