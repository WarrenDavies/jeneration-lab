import datetime
import sys

from pydantic import BaseModel

from jenerationutils.benchmarker.benchmarker import Benchmarker
from jenerationlab.schemas.base import BaseSchema


class Runner():
    """
    """
    def __init__(self, core_config, experiment_config, experiment, storage_manager):
        """
        """
        self.start_timestamp_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.core_config = core_config
        self.experiment_config = experiment_config
        self.experiment = experiment
        self.storage_manager = storage_manager
        self.storage_manager.setup_experiment_folders(self.start_timestamp_str)
        self.generation_metadata = BaseSchema(**{**experiment_config["experiment"], **experiment_config["generator"]})
        self.ParamsSchema = self.get_params_schema()
        self.storage_manager.data_connection.create_new_data_source(["test"])
        # print(self.data_connection)
        # sys.exit()

    
    def get_params_schema(self):
        # This eventually to be emitted from the generator
        # e.g., ParamsSchema = self.parent.generator.get_params_schema()

        class ParamsSchema(BaseModel):
            dtype: str = ""
            seed: int = 0
            height: int = 0
            width: int = 0
            inf_steps: int = 0
            guidance_scale: float = 0
            enable_attention_slicing: bool = True
            scheduler: str = ""

        return ParamsSchema


    def run(self):
        """
        """
        for inference_config in self.experiment.inference_configs:
            self.experiment.generator.config.update(inference_config)
            with Benchmarker() as benchmarker:
                self.storage_manager.images = self.experiment.generator.run_pipeline()
            print(benchmarker.execution_time)
            self.storage_manager.save()