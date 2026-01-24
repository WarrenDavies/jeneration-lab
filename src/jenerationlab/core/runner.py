import datetime
import sys
import json
import copy
import uuid

from pydantic import BaseModel
from pathlib import Path

from jenerationutils.benchmarker.benchmarker import Benchmarker
from jenerationutils.jenerationrecord import registry as recorder_registry

from jenerationlab.schemas.base import BaseSchema
from jenerationlab.schemas.registry import get_schema_class
from jenerationlab.rater.rater import Rater


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
        self.setup_experiment_folders(self.start_timestamp_str)
        self.GenerationRecordClass = recorder_registry.get_class(core_config["output_data_type"])
        self.run_context = {
            "experiment_id": self.experiment.experiment_id,
            **experiment_config["experiment"], 
            **experiment_config["generator"]
        }
        self.ParamsSchema = self.get_params_schema()
        self.save_config()


    def setup_experiment_folders(self, experiment_folder_name):
        self.experiment_folder_name = experiment_folder_name

        self.experiment_folder = Path("outputs/") / Path(experiment_folder_name)
        self.experiment_folder.mkdir(parents=True, exist_ok=True)

        self.output_folder = Path(self.experiment_folder) / Path("artifacts")
        self.output_folder.mkdir(parents=True, exist_ok=True)


    def get_params_schema(self):
        # This lives here temporarily, need to update and republish the generator
        # to emit the params class it expects.
        # e.g., this will simply changes to ParamsSchema = self.generator.get_params_schema()
        class ParamsSchema(BaseModel):
            dtype: str = ""
            seed: int = 0
            height: int = 0
            width: int = 0
            num_inference_steps: int = 0
            guidance_scale: float = 0
            enable_attention_slicing: bool = True
            scheduler: str = ""

        return ParamsSchema


    def build_run_context(self, benchmarker, artifact_bundle, filename):

        run_context = self.run_context.copy()
        run_context["artifact_id"] = uuid.uuid4().hex[:8]
        run_context["timestamp"] = self.start_timestamp_str
        run_context["batch_generation_time"] = benchmarker.execution_time
        run_context["generation_time"] = benchmarker.execution_time / self.experiment.generator.batch_size
        run_context["params"] = json.dumps(
            dict(self.ParamsSchema(**{
                **self.experiment.generator.config,
                **artifact_bundle
            })),
            sort_keys=True
        )
        run_context["filename"] = filename
        run_context["output_path"] = str(self.output_folder)

        return run_context


    def normalize_to_bundles(raw_output):
        items = raw_output if isinstance(raw_output, list) else [raw_output]
        normalized = []
        for item in items:
            if isinstance(item, dict):
                normalized.append(item)
            else:
                normalized.append({
                    "artifact": item, 
                    "seed": None
                })
        return normalized


    def build_measurement_record(self, artifact_id, metric_name, metric):

        rating_type_key = Rater.get_rating_type_key(metric)

        values = {
            "value_int": None,
            "value_float": None,
            "value_str": None,
            "value_bool": None
        }
        values[rating_type_key] = metric

        measurement_record = {
            "measurement_id": uuid.uuid4().hex[:8],
            "artifact_id": artifact_id,
            "experiment_id": self.experiment.experiment_id,
            "timestamp": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
            "producer": "auto",
            "measurement_name": metric_name,
            **values
        }

        return measurement_record


    def save_metadata(self, dataset_name, run_context):
        SchemaClass = get_schema_class(dataset_name)
        metadata_record = self.GenerationRecordClass(
            schema = SchemaClass,
            generation_metadata = run_context
        )
        generation_data_row = metadata_record.create_data_row()
        self.storage_manager.data_connections[dataset_name].append_data(generation_data_row)


    def save_generation_timing(self, dataset_name, run_context):
        
        for measurement_name in ["generation_time", "batch_generation_time"]:

            measurement_record = self.build_measurement_record(
                run_context["artifact_id"],
                measurement_name,
                run_context[measurement_name]
            )
            
            self.save_metadata(dataset_name, measurement_record)


    def get_param_changes(self, inference_config):
        param_changes = [
            key 
            for key in inference_config 
            if key in self.experiment.generator.config 
            and inference_config[key] != self.experiment.generator.config[key]
        ]
        return param_changes


    def reload_generator_if_needed(self, inference_config, param_changes):
        if any(param not in self.experiment.generator.get_runtime_params() for param in param_changes):
            print("model change param dectected, tearing down model")
            self.experiment.rebuild_generator(inference_config)
        else:
            self.experiment.generator.config.update(inference_config)


    def save_output_to_disk(self, artifacts):
        self.storage_manager.artifacts.extend(artifacts)
        batch_filenames = self.storage_manager.save(self.output_folder, artifacts)

        return batch_filenames


    def run(self):
        """
        """
        for inference_config in self.experiment.inference_configs:
            if self.experiment_config["experiment"]["reset_model_each_run"]:
                self.experiment.generator.prepare()
            
            param_changes = self.get_param_changes(inference_config)
            self.reload_generator_if_needed(inference_config, param_changes)

            with Benchmarker() as benchmarker:
                output = self.experiment.generator.generate()
            artifacts = [artifact for artifact in output.batch]

            batch_filenames = self.save_output_to_disk(artifacts)

            for i, artifact in enumerate(artifacts):
                run_context = self.build_run_context(
                    benchmarker, 
                    artifact.item_extras,
                    batch_filenames[i]
                )
                self.save_metadata("artifacts", run_context)
                self.save_generation_timing("measurements", run_context)
            self.save_metadata("experiments", run_context)
            

            

    def save_config(self):
        config = copy.deepcopy(self.experiment.config)
        config["experiment"]["experiment_id"] = self.experiment.experiment_id
        config["experiment"]["artifact_folder"] = str(self.output_folder)
        config["experiment"]["experiment_folder"] = str(self.experiment_folder)

        self.experiment_config_path = Path(self.experiment_folder / "experiment.yaml")
        self.storage_manager.dump_config(config, self.experiment_config_path)
