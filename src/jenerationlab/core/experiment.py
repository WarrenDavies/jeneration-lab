import datetime
import sys
from pathlib import Path
from itertools import product
import uuid
import copy

from jenerationutils.benchmarker.benchmarker import Benchmarker

from jenerationlab.variables import registry as variable_registry
from jenerationlab.core.generators import generator_registries
from jenerationlab.benchmarking.benchmarking_manager import BenchmarkingManager

class Experiment():
    """
    """
    def __init__(self, config):
        """
        """
        self.experiment_id = uuid.uuid4().hex[:8]
        self.benchmarking_manager = None
        self.config = config
        self.generator_config = self.process_generator_config()
        self.generator = self.get_generator()
        self.variables = self.define_variables()
        self.inference_configs = self.get_inference_configs()
        self.generator.load()
        self.generator.prepare()
        self.process_benchmarking()


    def process_benchmarking(self):
        
        benchmarking_not_defined = "benchmarking" not in self.config
        format_is_image = self.config["experiment"]["generation_format"] == "image"

        if benchmarking_not_defined or format_is_image:
            ## create mock benchmark
            return
        
        self.benchmarking_manager = BenchmarkingManager(
            self.config["benchmarking"]
        )

        self.variables = (
            self.benchmarking_manager.remove_message_variables(self.variables)
        )

        self.benchmarking_manager.create_cases()


    def process_generator_config(self):
        generator_config = self.config["generator"]
        
        return generator_config


    def get_generator(self, generator_config = None):
        if not generator_config:
            generator_config = self.generator_config
        generation_format = self.config["experiment"]["generation_format"]
        generator_registry = generator_registries[generation_format]
        generator = generator_registry.get_model_class(generator_config)
        
        return generator


    def rebuild_generator(self, generator_config):
        
        self.generator.teardown()
        self.generator = None

        new_generator_config = self.generator_config.copy()
        new_generator_config.update(generator_config)

        self.generator = self.get_generator(
            new_generator_config
        )
        self.generator.load()
        self.generator.prepare()

        
    def define_variables(self):
        variables = []
        for variable_name in self.config["variables"]:
            variable_config = self.config["variables"][variable_name]
            variable = variable_registry.get_object(variable_config)
            variable.name = variable_name
            variables.append(variable)
        return variables


    def unnest_multi_configs(self, config):
        unnested_config = {}
        for key, value in config.items():
            if isinstance(value, dict):
                unnested_config.update(value)
            else:
                unnested_config[key] = value
        return unnested_config


    def get_inference_configs(self):
        inference_configs = []
        inference_param_combos = product(*[variable.values for variable in self.variables])
        for inference_param_combo in inference_param_combos:
            inference_configs.append({
                variable.name: value 
                for variable, value in zip(self.variables, inference_param_combo)
            })
        unnested_inference_configs = []
        for config in inference_configs:
            config_unnested = self.unnest_multi_configs(config)
            unnested_inference_configs.append(config_unnested)

        return unnested_inference_configs


    def run(self):
        for inference_config in self.inference_configs:
            self.generator.config.update(inference_config)
            with Benchmarker() as benchmarker:
                self.generator.run_pipeline()
            print("generation time:", benchmarker.execution_time)
            self.generator.save_image()
        