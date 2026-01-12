import logging
import os

# 配置日志输出格式
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别
    format='%(asctime)s - %(levelname)s - %(message)s',
    # 将日志输出到文件 (可选，如果只想看控制台就删掉 filename 这一行)
    filename=os.path.join(os.path.dirname(__file__), 'app.log') 
)

# 直接生成一个全局的 logger 实例
logger = logging.getLogger(__name__)
