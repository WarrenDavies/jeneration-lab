import yaml

from jenerationlab.core.experiment import Experiment
from jenerationlab.core.runner import Runner
from jenerationlab.storage.storage_manager import StorageManager
from jenerationlab.rater.rater import Rater

with open("configs/experiment_demo.yaml", 'r') as stream:
    experiment_config = yaml.safe_load(stream)

with open("configs/core_config.yaml", 'r') as stream:
    core_config = yaml.safe_load(stream)

with open("configs/rater_config.yaml", 'r') as stream:
    rater_config = yaml.safe_load(stream)

experiment = Experiment(experiment_config)
storage_manager = StorageManager(core_config, experiment_config)
runner = Runner(core_config, experiment_config, experiment, storage_manager)
runner.run()

storage_manager.create_data_connection(rater_config["data_connection"])


experiment_id = "b932bdef"
rating_manager = Rater(rater_config, storage_manager)
queue = rating_manager.get_queue(experiment_id)
print(queue)


