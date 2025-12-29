import datetime

from jenerationlab.core.generators import generator_registries


class Experiment():
    """
    """
    def __init__(self, config):
        """
        """
        self.start_timestamp_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.config = config
        self.generator = self.get_generator()
        self.generator.create_pipeline()
        
        # self.variables = self.define_variables()


    def get_generator(self):

        generation_format = self.config["experiment"]["generation_format"]
        generator_registry = generator_registries[generation_format]
        generator = generator_registry.get_model_class(self.config["generator"])
        
        return generator


    def define_variables(self):
        for variable in self.config["variables"]:
            pass


    def run(self):
        pass
