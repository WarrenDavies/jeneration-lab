from jenerationlab.metrics.base_metric import BaseMetric
from jenerationlab.metrics.registry import register


@register("word_count")
class WordCount(BaseMetric):

    def __init__(self):
        super().__init__()

        
    def calculate(self, output):
        word_count = len(output.lower().split())
        print(word_count)
        return word_count