from jenerationlab.variables.variable import Variable
from jenerationlab.variables.registry import register_model

import numpy as np

@register_model("float")
class FloatVariable(Variable):

    def __init__(self, config):
        super().__init__(config)
        self.min = config["min"]
        self.max = config["max"]
        self.step = config["step"]
        self.values = self.get_values()
        

    def get_values(self):
        return list(np.arange(
            self.min,
            self.max,
            self.step
        ))

    