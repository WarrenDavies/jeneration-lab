from jenerationlab.processors.base_processor import BaseProcessor
from jenerationlab.processors.registry import register


@register("word_count")
class RemoveBackticks(BaseProcessor):
    """
    """
    def __init__(self):
        super().__init__()


    @staticmethod
    def process(text):
        """
        """
        processed_lines = []
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("```"):
                continue
            processed_lines.append(line)
        
        return "\n".join(processed_lines)
