import torch
import torch.nn as nn
import re
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import MultiLabelBinarizer
# -- 自定义库
from utils.config import TASK_TYPES, DOMAINS, REASONING_LEVELS, SAFETY_LEVELS, LENGTH_BUCKETS, TENANT_PREFERENCES
from utils.config import InterpretableType
import utils.interpretable_keywords as KEYWORDS  

"""

"""

class QSpaceEncode:
    """
    将查询文本和id转换为混合向量
    混合向量包括 可解释性向量 和 隐向量
    """
    def __init__(self, embedding_model_name='all-MiniLM-L6-v2', latent_dim=128):
        # q_spcae需要embedding模型处理隐藏特征
        self.embedding_model = SentenceTransformer(embedding_model_name)
        print("Embdedding model loaded")

        # --- 正确初始化所有 MultiLabelBinarizer ---
        # fit all tags in config.py
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

        # 添加投影层
        embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        self.projection_layer = nn.Linear(embedding_dim, latent_dim) # 需要训练的神经网络

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
        return detected_tasks if detected_tasks else ["chat"] # 默认为聊天
    
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
        # TODO: 检测安全性
        return "safety"
    
    def detect_length(self, query: str):
        """
        检测查询文本的长度
        :param query: 查询文本
        :return: 长度
        """
        # TODO: 检测长度
        return "length"
    
    def estimate_reasoning_level(self, query_text: str):
        """根据查询长度和关键词估算推理深度"""
        if "step by step" in query_text.lower() or "explain" in query_text.lower() or len(query_text) > 200:
            return ["high"]
        elif "why" in query_text.lower() or "how" in query_text.lower():
            return ["medium"]
        else:
            return ["low"]
        
    def get_tenant_preference(self, tenant_id: str):
        """
        检测查询文本的租户偏好
        :param tenant_id: 租户id
        :return: 租户偏好
        """

        # 通过id查询数据库 得到用户的约束

        # TODO: 检测租户偏好
        return "tenant_preference"
    
    # -- 核心流程 -- 
    def encode(self, query_text: str, tenant_id: str):
        # 1. 生成可解释特征 结构为二维列表
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

        # 3. 调用嵌入服务
        text_embedding_tensor = self.embedding_model.encode(query_text, convert_to_tensor=True)

        # 4. 应用投影层 (生成潜在向量)
        q_latent = self.projection_layer(text_embedding_tensor)
        
        # 5. 拼接成最终的Q向量
        Q_vector = torch.cat([q_interpretable, q_latent])
        
        # z_Q 是用于Z空间匹配的潜在部分
        z_Q = q_latent

        return {
            "q_interpretable": q_interpretable,
            "q_latent": q_latent,
            "z_Q": z_Q,
            "Q_vector": Q_vector
        }

