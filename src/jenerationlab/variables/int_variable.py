from jenerationlab.variables.variable import Variable
from jenerationlab.variables.registry import register_model

@register_model("int")
class IntVariable(Variable):

    def __init__(self, config):
        super().__init__(config)
        self.step = config["step"]
        self.values = self.get_values()
        

    def get_values(self):
        return list(range(
            self.min,
            self.max + 1,
            self.step
        ))

    