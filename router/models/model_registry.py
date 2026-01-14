MODEL_REGISTRY = {
    "glm-4": {
        "probe_scores": [0.88, 0.85, 0.90, 0.98, 0.89], 
        "meta_scalars": [0.8, 0.5, 1.0] 
    },
    
    "qwen2.5-7b-instruct": {
        "probe_scores": [0.95, 0.90, 0.92, 0.95, 0.92], 
        "meta_scalars": [0.6, 0.8, 1.0] 
    },
    
    "deepseek-coder": {
        "probe_scores": [0.80, 0.99, 0.85, 0.92, 0.70], 
        "meta_scalars": [0.1, 0.9, 1.0] 
    }
}

""""
https://lmarena.ai/zh/leaderboard
  probe: math code writing expert safety
  safety from: https://arxiv.org/pdf/2511.02366v2
  interpretable ：cost latency long_query 

  math: gemini-2.5-pro qwen3-max deepseek-v3.2-exp 11 15 22 (0.458 0.3125 0.229)
  code: qwen3-max deepseek-v3.2-exp gemini-2.5-pro 18 28 30 ()
  creative_writing: gemini-2.5-pro deepseek-v3.2-exp qwen3-max 5 24 35()
  expert: qwen3-max gemini-2.5-pro deepseek-v3.2-exp 13 15 35 ()
  safety: qwen3-max deepseek-v3.2-exp gemini-2.5-pro 79.38 68.47 48.93 ()
  long_query: gemini-2.5-pro qwen3-max deepseek-v3.2-exp 12 21 24 ()
 
  cost: deepseek-v3.2-exp qwen3-max gemini-2.5-pro
  latency: qwen3-max deepseek-v3.2-exp gemini-2.5-pro

  [
    [0.458, 0.3125, 0.229],
    [0.395, 0.368, 0.237], 
    [0.547, 0.375, 0.078], 
    [0.556, 0.238, 0.206], 
    [0.403, 0.347, 0.250], 
    [0.421, 0.368, 0.211]
  ]
"""
score = []
for i in range(5):
    res = []
    temp_score = []
    n=0

    for i in range(3):
        print("输入排名")
        res.append(int(input()))
        n += res[i]
    
    res.sort()
    print(res)

    for i in range(3):
        temp_score.append(res[2-i] / n)
    print(temp_score)
    score.append(temp_score)
print(score)