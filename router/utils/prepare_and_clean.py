import json
import os
import pickle
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# 1. 配置
INPUT_FILE = "data/mock_data.json"
OUTPUT_FILE = "data/router_embeddings.pkl"

# 2. 加载离线模型
# 这一行会自动从 HuggingFace 下载模型到本地 (只需要下载一次)
# 如果你也连不上 HuggingFace，它可能会报错。但通常 sentence-transformers 的下载比较稳定。
print("正在加载离线 Embedding 模型 (BAAI/bge-small-en-v1.5)...")
model = SentenceTransformer('BAAI/bge-small-en-v1.5')
print("模型加载成功！")

def main():
    print(f"正在读取数据: {INPUT_FILE}")
    
    if not os.path.exists(INPUT_FILE):
        print(f"错误：找不到文件 {INPUT_FILE}")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"读取成功！共 {len(data)} 条对局数据。")
    
    # 如果是中文数据，建议换成中文模型：
    # model = SentenceTransformer('shibing624/text2vec-base-chinese')
    
    embeddings = []
    labels = []
    model_pairs = []
    
    # 批量处理可以稍微快点，但 100 条一条条跑也很快
    for item in tqdm(data, desc="生成向量"):
        prompt = item['prompt']
        winner = item['winner']
        loser = item['loser']
        
        # 1. 离线生成向量
        vec = model.encode(prompt, normalize_embeddings=True)
        
        # 2. 确定标签 (按名字排序固定 A/B 顺序)
        models = sorted([winner, loser])
        model_a = models[0]
        model_b = models[1]
        
        if winner == model_a:
            label = 0 # A 赢
        else:
            label = 1 # B 赢
            
        embeddings.append(vec)
        labels.append(label)
        model_pairs.append((model_a, model_b, winner))

    # 3. 保存
    print(f"\n处理完成！共生成 {len(embeddings)} 条向量数据。")
    
    save_data = {
        "embeddings": embeddings,
        "labels": labels,
        "model_pairs": model_pairs
    }
    
    # os.makedirs("data", exist_ok=True)
    with open(OUTPUT_FILE, 'wb') as f:
        pickle.dump(save_data, f)
        print(f"向量数据已保存至: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
