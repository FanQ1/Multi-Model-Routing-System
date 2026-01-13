import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
import pickle
current_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))
sys.path.insert(0, project_root)
from router.encoder.Q_encoder import QSpaceEncode
from router.encoder.M_encoder import MSpaceEncode
from router.models.model_registry import MODEL_REGISTRY

# --- 1. 配置 ---
LATENT_DIM = 128
LEARNING_RATE = 1e-3
EPOCHS = 50
MARGIN = 0.5
BATCH_SIZE = 32  # 建议使用 DataLoader，这里为了简单用伪 batch
DATA_PATH = "router/utils/data/router_embeddings.pkl" # 确保路径正确

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"使用设备: {device}")
import torch
print(torch.__version__)
print(torch.cuda.is_available())

# --- 2. 初始化模型 ---
# 注意：QSpaceEncode 内部必须有 self.interpretable_dim 属性
q_encoder = QSpaceEncode(latent_dim=LATENT_DIM).to(device)
m_encoder = MSpaceEncode(latent_dim=LATENT_DIM).to(device)

# --- 3. 优化器 ---
optimizer = optim.AdamW(
    list(q_encoder.projection_layer.parameters()) + 
    list(m_encoder.projection_layer.parameters()), 
    lr=LEARNING_RATE
)

# --- 4. 加载数据 ---
# 假设 data 结构如 prepare_data.py 输出: 
# { "embeddings": list, "labels": list, "model_pairs": list }
try:
    with open(DATA_PATH, 'rb') as f:
        raw_data = pickle.load(f) # 或 pickle.load(f)，取决于你保存的方式
    
    # 转换为 Tensor
    # raw_data['embeddings'] 应该是 List[List[float]] 或 Numpy Array
    all_embeddings = torch.tensor(raw_data['embeddings'], dtype=torch.float32).to(device)
    all_labels = raw_data['labels']
    all_model_pairs = raw_data['model_pairs']
    print(f"数据加载成功，样本数: {len(all_embeddings)}")

except Exception as e:
    print(f"数据加载失败: {e}")
    sys.exit(1)

# --- 5. 训练循环 ---
print(f"\n开始训练，共 {EPOCHS} 轮...")

# 获取 Q 编码器的可解释特征维度，用于构造 dummy vector
# 假设 QSpaceEncode 中计算了 self.interpretable_dim
interp_dim = q_encoder.interpretable_dim if hasattr(q_encoder, 'interpretable_dim') else 50
if hasattr(q_encoder, 'interpretable_dim'):
    print(f"检测到可解释特征维度: {interp_dim}")
else:
    print("警告: QSpaceEncode 未提供 interpretable_dim，使用默认值 50 (可能导致维度错误)")

for epoch in range(EPOCHS):
    total_loss = 0
    num_processed = 0
    
    # 简单打乱索引
    indices = torch.randperm(len(all_embeddings))
    
    # 为了演示，这里手动实现简单的 batch 处理
    for i in range(0, len(indices), BATCH_SIZE):
        batch_indices = indices[i:i+BATCH_SIZE]
        
        # --- A. 准备 Batch 数据 ---
        batch_embs = all_embeddings[batch_indices] # [B, 384]
        
        # 提取该 batch 对应的 labels 和 pairs
        batch_labels = [all_labels[idx] for idx in batch_indices]
        batch_pairs = [all_model_pairs[idx] for idx in batch_indices]
        
        batch_loss = 0.0
        valid_samples = 0
        
        # --- B. 遍历 Batch 中的每个样本 ---
        # 注意：由于每个样本对应的 Winner/Loser 模型不同，很难完全向量化，
        # 除非所有样本都在同一对模型之间比较。这里采用循环处理 Loss。
        
        optimizer.zero_grad() 
        
        for j in range(len(batch_indices)):
            emb = batch_embs[j] # [384]
            label = batch_labels[j]
            pair = batch_pairs[j] # (model_a, model_b, winner_name)
            
            model_a, model_b, winner_name = pair
            
            # 确定 Winner 和 Loser ID
            if label == 0:
                winner_id, loser_id = model_a, model_b
            else:
                winner_id, loser_id = model_b, model_a
            
            # 检查模型是否在注册表中
            if winner_id not in MODEL_REGISTRY or loser_id not in MODEL_REGISTRY:
                continue
            
            # --- C. 计算 Q 向量 ---
            # 场景：使用离线 embedding，缺少文本
            # z_Q 只依赖 projection_layer，不依赖 q_interpretable
            z_Q = q_encoder.projection_layer(emb)
            
            # --- D. 计算 M 向量 ---
            w_meta = MODEL_REGISTRY[winner_id]
            l_meta = MODEL_REGISTRY[loser_id]
            
            # 拼接特征: probe_scores (5) + meta_scalars (3) = 8
            w_input = torch.tensor(w_meta["probe_scores"] + w_meta["meta_scalars"], dtype=torch.float32).to(device)
            l_input = torch.tensor(l_meta["probe_scores"] + l_meta["meta_scalars"], dtype=torch.float32).to(device)
            
            z_M_w = m_encoder.projection_layer(w_input)
            z_M_l = m_encoder.projection_layer(l_input)
            
            # --- E. 计算 Loss ---
            sim_w = torch.dot(z_Q, z_M_w)
            sim_l = torch.dot(z_Q, z_M_l)
            
            loss = torch.relu(sim_l - sim_w + MARGIN)
            batch_loss += loss
            valid_samples += 1
            
        # --- F. 反向传播 ---
        if valid_samples > 0:
            # 对 Batch 的 Loss 取平均，保持梯度稳定
            avg_batch_loss = batch_loss / valid_samples
            avg_batch_loss.backward()
            optimizer.step()
            
            total_loss += avg_batch_loss.item()
            num_processed += 1
            
    # 打印 Epoch 统计
    if num_processed > 0:
        print(f"Epoch [{epoch+1}/{EPOCHS}], Loss: {total_loss / num_processed:.4f}")
    else:
        print(f"Epoch [{epoch+1}/{EPOCHS}], No valid data processed.")

    # --- G. 验证 ---
    if (epoch + 1) % 10 == 0:
        print("--- 验证 ---")
        q_encoder.eval()
        m_encoder.eval()
        with torch.no_grad():
            # 取第一个样本测试
            test_emb = all_embeddings[0].unsqueeze(0) # [1, 384]
            z_test = q_encoder.projection_layer(test_emb) # [1, 128]
            
            scores = {}
            for mid, mdata in MODEL_REGISTRY.items():
                inp = torch.tensor(mdata["probe_scores"] + mdata["meta_scalars"], dtype=torch.float32).to(device)
                z_m = m_encoder.projection_layer(inp)
                scores[mid] = torch.dot(z_test[0], z_m).item() # dot product
            
            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            print("当前 Top 模型匹配度:")
            for mid, score in sorted_scores[:3]:
                print(f"  {mid}: {score:.4f}")
        
        q_encoder.train()
        m_encoder.train()
        print("------------")

# --- 6. 保存模型 ---
print("\n训练完成！")
save_dir = "checkpoints"
os.makedirs(save_dir, exist_ok=True)

torch.save({
    'epoch': EPOCHS,
    'q_state_dict': q_encoder.projection_layer.state_dict(),
    'm_state_dict': m_encoder.projection_layer.state_dict(),
    'optimizer': optimizer.state_dict(),
}, f"{save_dir}/router_model.pth")

print(f"模型已保存至 {save_dir}/router_model.pth")
