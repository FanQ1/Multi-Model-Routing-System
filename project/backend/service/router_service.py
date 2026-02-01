
from typing import Dict, List, Optional
from datetime import datetime
import json

import torch
# import encoder and inference scripts
import sys
import os
from zhipuai import ZhipuAI
from settings import Settings
from router.Q_encoder import QSpaceEncode
from router.M_encoder import MSpaceEncode
from service.capability_service import capability_service

class RouterService:
    """
    includes methods for routing, calling models, etc.
    """
    def __init__(self):
        self.client = ZhipuAI(api_key=Settings().get_api())
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.routing_history = []
        self.load_router_model()

    def load_router_model(self):
        """Load or initialize the routing decision model"""
        self.q_encoder = QSpaceEncode().to(self.device)
        self.m_encoder = MSpaceEncode().to(self.device)

        # load pth model here
        checkpoint_path = os.path.join(os.path.dirname(__file__), '..', '..', 'router', 'checkpoints', 'router_model.pth')
        if os.path.exists(checkpoint_path):
            checkpoint = torch.load(checkpoint_path)
            self.q_encoder.load_state_dict(checkpoint['q_encoder'])
            self.m_encoder.load_state_dict(checkpoint['m_encoder'])

            self.q_encoder.eval()
            self.m_encoder.eval()
            print("Router model loaded successfully.")
        else:
            print("Router model checkpoint not found. Please train the model first.")
    
    def route_query(self, user_query: str) -> Dict:
        """
        Route a user query to the best available model.

        Args:
            user_query: The user's query text
            required_capability: Optional specific capability required
        """
        with torch.no_grad():
            # 1. Encode the user query to get its capability vector
            embedding_vector = self.q_encoder.get_embedding_tensor(user_query, tenant_id="tenant_A")
            q_vector = self.q_encoder.forward(embedding_vector)
            # 2. get available models from capability_service
            model_list = capability_service.get_model_list()
            model_abilities = capability_service.get_model_ability_matrix()

            # 3. inference to get top-k models
            models_asc = []
            for i in range(len(model_list)):
                m_input_tensor = torch.tensor(model_abilities[i], dtype=torch.float32).to(self.device)
                m_vector = self.m_encoder.forward(m_input_tensor).squeeze()
                # 3.1 calculate similarity score
                score = torch.dot(q_vector, m_vector).item()
                models_asc.append((model_list[i], score))
                print(f"Model: {model_list[i]}, Score: {score}")

            models_asc.sort(key=lambda x: x[1], reverse=True)
            print("Models sorted by score:", models_asc)

            return [model[0] for model in models_asc[0:2]] # return top-2 models

    def get_response_from_model(self, user_query: str, best_model: list[str]) :
        """
        get response from the best available model for a user query.

        Args:
            user_query: The user's query text
            best_model: top-k best model list
        """
        # 1. call LLM to get response. we use one round interaction here.
        # need to be multiple round interaction in production
        try:
            # print("Best model selected:", best_model[0], "for the query:", user_query)
            response = self.client.chat.completions.create(
                model='glm-4',
                messages=[
                    {"role": "user", "content": user_query}
                ],
                max_tokens=1024,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise e

        
    

# Global router service instance
router = RouterService()
