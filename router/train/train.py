import torch
import torch.nn as nn
import torch.optim as optim
import os
import sys

from router.encoder.Q_encoder import QSpaceEncode
from router.encoder.M_encoder import MSpaceEncode
from router.models.model_registry import MODEL_REGISTRY

# 添加项目根目录到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

LATENT_DIM = 128        # Z 空间维度 
LEARNING_RATE = 1e-3    
EPOCHS = 100            
MARGIN = 0.5            
BATCH_SIZE = 4          


DATA_PATH = "data/train_cache.pt"

def get_train_data():
    if os.path.exists(DATA_PATH):
        print(f"加载数据缓存: {DATA_PATH}")
        return torch.load(DATA_PATH)
    else:
        print("警告: 未找到 data/train_cache.pt，生成模拟数据用于演示...")
        os.makedirs("data", exist_ok=True)
        
        # 模拟 3 条数据
        # 注意：这里我们只存 winner/loser 的名字，在训练循环里再去查 MODEL_REGISTRY
        mock_data = [
            {
                "query": "如何用 Python 实现快速排序算法？",
                "winner": "deepseek-coder-v2", # 代码题 DeepSeek 强
                "loser": "glm-4"
            },
            {
                "query": "请解释一下量子纠缠的基本原理。",
                "winner": "glm-4", # 通用理论题 GLM4 稳
                "loser": "deepseek-coder-v2"
            },
            {
                "query": "帮我写一个微积分的证明题。",
                "winner": "qwen2.5-72b", # 数学题 Qwen 强
                "loser": "deepseek-coder-v2"
            }
        ]
        
        # 我们需要把 query 文本转成 embedding 才能喂给模型
        # 这里为了演示，我们只存 query 文本，在 train 里面实时转 (慢一点但能跑)
        # 实际上 prepare_data.py 应该预处理好 embedding 存下来
        return mock_data

print("正在初始化模型...")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"使用设备: {device}")

# 初始化 Q 空间编码器
q_encoder = QSpaceEncode(latent_dim=LATENT_DIM)
q_encoder.projection_layer.to(device)

# 初始化 M 空间编码器
m_encoder = MSpaceEncode(latent_dim=LATENT_DIM)
m_encoder.projection_layer.to(device)

optimizer = optim.AdamW(
    list(q_encoder.projection_layer.parameters()) + 
    list(m_encoder.projection_layer.parameters()), 
    lr=LEARNING_RATE
)

train_data = get_train_data()

print(f"\n开始训练，共 {EPOCHS} 轮...")
for epoch in range(EPOCHS):
    total_loss = 0
    
    # 简单遍历数据 (为了演示不使用 DataLoader，实际大数据量建议用 DataLoader)
    for item in train_data:
        optimizer.zero_grad()
        
        # --- A. 获取数据 ---
        # 这里兼容两种数据格式：
        # 1. 模拟数据格式: {"query": str, "winner": str, "loser": str}
        # 2. 真实缓存格式: {"query_embedding": tensor, "winner": str, "loser": str}
        
        query_text = item.get("query")
        query_embedding = item.get("query_embedding")
        winner_id = item["winner"]
        loser_id = item["loser"]
        
        # 获取 Q 向量
        if query_embedding is not None:
            # 如果已经有缓存好的 Embedding，直接拿来用
            text_emb_tensor = query_embedding.to(device)
            # 需要手动跑一遍 projection_layer 得到 z_Q
            # 注意：q_interpretable 部分这里简化处理，假设为0或全1，因为缓存里可能没存
            # 实际训练时，prepare_data.py 应该把 q_interpretable 也存下来
            q_interpretable_dummy = torch.zeros(50).to(device) # 假设可解释部分是50维
            z_Q = q_encoder.projection_layer(text_emb_tensor)
        else:
            # 如果是文本，实时编码
            result = q_encoder.encode(query_text, tenant_id="tenant_A")
            z_Q = result["z_Q"]
        
        # --- B. 获取 M 向量 ---
        # 从 MODEL_REGISTRY 获取 winner 和 loser 的元数据
        w_data = MODEL_REGISTRY.get(winner_id)
        l_data = MODEL_REGISTRY.get(loser_id)
        
        if not w_data or not l_data:
            print(f"警告: 模型 {winner_id} 或 {loser_id} 不在注册表中，跳过")
            continue
            
        # Winner M 向量
        w_input_features = w_data["probe_scores"] + w_data["meta_scalars"]
        w_input_tensor = torch.tensor(w_input_features, dtype=torch.float32).to(device)
        z_M_winner = m_encoder.projection_layer(w_input_tensor)
        
        # Loser M 向量
        l_input_features = l_data["probe_scores"] + l_data["meta_scalars"]
        l_input_tensor = torch.tensor(l_input_features, dtype=torch.float32).to(device)
        z_M_loser = m_encoder.projection_layer(l_input_tensor)
        
        # --- C. 计算相似度 (点积) ---
        sim_winner = torch.dot(z_Q, z_M_winner)
        sim_loser = torch.dot(z_Q, z_M_loser)
        
        # --- D. 计算 Triplet Loss ---
        # 目标: sim_winner - sim_loser > margin
        # Loss = max(0, sim_loser - sim_winner + margin)
        loss = torch.relu(sim_loser - sim_winner + MARGIN)
        
        total_loss += loss.item()
        
        # --- E. 反向传播与更新 ---
        loss.backward()
        optimizer.step()
        
    # 打印本轮平均 Loss
    avg_loss = total_loss / len(train_data)
    if (epoch + 1) % 10 == 0:
        print(f"Epoch [{epoch+1}/{EPOCHS}], Loss: {avg_loss:.4f}")

        # --- F. 简单验证 ---
        print("--- 验证 ---")
        with torch.no_grad():
            # 测试第一个样本
            test_item = train_data[0]
            if "query" in test_item:
                res = q_encoder.encode(test_item["query"], "tenant_A")
                z_test = res["z_Q"]
            else:
                z_test = z_Q # 用循环里最后一次的值
            
            scores = {}
            for mid, mdata in MODEL_REGISTRY.items():
                inp = torch.tensor(mdata["probe_scores"] + mdata["meta_scalars"], dtype=torch.float32).to(device)
                z_m = m_encoder.projection_layer(inp)
                scores[mid] = torch.dot(z_test, z_m).item()
            
            # 排序
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            print(f"Query: {test_item.get('query', '...')[:20]}...")
            print("模型匹配度排序:")
            for mid, score in sorted_scores:
                print(f"  {mid}: {score:.4f}")
        print("------------")

# --- 6. 保存模型 ---
print("\n训练完成！")
save_dir = "checkpoints"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

torch.save({
    'epoch': EPOCHS,
    'q_projection_state_dict': q_encoder.projection_layer.state_dict(),
    'm_projection_state_dict': m_encoder.projection_layer.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
}, f"{save_dir}/router_model.pth")

print(f"模型已保存至 {save_dir}/router_model.pth")
