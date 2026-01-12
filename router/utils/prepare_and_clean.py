import json
import os
from datasets import load_dataset
from tqdm import tqdm

# 配置
OUTPUT_FILE = "data/raw_tiger_1k.json"
TARGET_COUNT = 1000  # 想要多少条

def main():
    print("正在从 HuggingFace 下载 TIGER-Lab/ucl-trustful-qa...")
    print("这是一个干净的小数据集，不需要复杂的清洗。")
    
    try:
        # 这个数据集在 HuggingFace 上是公开的，不需要登录
        dataset = load_dataset("C-MTEB/C-STM", split="test")
        print(f"下载成功！共 {len(dataset)} 条数据。")
    except Exception as e:
        print(f"下载失败: {e}")
        print("请确保已安装 datasets 库: pip install datasets")
        return

    processed_data = []
    count = 0

    # 只保留我们关心的模型
    valid_keywords = ["glm", "deepseek", "qwen"]

    print("正在处理数据...")
    for item in tqdm(dataset):
        if count >= TARGET_COUNT:
            break
            
        prompt = item.get('prompt', item.get('question'))
        responses = item.get('responses', [])
        ranking = item.get('rank', [])
        
        if not prompt or not responses or len(responses) < 2:
            continue
            
        # 找到排名第一和第二的模型
        # ranking 通常是对应 responses 的索引，比如 [1, 0] 表示 responses[1] 是第一名
        try:
            best_idx = ranking[0]
            second_idx = ranking[1]
        except:
            continue
            
        winner_data = responses[best_idx]
        loser_data = responses[second_idx]
        
        winner_model = winner_data.get('model', winner_data.get('model_name', 'unknown'))
        loser_model = loser_data.get('model', loser_data.get('model_name', 'unknown'))
        
        # 简单的模型过滤 (只保留我们注册表里的模型)
        # 注意：这个数据集里模型名可能不一样，比如是 'deepseek-chat'，匹配 'deepseek' 即可
        if not any(kw in winner_model.lower() or kw in loser_model.lower() for kw in valid_keywords):
            continue
            
        processed_data.append({
            "prompt": prompt,
            "winner": winner_model,
            "loser": loser_model
        })
        count += 1

    # 保存
    os.makedirs("data", exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)
        
    print(f"\n处理完成！共保存 {len(processed_data)} 条数据到 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
