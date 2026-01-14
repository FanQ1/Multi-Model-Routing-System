import torch
import torch.nn as nn
import re
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import MultiLabelBinarizer
# -- 自定义库
from router.utils.config import TASK_TYPES, DOMAINS, REASONING_LEVELS, SAFETY_LEVELS, LENGTH_BUCKETS, TENANT_PREFERENCES
from router.utils.config import InterpretableType
import router.utils.interpretable_keywords as KEYWORDS  

# 
from router.models.Llm_client import LLM
from router.models.logger import logger
"""

"""

class QSpaceEncode(nn.Module):
    """
    将查询文本和id转换为混合向量
    混合向量包括 可解释性向量 和 隐向量
    """
    def __init__(self, latent_dim=128):
        super().__init__()

        self.llm_client = LLM()
        self.embedding_dim = 384
        self.projection_layer = nn.Linear(self.embedding_dim, latent_dim)

        # --- 正确初始化所有 MultiLabelBinarizer ---
        self.task_mlb = MultiLabelBinarizer(classes=TASK_TYPES)
        self.task_mlb.fit([TASK_TYPES])

        self.domain_mlb = MultiLabelBinarizer(classes=DOMAINS)
        self.domain_mlb.fit([DOMAINS])

        self.reasoning_mlb = MultiLabelBinarizer(classes=REASONING_LEVELS)
        self.reasoning_mlb.fit([REASONING_LEVELS])

        self.safety_mlb = MultiLabelBinarizer(classes=SAFETY_LEVELS)
        self.safety_mlb.fit([SAFETY_LEVELS])

        self.length_mlb = MultiLabelBinarizer(classes=LENGTH_BUCKETS)
        self.length_mlb.fit([LENGTH_BUCKETS])
        
        self.tenant_pref_mlb = MultiLabelBinarizer(classes=TENANT_PREFERENCES)
        self.tenant_pref_mlb.fit([TENANT_PREFERENCES])

        # 租户配置
        self.tenant_configs = {
            "tenant_A": {"preference": "quality"},
            "tenant_B": {"preference": "cost"},
            "tenant_C": {"preference": "latency"},
        }

    # --- 以下是生成可解释特征的方法，基于设定好的规则 --- 
    def detect_task_type(self, query: str):
        """
        检测查询文本的任务类型
        :param query: 查询文本
        :return: 任务类型
        """
        keywords = KEYWORDS.get_interpretable_keywords(InterpretableType.TASK_TYPE)

        detected_tasks = []
        for task, keys in keywords.items():
            if any(key in query.lower() for key in keys):
                detected_tasks.append(task)
        return detected_tasks if detected_tasks else ["code"] 
    
    def detect_domain(self, query: str):
        """
        检测查询文本的领域
        :param query: 查询文本
        :return: 领域
        """
        keywords = KEYWORDS.get_interpretable_keywords(InterpretableType.DOMAIN)
        
        detected_tasks = []
        for task, keys in keywords.items():
            if any(key in query.lower() for key in keys):
                detected_tasks.append(task)
        return detected_tasks if detected_tasks else ["general"] # 默认为通用
    
    def detect_safety(self, query: str):
        """
        检测查询文本的安全性
        :param query: 查询文本
        :return: 安全性
        """
        keywords = KEYWORDS.get_interpretable_keywords(InterpretableType.SAFETY)

        detected_tasks = []
        for task, keys in keywords.items():
            if any(key in query.lower() for key in keys):
                detected_tasks.append(task)
        return detected_tasks if detected_tasks else ["safe"]
    
    def detect_length(self, query: str):
        """
        检测查询文本的长度
        :param query: 查询文本
        :return: 长度
        """
        keywords = KEYWORDS.get_interpretable_keywords(InterpretableType.LENGTH)

        detected_tasks = []
        for task, keys in keywords.items():
            if any(key in query.lower() for key in keys):
                detected_tasks.append(task)
        return detected_tasks if detected_tasks else ["medium"]
    
    
    def estimate_reasoning_level(self, query: str):
        """根据查询长度和关键词估算推理深度"""
        keywords = KEYWORDS.get_interpretable_keywords(InterpretableType.REASONING_LEVEL)

        detected_tasks = []
        for task, keys in keywords.items():
            if any(key in query.lower() for key in keys):
                detected_tasks.append(task)
        return detected_tasks if detected_tasks else ["moderate"]
        
    def get_tenant_preference(self, tenant_id: str):
        """
        检测查询文本的租户偏好
        :param tenant_id: 租户id
        :return: 租户偏好
        """
        return "cost"
    
    # -- 核心流程 -- 
    def encode(self, query_text: str, tenant_id: str):
        # 1. 生成可解释特征 结构为二维列表
        q_interpretable = self.get_interpretable_vector(query_text=query_text, tenant_id=tenant_id)

        with torch.no_grad(): 
            text_embedding_tensor = self.llm_client.get_offline_embedding(query_text)

        device = next(self.projection_layer.parameters()).device # 获取投影层所在的设备
        q_interpretable = q_interpretable.to(device)
        
        text_embedding_tensor = text_embedding_tensor.to(device)

        # 4. 应用投影层 (生成潜在向量)
        z_Q = self.projection_layer(text_embedding_tensor)
        
        # 5. 拼接成最终的Q向量
        Q_vector = torch.cat([q_interpretable, z_Q])

        return {
            "q_interpretable": q_interpretable,
            # "q_latent": q_latent,
            "z_Q": z_Q,
            "Q_vector": Q_vector
        }
    
    def get_interpretable_vector(self, query_text: str, tenant_id: str):
        interpretable_features_list = [
            self.detect_task_type(query_text),
            self.detect_domain(query_text),
            self.estimate_reasoning_level(query_text),
            self.detect_safety(query_text),
            self.detect_length(query_text),
            self.get_tenant_preference(tenant_id),
        ]
        
        # 2. 使用对应的 MultiLabelBinarizer 进行 one-hot编码
        task_vec = self.task_mlb.transform([interpretable_features_list[0]])[0]
        domain_vec = self.domain_mlb.transform([interpretable_features_list[1]])[0]
        reasoning_vec = self.reasoning_mlb.transform([interpretable_features_list[2]])[0]
        safety_vec = self.safety_mlb.transform([interpretable_features_list[3]])[0]
        length_vec = self.length_mlb.transform([interpretable_features_list[4]])[0]
        tenant_pref_vec = self.tenant_pref_mlb.transform([interpretable_features_list[5]])[0]

        # 拼接所有可解释向量
        interpretable_vectors = [task_vec, domain_vec, reasoning_vec, safety_vec, length_vec, tenant_pref_vec]
        q_interpretable = torch.tensor(interpretable_vectors).flatten().float()

        return q_interpretable
