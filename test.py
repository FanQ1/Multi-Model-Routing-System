import openai

client = openai.OpenAI(
  base_url="https://gateway.api.sightai.io/",
  api_key="sk-ecb0fc3a435dbd09432334c6ff5ceeea"
)

try:
    # 尝试获取模型列表
    models = client.models.list()
    print("✅ 成功获取模型列表：")
    for model in models.data:
        print(f"  - {model.id}")
except Exception as e:
    print(f"❌ 错误：{e}")
