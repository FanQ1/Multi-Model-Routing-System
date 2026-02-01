import torch
import torch.nn as nn
import torch
import torch.nn as nn

class MSpaceEncode(nn.Module):
    """
    将模型探测分数转换为 Z 空间向量
    （训练时只使用probe_scores，meta_scalars在推理时单独处理）
    """
    def __init__(self, latent_dim=128, probe_dim=5):
        super().__init__()
        
        # 只使用探测任务分数
        self.probe_dim = probe_dim
        self.projection_layer = nn.Sequential(
                                    nn.Linear(5, 64),
                                    nn.ReLU(),
                                    nn.Linear(64, 128)
                                )

    def encode(self, model_probe_scores: list):
        """
        仅使用探测分数生成 z_M
        
        :param model_probe_scores: 该模型在探测集上的归一化分数 (5维)
        :return: 包含 z_M 的字典
        """
        # 转换为张量并通过投影层
        input_tensor = torch.tensor(model_probe_scores, dtype=torch.float32)
        z_M = self.projection_layer(input_tensor)
        
        return {
            "z_M": z_M,
            "raw_input": input_tensor
        }
    
    def forward(self, probe_scores_tensor):
        """
        前向传播接口，方便训练脚本调用
        
        :param probe_scores_tensor: 已经转换为张量的探测分数
        :return: z_M 向量
        """
        return self.projection_layer(probe_scores_tensor)
