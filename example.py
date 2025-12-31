import yaml

from jenerationlab.core.experiment import Experiment
from jenerationlab.core.runner import Runner
from jenerationlab.storage.storage_manager import StorageManager

with open("configs/experiment_demo.yaml", 'r') as stream:
    config = yaml.safe_load(stream)

experiment = Experiment(config)
storage_manager = StorageManager(config)
runner = Runner(config, experiment, storage_manager)
runner.run()


