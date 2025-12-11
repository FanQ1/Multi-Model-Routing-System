from enum import Enum

class InterpretableType(Enum):
   TASK_TYPE = 1
   DOMAIN = 2
   SAFETY = 3
   LENGTH = 4
   REASONING_LEVEL = 5
   TENANT_PREFERENCE = 6
# --- for Q_encoder ---

TASK_TYPES = ["chat", "code", "math", "translation", "tool_use"]
DOMAINS = ["general", "programming", "math", "finance"]
REASONING_LEVELS = ["low", "medium", "high"]
SAFETY_LEVELS = ["normal", "sensitive", "high_risk"]
LENGTH_BUCKETS = ["short", "medium", "long"]
TENANT_PREFERENCES = ["cost", "latency", "quality"]



# --- for M_encoder ---

