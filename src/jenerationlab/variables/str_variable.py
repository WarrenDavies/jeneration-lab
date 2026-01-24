from jenerationlab.variables.variable import Variable
from jenerationlab.variables.registry import register_model

@register_model("str")
class StrVariable(Variable):

    def __init__(self, config):
        super().__init__(config)
        self.config = config
        self.values = self.get_values()
        

    def get_values(self):
        return self.config["options"]

    