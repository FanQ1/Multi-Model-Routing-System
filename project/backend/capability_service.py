
"""
能力矩阵服务
用于处理模型排名到能力矩阵的转换
"""

from typing import List, Dict
from venv import logger
import numpy as np
from schema import ApiResponse
from database import SessionLocal, Model
from models import ModelInfo

class CapabilityService:
    """能力矩阵服务类"""

    def __init__(self):
        self.model_rank_matrix = [] # 排名矩阵
        self.model_list = [] #模型名称列表
        self.model_ability_matrix = None # 能力矩阵

    def _initialize_from_db(self):
        """从数据库中初始化模型矩阵"""
        db = SessionLocal()

        try:
            models = db.query(Model).all()
            print(len(models))
            # 1. 初始化模型列表和能力矩阵
            for idx, model in enumerate(models):
                self.model_list.append(model.name)
                single_model_rank = model.capability_ranks # 这是list
                self.model_rank_matrix.append(single_model_rank)
            
            # 2. 计算能力矩阵
            if len(self.model_list) > 0:
                self.model_ability_matrix = self.calculate_capability_matrix()

            # 3. 对于第一次初始化，提前插入三个模型
            if len(self.model_list) == 0:
                # 初始化三个模型
                self.update_model_matrix("gemini-2.5-pro", [11, 30, 11, 15, 29])
                self.update_model_matrix("qwen3-max", [15, 18, 23, 13, 4])
                self.update_model_matrix("deepseek-3.2-exp", [22, 28, 21, 35, 8])

                print("Initialized model rank matrix with default models.")

        except Exception as e:
            print(f"Error initializing model rank matrix: {e}")
            raise e

    def update_model_matrix(self, model_name: str, ranks: List):
        """
        更新模型的能力矩阵

        Args:
            model_id: 模型ID
            ranks: 能力列表
        """
        db = SessionLocal()
        try:
            print(self.model_list)
            if model_name in self.model_list:
                # 找到model在list的索引
                index = self.model_list.index(model_name)
                # 更新model的ranks
                self.model_rank_matrix[index] = ranks
            else:
                # 添加新的model
                self.model_list.append(model_name)
                self.model_rank_matrix.append(ranks)
                            
            self.model_ability_matrix = self.calculate_capability_matrix()

            print(self.model_list, self.model_rank_matrix)
            # 同步更新数据库中的模型信息
            existing_model = db.query(Model).filter(Model.name == model_name).first()

            if existing_model:
                existing_model.capability_ranks = ranks
                existing_model.capability_vector = self.get_model_ability_vector(model_name)
            else:
                import uuid
                model_id = f"model_{uuid.uuid4().hex}"
                db.add(Model(
                    id=model_id,
                    name=model_name,
                    capability_ranks=ranks,
                    capability_vector=self.get_model_ability_vector(model_name)
                ))
                print(f"Added new model {model_name} to database.")
            db.commit()

        except Exception as e:
            db.rollback()
            raise e
    
    def delete_model_from_matrix(self, model_name: str):
        """
        从能力矩阵中删除一个模型

        Args:
            model_name: 模型名称
        """
        try:
            db = SessionLocal()
            # 同步删除数据库中的模型信息
            existing_model = db.query(Model).filter(Model.name == model_name).first()

            if existing_model:
                db.delete(existing_model)
                db.commit()
                print(f"Deleted model {model_name} from database.")
                # delete from matrix
                index = self.model_list.index(model_name)
                self.model_list.pop(index)
                self.model_rank_matrix.pop(index)
                # calculate ability matrix again
                self.model_ability_matrix = self.calculate_capability_matrix()
            else:
                print(f"Model {model_name} not found in database.")
        except Exception as e:
            db.rollback()
            raise e
        
    def get_model_rank_vector(self, model_name: str):
        """
        获取一个模型的排名向量
        """
        if model_name in self.model_list:
            index = self.model_list.index(model_name)
            print('imhere')
            return self.model_rank_matrix[index].tolist()
        
        return None
    def get_model_ability_vector(self, model_name: str):
        """
        获取一个模型的能力向量
        """
        if model_name in self.model_list:
            index = self.model_list.index(model_name)
            return self.model_ability_matrix[index].tolist()
        
        return None
        
    def get_model_rank_matrix(self):
        """
        获取模型的排名矩阵
        """
        return self.model_rank_matrix
    
    def get_model_ability_matrix(self):
        """
        获取模型的能力矩阵
        """
        return self.model_ability_matrix
    
    def get_model_list(self):
        """
        获取模型列表
        """
        return self.model_list
    
    def calculate_capability_matrix(self):
        scale_to=0.6
        def calculate_scores(ranks):
            """对单个维度的排名计算能力分"""
            # 先将排名转换为"相对强度"
            # 核心：排名每差1位，能力值差距应该是多少？
            # 我们设基准：排名每差1位，胜率增加约5-8个百分点
            
            # 找到最佳排名（最小值）
            best_rank = min(ranks)
            
            # 计算每个排名与最佳排名的差值
            rank_diffs = [r - best_rank for r in ranks]
            
            # 根据差值设定能力衰减
            scores = []
            for diff in rank_diffs:
                if diff == 0:  # 最佳排名
                    score = 1.0
                elif diff <= 3:  # 差1-3位：激烈竞争区
                    # 每差1位，能力衰减10%
                    score = 1.0 / (1.0 + 0.10 * diff)
                elif diff <= 8:  # 差4-8位：优势区
                    # 基准衰减已到0.77，再每差1位衰减15%
                    base = 1.0 / (1.0 + 0.10 * 3)  # ≈0.77
                    extra_diff = diff - 3
                    score = base / (1.0 + 0.15 * extra_diff)
                elif diff <= 15:  # 差9-15位：大优势区
                    # 基准衰减已到0.48，再每差1位衰减20%
                    base = 1.0 / (1.0 + 0.10 * 3) / (1.0 + 0.15 * 5)  # ≈0.48
                    extra_diff = diff - 8
                    score = base / (1.0 + 0.20 * extra_diff)
                else:  # 差＞15位：绝对优势区
                    # 急剧衰减
                    base = 1.0 / (1.0 + 0.10 * 3) / (1.0 + 0.15 * 5) / (1.0 + 0.20 * 7)  # ≈0.19
                    extra_diff = diff - 15
                    score = base / (1.0 + 0.30 * extra_diff)
                scores.append(score)
            
            return scores
        
        ability_matrix = []
        
        for ranks in self.model_rank_matrix:
            # 计算原始分数
            raw_scores = calculate_scores(ranks)
            
            # 缩放到目标范围
            max_score = max(raw_scores)
            scaled_scores = [(s / max_score) * scale_to for s in raw_scores]
            
            ability_matrix.append(scaled_scores)
        
        return np.array(ability_matrix)
# 全局能力服务实例
capability_service = CapabilityService()
