import openai
import pandas as pd
import logging
import re
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=f"debate_judge_{int(time.time())}.log",
    filemode="a",
)
logger = logging.getLogger(__name__)
# 同时添加一个控制台处理器，方便在终端实时查看日志
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
logger.addHandler(console_handler)


class llm_client:
  def __init__(self):
    self.client = openai.OpenAI(
      base_url="https://gateway.api.anyint.ai/openai/v1/",
      api_key="sk-51009f73f12b15931d753a69f3a71b28"
    )
    self.register_models = ["gpt-5", "deepseek-v3.2-exp","qwen3-max","gemini-2.5-pro"]
    self.length = len(self.register_models)
    self.test_type = ""

  def get_prompt(self):
    prompt = f"""
            solve the question step-by-step,and give the final answer in the end.
            example format:
            {{
                "reasoning_steps": ... # your reasoning steps
                "final_answer": ... # your final answer
            }}
            """
    
    return prompt
  
  def call_api(self, question, model):
    response = self.client.chat.completions.create(
      model=model,
      messages=[
        {"role": "user", "content": f"please answer the question: {question}"},
        {"role": "system", "content": self.get_prompt()}
      ]
    )
    return response
    
  def get_test_file(self):
    while True:
      print("输入测试文件，1 for math 2 for mmlu 3 for code")
      res = int(input())
      if res==1:
        file_path = "test_MATH.csv"
        self.test_type = "math"
        break
      elif res==2:
        file_path = "test_MMLU.csv"
        self.test_type = "mmlu"
        break
      elif res==3:
        file_path = "test_humanev.csv"
        self.test_type = "code"
        break
      else:
        print("输入错误")
        continue

    return file_path
    
  def detect_llm(self):
    file_path = self.get_test_file()

    for i in range(self.length):
      model = self.register_models[i]

      if self.test_type == "math":
        self.test_MATH(file_path, model)
      elif self.test_type == "mmlu":
        self
      elif self.test_type == "code":
        pass
      else:
        print("不存在的test_type")
      response = self.call_api(self.register_models[i])

  def detect_llm_exalmple(self):
    response = self.call_api("你好", "deepseek-3.2")
    print(response)

if __name__ == "__main__":
  client = llm_client()
  client.detect_llm_exalmple()


""""
https://lmarena.ai/zh/leaderboard
["gpt-5", "deepseek-v3.2-exp","qwen3-max","gemini-2.5-pro"]
  math: gemini-2.5-pro qwen3-max deepseek-v3.2-exp 
  code: qwen3-max gemini-2.5-pro deepseek-v3.2-exp  
  creative_writing: gemini-2.5-pro deepseek-v3.2-exp qwen3-max 
  long_query: gemini-2.5-pro qwen3-max deepseek-v3.2-exp
  expert: qwen3-max gemini-2.5-pro deepseek-v3.2-exp
  cost: deepseek-v3.2-exp qwen3-max gemini-2.5-pro
  latency: deepseek-v3.2-exp qwen3-max gemini-2.5-pro
"""