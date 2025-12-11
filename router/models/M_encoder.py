import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Any

class MSpaceEncoder(nn.Module):
    """
    根据模型在探测集上的表现分数，生成其能力向量 z_M。
    设计遵循了“潜在能力向量 + 可解释标量”的分离原则。
    """
    def __init__(self, probe_dim: int, latent_dim: int):
        """
        初始化 M-encoder。

        Args:
            probe_dim (int): 探测集分数的维度。例如，如果探测集有5个任务，这里就是5。
            latent_dim (int): 潜在空间 z_M 的维度，必须与 Q-encoder 的 latent_dim 一致。
        """
        super().__init__()
        
        # 这是核心的映射函数 f_M，一个简单的全连接层
        # 它将探测集分数（例如 [math_score, code_score, ...]）映射到 Z 空间
        self.probe_to_latent = nn.Linear(probe_dim, latent_dim)

    def forward(self, probe_scores: torch.Tensor) -> torch.Tensor:
        """
        f_M 的前向传播。

        Args:
            probe_scores (torch.Tensor): 模型在探测集上的分数向量。
                                        Shape: [probe_dim]

        Returns:
            torch.Tensor: 生成的潜在能力向量 z_M。 Shape: [latent_dim]
        """
        # 直接通过线性层进行映射
        z_M = self.probe_to_latent(probe_scores)
        return z_M

    def encode(self, model_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        对一个完整的模型记录进行编码，返回其所有表示。

        Args:
            model_record (Dict[str, Any]): 包含模型所有信息的字典。

        Returns:
            Dict[str, Any]: 包含 z_M 和可解释标量的字典。
        """
        # 1. 生成潜在能力向量 z_M
        probe_scores_tensor = torch.tensor(model_record['probe_scores'], dtype=torch.float32)
        z_M = self.forward(probe_scores_tensor)

        # 2. 提取可解释的标量
        interpretable_scalars = {
            "cost_per_1k_tokens": model_record['cost_per_1k_tokens'],
            "latency_p50_ms": model_record['latency_p50_ms'],
            "safety_rating": model_record['safety_rating'], # 可以是 1-5 的数字
            "max_context_length": model_record['max_context_length'],
        }
        
        # 注意：根据设计，我们在这里不拼接 z_M 和 scalars
        # 它们在路由决策中被分开使用

        return {
            "z_M": z_M,
            "interpretable_scalars": interpretable_scalars
        }

