import datetime

from jenerationutils.benchmarker.benchmarker import Benchmarker


class Runner():
    """
    """
    def __init__(self, config, experiment, storage_manager):
        """
        """
        self.start_timestamp_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.config = config
        self.experiment = experiment
        self.storage_manager = storage_manager
        self.storage_manager.setup_experiment_folders(self.start_timestamp_str)


    def run(self):
        """
        """
        for inference_config in self.experiment.inference_configs:
            self.experiment.generator.config.update(inference_config)
            with Benchmarker() as benchmarker:
                self.storage_manager.images = self.experiment.generator.run_pipeline()
            print(benchmarker.execution_time)
            self.storage_manager.save()