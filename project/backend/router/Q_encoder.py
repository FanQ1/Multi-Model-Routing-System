import torch
import torch.nn as nn
from Llm_client import LLM

class QSpaceEncode(nn.Module):
    """
    将查询文本和id转换为混合向量
    混合向量包括 可解释性向量 和 隐向量
    """
    def __init__(self, latent_dim=128):
        super().__init__()

        self.llm_client = LLM()
        self.embedding_dim = 384
        self.projection_layer = nn.Sequential(
                                    nn.Linear(384, 256),
                                    nn.ReLU(),
                                    nn.Linear(256, 128)
                                )        

        # 租户配置
        self.tenant_configs = {
            "tenant_A": {"preference": "quality"},
            "tenant_B": {"preference": "cost"},
            "tenant_C": {"preference": "latency"},
        }

    # -- 核心流程 -- 
    def get_embedding_tensor(self, query_text, tenant_id: str):
        """
        调用embedding 获取tensor
        """
        embedding_tensor = self.llm_client.get_offline_embedding(query_text)
        return embedding_tensor.clone() # 将推理张量（inference tensor)转为普通张量
        
    
    def forward(self, query_embedding: torch.Tensor):
        device = next(self.projection_layer.parameters()).device
        query_embedding = query_embedding.to(device)
        
        return self.projection_layer(query_embedding)
    

    