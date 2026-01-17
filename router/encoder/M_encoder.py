import torch
import torch.nn as nn
import numpy as np

class MSpaceEncode(nn.Module):
    """
    将模型探测分数和元数据转换为 Z 空间向量
    """
    def __init__(self, latent_dim=128):
        super().__init__()
        
        # 6 个探测任务分数 (math, code, creative_writing, expert, safety, long_query)
        self.probe_dim = 6 
        # 3 个标量特征 (cost_norm, latency_norm, context_norm)
        self.meta_scalar_dim = 3 
        total_input_dim = self.probe_dim + self.meta_scalar_dim

        self.projection_layer = nn.Linear(total_input_dim, latent_dim)

    def encode(self, model_probe_scores: list, model_meta_scalars: list):
        """
        :param model_probe_scores: 该模型在探测集上的归一化分数
        :param model_meta_scalars: 归一化后的元数据
        """
        # 1. 拼接输入特征
        input_features = model_probe_scores + model_meta_scalars
        input_tensor = torch.tensor(input_features, dtype=torch.float32)
        
        # 2. 通过投影层生成 z_M
        z_M = self.projection_layer(input_tensor)
        
        return {
            "z_M": z_M,
            "raw_input": input_tensor
        }

