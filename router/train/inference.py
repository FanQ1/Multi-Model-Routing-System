import torch
import os
import sys

# ================= 1. 路径配置与导入 =================
# 获取项目根目录，确保能导入你的自定义模块
current_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))
sys.path.insert(0, project_root)

# 导入你的模型类和注册表
# 注意：运行前请确保 router 包在 PYTHONPATH 或者当前目录下
from router.encoder.Q_encoder import QSpaceEncode
from router.encoder.M_encoder import MSpaceEncode
from router.models.model_registry import MODEL_REGISTRY

# ================= 2. 全局配置 =================
CHECKPOINT_PATH = "router/utils/checkpoints/router_model.pth" # 训练生成的权重文件路径
LATENT_DIM = 128
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ================= 3. 模型加载函数 =================
def load_router():
    print(f"正在使用设备: {DEVICE}")
    print(f"正在初始化模型结构 (Latent Dim: {LATENT_DIM})...")

    # 1. 实例化模型结构 (这会初始化随机参数)
    q_encoder = QSpaceEncode(latent_dim=LATENT_DIM).to(DEVICE)
    m_encoder = MSpaceEncode(latent_dim=LATENT_DIM).to(DEVICE)

    # 2. 检查权重文件是否存在
    if not os.path.exists(CHECKPOINT_PATH):
        raise FileNotFoundError(f"找不到权重文件: {CHECKPOINT_PATH}，请先运行训练脚本。")

    print(f"正在加载权重: {CHECKPOINT_PATH}")
    checkpoint = torch.load(CHECKPOINT_PATH, map_location=DEVICE)

    # 3. 加载权重到模型中 (只加载投影层，这是关键！)
    q_encoder.projection_layer.load_state_dict(checkpoint['q_state_dict'])
    m_encoder.projection_layer.load_state_dict(checkpoint['m_state_dict'])

    # 4. 设置为评估模式
    # 这会关闭 Dropout 等训练时特有的层，确保推理结果稳定
    q_encoder.eval()
    m_encoder.eval()
    
    print("✅ 模型加载完成，准备推理！\n")
    return q_encoder, m_encoder

# ================= 4. 核心推理函数 =================
def route_query(query_text: str, tenant_id: str, q_encoder, m_encoder, top_k=3):
    """
    根据用户查询，路由到最合适的 Top-K 模型
    """
    with torch.no_grad(): # 推理不需要梯度，节省显存
        # --- A. 编码 Query ---
        # 注意：q_encoder.encode 内部会自动处理文本 -> embedding -> projection
        # 它会返回一个字典，包含 "z_Q" (潜向量) 和 "q_interpretable" (可解释特征)
        q_outputs = q_encoder.encode(query_text, tenant_id)
        
        # ⚠️ 关键点：只使用 Latent Vector (z_Q) 进行点积匹配
        # 不要使用 Q_vector (拼接向量)，因为 M 空间只有 Latent 维度
        z_Q = q_outputs["z_Q"] 

        # --- B. 遍历注册表中的所有模型进行匹配 ---
        model_scores = []
        
        for model_id, meta in MODEL_REGISTRY.items():
            # 1. 准备 M 的输入数据
            # 假设 meta 结构是: {"probe_scores": [...], "meta_scalars": [...]}
            m_input_features = meta["probe_scores"] + meta["meta_scalars"]
            
            # 转换为 Tensor 并移动到设备
            m_input_tensor = torch.tensor(m_input_features, dtype=torch.float32).to(DEVICE)
            
            # 2. 编码 Model 能力 -> z_M
            z_M = m_encoder.projection_layer(m_input_tensor)
            
            # 3. 计算匹配度 (点积)
            # 点积越大，代表 Query 需求 和 Model 能力 方向越一致
            score = torch.dot(z_Q, z_M).item()
            
            model_scores.append((model_id, score))

        # --- C. 排序并返回 Top-K ---
        # 按分数降序排列
        model_scores.sort(key=lambda x: x[1], reverse=True)
        
        return model_scores[:top_k]

# ================= 5. 主程序入口 =================
if __name__ == "__main__":
    # 1. 加载模型
    try:
        q_enc, m_enc = load_router()
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        sys.exit(1)

    # 2. 模拟用户输入 (你可以替换成真实的测试用例)
    test_queries = [
        {"tenant": "tenant_A", "text": "如何在 Python 中实现快速排序算法？"},
        {"tenant": "tenant_B", "text": "帮我写一首关于秋天的诗"},
        {"tenant": "tenant_A", "text": "解释一下量子力学的基本原理"},
        {"tenant": "tenant_C", "text": "帮我分析这段日志报错的原因"}
    ]

    # 3. 执行推理
    print("=" * 50)
    print("开始批量推理测试...")
    print("=" * 50)

    for item in test_queries:
        text = item["text"]
        tenant = item["tenant"]
        
        print(f"\n🟢 用户: {text}")
        print(f"   租户: {tenant}")
        
        # 调用路由函数
        top_results = route_query(text, tenant, q_enc, m_enc, top_k=3)
        
        print(top_results)
            
    print("\n" + "=" * 50)
    print("推理测试结束")
