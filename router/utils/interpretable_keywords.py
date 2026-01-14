from router.utils.config import InterpretableType



def get_interpretable_keywords(type: str) -> list:
    keywords = {}

    try:
        if type == InterpretableType.TASK_TYPE:
            keywords = {
                "code": ["code", "function", "python", "def "],
                "math": ["calculate", "solve", "equation"],
                "translation": ["translate", "in french", "to spanish"],
                "tool_use": ["json", "format", "api"],
            }
        elif type == InterpretableType.DOMAIN:
            keywords = {
                "programming": ["python", "java", "algorithm"],
                "finance": ["stock", "investment"],
                "legal": ["contract", "law"],
                "medical": ["symptom", "diagnosis"],
            }
        elif type == InterpretableType.SAFETY:
            keywords = {
                "toxic": ["hate", "kill", "suicide", "violence", "bomb"],
                "pi": ["private key", "password", "social security", "confidential"],
                "jailbreak": ["ignore instructions", "override", "developer mode", "no limits"],
                "safe": ["story", "email", "translate", "hello", "help"]
            }
        elif type == InterpretableType.REASONING_LEVEL:
            keywords = {
                "simple": ["what is", "who is", "list of", "definition"],
                "moderate": ["explain", "compare", "how to", "difference"],
                "complex": ["analyze", "evaluate", "strategy", "design", "optimize", "architect"],
                "logic": ["proof", "syllogism", "riddle", "puzzle", "step-by-step"]
            }
        elif type == InterpretableType.LENGTH:
            keywords = {
                "short": ["short", "brief", "summarize"],
                "medium": ["medium", "explain", "standard"],
                "long": ["long", "detailed", "essay"],
                "very_long": ["book", "thesis", "comprehensive"]
            }
        
    except Exception as e:
        raise e



    return keywords