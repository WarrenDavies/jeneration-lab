import yaml

from jenerationlab.core.experiment import Experiment

with open("configs/experiment_demo.yaml", 'r') as stream:
    config = yaml.safe_load(stream)

experiment = Experiment(config)