from config import InterpretableType



def get_interpretable_keywords(type: str) -> list:
    if type == InterpretableType.TASK_TYPE:
        keywords = {
            "code": ["code", "function", "python", "def "],
            "math": ["calculate", "solve", "equation"],
            "translation": ["translate", "in french", "to spanish"],
            "tool_use": ["json", "format", "api"],
        }
    elif type == InterpretableType.MATH:
        keywords = {
            "programming": ["python", "java", "algorithm"],
            "finance": ["stock", "investment"],
            "legal": ["contract", "law"],
            "medical": ["symptom", "diagnosis"],
        }


    return keywords