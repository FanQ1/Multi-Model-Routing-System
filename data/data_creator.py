import pandas as pd
import random
import numpy as np

# 配置
MATH_PATH = "data/test_gsm8k.csv"
CODE_PATH = "data/test_humanev.csv"
OUTPUT_PATH = "data/training_data.csv"

# 模型列表（与矩阵列对应）
MODELS = ["gemini-2.5-pro", "qwen3-max", "deepseek-v3.2-exp"]

# 能力矩阵（6行×3列）
# 行顺序: math, code, creative_writing, expert, safety, long_query
ABILITY_MATRIX = [
    [0.458, 0.3125, 0.229],    # math
    [0.395, 0.368, 0.237],     # code
    [0.547, 0.375, 0.078],     # creative_writing
    [0.556, 0.238, 0.206],     # expert
    [0.403, 0.347, 0.250],     # safety
    [0.421, 0.368, 0.211]      # long_query
]

# 类别到矩阵行的映射
CATEGORY_TO_ROW = {
    "math": 0,
    "code": 1,
    "creative_writing": 2,
    "expert": 3,
    "safety": 4,
    "long_query": 5
}

def get_prompt_from_row(row, category):
    """
    根据类别从DataFrame行中提取prompt
    """
    if category == "math":
        # GSM8K
        if 'question' in row:
            return str(row['question'])
    elif category == "code":
        # mbpp
        if 'text' in row:
            return str(row['text'])
    
    return None

def select_random_model_pair():
    """
    随机选择两个不同的模型
    返回: (model_a, model_b, idx_a, idx_b)
    """
    indices = random.sample(range(len(MODELS)), 2)
    idx_a, idx_b = indices[0], indices[1]
    return MODELS[idx_a], MODELS[idx_b], idx_a, idx_b

def select_winner_by_probability(model_a_idx, model_b_idx, category):
    """
    根据矩阵中的分数概率随机选择winner
    
    参数:
        model_a_idx: 模型A在MODELS列表中的索引
        model_b_idx: 模型B在MODELS列表中的索引
        category: 任务类别
    
    返回:
        winner: 模型A或模型B的名称
    """
    if category not in CATEGORY_TO_ROW:
        # 如果类别未知，随机选择
        return random.choice([MODELS[model_a_idx], MODELS[model_b_idx]])
    
    # 获取该类别的分数行
    row_idx = CATEGORY_TO_ROW[category]
    scores = ABILITY_MATRIX[row_idx]
    
    # 获取两个模型的分数
    score_a = scores[model_a_idx]
    score_b = scores[model_b_idx]
    
    # 计算模型A获胜的概率
    total_score = score_a + score_b
    if total_score <= 0:
        # 如果分数都为0，随机选择
        prob_a_wins = 0.5
    else:
        prob_a_wins = score_a / total_score
    
    # 按概率随机选择winner
    if random.random() < prob_a_wins:
        return MODELS[model_a_idx]
    else:
        return MODELS[model_b_idx]

def generate_data_for_category(df, category, num_samples=None):
    """
    为指定类别生成训练数据
    
    参数:
        df: 包含原始数据的DataFrame
        category: 任务类别
        num_samples: 要生成的样本数量（None表示使用所有数据）
    
    返回:
        list: 生成的训练数据记录列表
    """
    if category not in CATEGORY_TO_ROW:
        print(f"警告: 未知类别 '{category}'，跳过")
        return []
    
    data_records = []
    
    # 确定要处理多少行数据
    if num_samples is not None and num_samples < len(df):
        # 随机抽样指定数量的行
        df_sample = df.sample(n=num_samples, random_state=42)
    else:
        df_sample = df
    
    print(f"为类别 '{category}' 处理 {len(df_sample)} 条数据...")
    
    # 遍历DataFrame的每一行
    for _, row in df_sample.iterrows():
        # 获取prompt
        prompt = get_prompt_from_row(row, category)
        if not prompt or prompt.strip() == "":
            continue  # 跳过空prompt
        
        # 随机选择两个模型
        model_a, model_b, idx_a, idx_b = select_random_model_pair()
        
        # 根据矩阵分数概率选择winner
        winner = select_winner_by_probability(idx_a, idx_b, category)
        
        # 创建数据记录
        record = {
            "prompt": prompt.strip(),
            "model_a": model_a,
            "model_b": model_b,
            "winner": winner,
            "category": category
        }
        
        data_records.append(record)
    
    print(f"  成功生成 {len(data_records)} 条训练数据")
    return data_records


def create_training_data():
    """
    主函数：创建完整的训练数据集
    该函数整合math和code的真实数据以及其他类别的合成数据，
    最终生成一个格式化的训练数据集并保存为CSV文件
    Returns:
        pd.DataFrame: 生成的训练数据集，如果生成失败则返回None
    """
    all_data = []
    
    # 1. 处理math数据
    try:
        math_df = pd.read_csv(MATH_PATH)
        math_data = generate_data_for_category(math_df, "math", num_samples=200)
        all_data.extend(math_data)
    except Exception as e:
        print(f"读取math数据失败: {e}")
    
    # 2. 处理code数据
    try:
        code_df = pd.read_csv(CODE_PATH)
        code_data = generate_data_for_category(code_df, "code", num_samples=200)
        all_data.extend(code_data)
    except Exception as e:
        print(f"读取code数据失败: {e}")
    
    # 3. 处理其他类别（使用合成数据）
    other_categories = ["creative_writing", "expert", "safety", "long_query"]
    
    for category in other_categories:
        print(f"\n处理 {category} 数据...")
    
    # 4. 转换为DataFrame
    if not all_data:
        print("错误: 没有生成任何数据！")
        return None
    
    result_df = pd.DataFrame(all_data)
    
    # 5. 随机打乱数据
    result_df = result_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # 6. 保存到CSV
    result_df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8')
    
    # 7. 打印统计信息
    print("\n" + "="*50)
    print("数据生成完成！")
    print(f"总数据量: {len(result_df)} 条")
    print(f"保存到: {OUTPUT_PATH}")
    print("\n类别分布:")
    print(result_df['category'].value_counts())
    
    print("\n模型对出现次数统计:")
    result_df['model_pair'] = result_df.apply(
        lambda x: tuple(sorted([x['model_a'], x['model_b']])), axis=1
    )
    print(result_df['model_pair'].value_counts().head(10))
    
    print("\nWinner分布:")
    winner_counts = result_df['winner'].value_counts()
    for model in MODELS:
        count = winner_counts.get(model, 0)
        percentage = count / len(result_df) * 100
        print(f"  {model}: {count} 次 ({percentage:.1f}%)")
    
    print("\n数据示例:")
    print(result_df.head(10))
    
    # 8. 验证概率计算的正确性
    print("\n概率计算验证（按类别）:")
    for category in CATEGORY_TO_ROW.keys():
        cat_data = result_df[result_df['category'] == category]
        if len(cat_data) > 0:
            row_idx = CATEGORY_TO_ROW[category]
            scores = ABILITY_MATRIX[row_idx]
            
            print(f"\n{category}类别:")
            print(f"  矩阵分数: {scores}")
            
            # 计算每个模型作为winner的比例
            for i, model in enumerate(MODELS):
                model_wins = len(cat_data[cat_data['winner'] == model])
                total_involving_model = len(cat_data[
                    (cat_data['model_a'] == model) | (cat_data['model_b'] == model)
                ])
                
                if total_involving_model > 0:
                    win_rate = model_wins / total_involving_model * 100
                    print(f"  {model}: 胜率 {win_rate:.1f}% (矩阵分数: {scores[i]})")
    
    return result_df

if __name__ == "__main__":
    print("开始生成训练数据...")
    print("="*50)
    
    # 生成完整训练数据
    training_data = create_training_data()

    print("\n" + "="*50)
    print("数据生成流程完成！")