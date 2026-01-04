import datetime
import sys
import json

from pydantic import BaseModel

from jenerationutils.benchmarker.benchmarker import Benchmarker
from jenerationutils.jenerationrecord import registry as recorder_registry
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
        self.GenerationRecordClass = recorder_registry.get_class(core_config["output_data_type"])
        self.run_context = {
            "experiment_id": self.experiment.experiment_id,
            **experiment_config["experiment"], 
            **experiment_config["generator"]
        }
        self.ParamsSchema = self.get_params_schema()

    
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
        run_context["output_path"] = str(self.storage_manager.output_folder)

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


    def run(self):
        """
        """
        for inference_config in self.experiment.inference_configs:
            if self.experiment.generator.config["reset_torch_generators"]:
                self.experiment.generator.create_generators()
            
            self.experiment.generator.config.update(inference_config)
            with Benchmarker() as benchmarker:
                batch = self.experiment.generator.run_pipeline()
            
            artifacts = [item["artifact"] for item in batch]
            self.storage_manager.artifacts.extend(artifacts)
            batch_filenames = self.storage_manager.save(artifacts)

            for i, artifact_bundle in enumerate(batch):
                run_context = self.build_run_context(
                    benchmarker, 
                    artifact_bundle,
                    batch_filenames[i]
                )
                generation_metadata_record = self.GenerationRecordClass(
                    schema=BaseSchema,
                    generation_metadata = run_context
                )
                data_row = generation_metadata_record.create_data_row()
                self.storage_manager.data_connection.append_data(data_row)
            