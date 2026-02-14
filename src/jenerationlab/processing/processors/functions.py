import re

PROCESSORS_REGISTRY = {}

def register(name):
    def decorator(func):
        PROCESSORS_REGISTRY[name] = func
        return func
    return decorator


@register("remove_code_fences")
def remove_code_fences(text):
    """
    """
    processed_lines = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("```"):
            continue
        processed_lines.append(line)
    
    return "\n".join(processed_lines)


@register("extract_json")
def extract_json(text):
    """
    """
    start = text.find('{')
    end = text.rfind('}')

    if (start == -1) or (end == -1) or (end < start):
        return text

    json_str = text[start:end + 1]

    return json_str