import re

from jenerationlab.metrics.base_metric import BaseMetric
from jenerationlab.metrics.registry import register


@register("word_count")
class WordCount(BaseMetric):

    def __init__(self):
        super().__init__()

        
    def calculate(self, text):
        word_count = len(re.findall(r"\b[\w']+\b", text))
        return word_count