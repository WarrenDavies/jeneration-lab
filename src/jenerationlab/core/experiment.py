import datetime
from pathlib import Path
from itertools import product

from jenerationutils.benchmarker.benchmarker import Benchmarker

from jenerationlab.variables import registry as variable_registry
from jenerationlab.core.generators import generator_registries


class Experiment():
    """
    """
    def __init__(self, config):
        """
        """
        self.config = config
        self.start_timestamp_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.setup_experiment_folders()
        self.generator_config = self.process_generator_config()
        self.generator = self.get_generator()
        self.generator.create_pipeline()
        self.variables = self.define_variables()
        self.inference_configs = self.get_inference_configs()

    def setup_experiment_folders(self):
        self.experiment_folder = Path("outputs/") / Path(self.start_timestamp_str)
        self.experiment_folder.mkdir(parents=True, exist_ok=True)

        self.images_output_folder = Path(self.experiment_folder) / Path("images")
        self.images_output_folder.mkdir(parents=True, exist_ok=True)

        self.text_output_folder = Path(self.experiment_folder) / Path("text")
        self.text_output_folder.mkdir(parents=True, exist_ok=True)


    def process_generator_config(self):
        generator_config = self.config["generator"]
        generator_config["image_save_folder"] = self.images_output_folder
        
        return generator_config


    def get_generator(self):
        generation_format = self.config["experiment"]["generation_format"]
        generator_registry = generator_registries[generation_format]
        generator = generator_registry.get_model_class(self.generator_config)
        
        return generator


    def define_variables(self):
        variables = []
        for variable_name in self.config["variables"]:
            variable_config = self.config["variables"][variable_name]
            variable = variable_registry.get_object(variable_config)
            variable.name = variable_name
            variables.append(variable)
        return variables


    def get_inference_configs(self):
        inference_configs = []
        inference_param_combos = product(*[variable.values for variable in self.variables])
        for inference_param_combo in inference_param_combos:
            inference_configs.append({
                variable.name: value 
                for variable, value in zip(self.variables, inference_param_combo)
            })
        return inference_configs


    def run(self):
        for inference_config in self.inference_configs:
            print(inference_config)
            self.generator.config.update(inference_config)
            with Benchmarker() as benchmarker:
                self.generator.run_pipeline()
            print(benchmarker.execution_time)
            self.generator.save_image()
        