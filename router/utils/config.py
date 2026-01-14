from enum import Enum

class InterpretableType(Enum):
   TASK_TYPE = 1
   DOMAIN = 2
   SAFETY = 3
   LENGTH = 4
   REASONING_LEVEL = 5
   TENANT_PREFERENCE = 6
# --- for Q_encoder ---

TASK_TYPES = [ "code", "math", "translation", "tool_use"]
DOMAINS = ["general", "programming", "math", "finance"]
REASONING_LEVELS = ["simple", "moderate", "complex", "logic"]
SAFETY_LEVELS = ["toxic", "pi", "jailbreak", "safe"]
LENGTH_BUCKETS = ["short", "medium", "long", "very_long"]
TENANT_PREFERENCES = ["quality", "cost", "latency", "balanced"]



# --- for M_encoder ---

