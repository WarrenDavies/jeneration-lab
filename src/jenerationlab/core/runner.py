import datetime
import sys
import json
import copy
import uuid
import copy

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
    def __init__(
        self, core_config, experiment_config, 
        experiment, storage_manager, processing_manager
    ):
        """
        """
        self.start_timestamp_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.core_config = core_config
        self.experiment_config = experiment_config
        self.experiment = experiment
        self.storage_manager = storage_manager
        self.processing_manager = processing_manager
        self.setup_experiment_folders(self.start_timestamp_str)
        self.GenerationRecordClass = recorder_registry.get_class(core_config["output_data_type"])
        self.run_context = {
            "experiment_id": self.experiment.experiment_id,
            **experiment_config["experiment"], 
            **experiment_config["generator"]
        }
        self.ParamsSchema = self.experiment.generator.get_params_schema()
        self.save_config()


    def create_id(self):
        return uuid.uuid4().hex[:8]


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


    def build_run_context(self, benchmark_run_id, artifact, filename):

        run_context = self.run_context.copy()

        run_context.update(self.experiment.generator.config)

        run_context["benchmark_run_id"] = benchmark_run_id
        run_context["timestamp"] = self.start_timestamp_str
        run_context["params"] = json.dumps(
            dict(self.ParamsSchema(**{
                **self.experiment.generator.config,
            })),
            sort_keys=True
        )
        run_context["output_path"] = str(self.output_folder)

        run_context["artifact_id"] = artifact.artifact_id
        run_context["batch_generation_time"] = artifact.generation_time
        run_context["generation_time"] = artifact.generation_time / self.experiment.generator.batch_size
        run_context["extras"] = json.dumps(
            dict(**{
                **artifact.item_extras,
            }),
            sort_keys=True
        )
        run_context["case_id"] = artifact.case_id
        
        run_context["filename"] = filename
        
        return run_context


    def update_run_context(self, run_context, *additions):

        for addition in additions:
            if hasattr(new_data, '__dict__'):
                addition = vars(addition)
            run_context.update(addition)

        return run_context


    def dump_to_json_if_dict(self, dict_):
        if not isinstance(dict_, dict):
            return dict_
        return json.dumps(dict_)



    def build_check_run_context(self, run_context, check, check_result):
        check_run_context = run_context
        check_run_context["check_id"] = uuid.uuid4().hex[:8]
        check_run_context["check_func"] = check["function"]
        check_run_context["check_func_params"] = json.dumps(
            dict(**{
                **{
                    k: v
                    for k, v in check["params"].items()
                    if k != "expected"
                }
            }),
            sort_keys=True
        )

        expected = self.dump_to_json_if_dict(check["params"]["expected"])
        check_run_context["expected"] = expected

        actual = self.dump_to_json_if_dict(check_result["actual"])
        check_run_context["actual"] = actual

        check_run_context["score"] = check_result["score"]

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


    def add_case_id(self, artifacts, case_id):
        for artifact in artifacts:
            artifact.case_id = case_id
        return artifacts


    def add_timing(self, artifacts, execution_time):
        for artifact in artifacts:
            artifact.generation_time = execution_time
        return artifacts


    def run_checks(self, case, artifact, run_context):
        for check in case["checks"]:
            check_run_context = copy.deepcopy(run_context)

            check_result = self.experiment.benchmarking_manager.run_check(
                check["function"],
                check["params"],
                artifact.data
            )

            check_run_context = self.build_check_run_context(
                run_context,
                check, 
                check_result
            )
            self.save_metadata("checks", check_run_context)


    def get_benchmark_run_id(self):
        if not self.experiment.benchmarking_manager.is_benchmark_run:
            benchmark_run_id = ""
        else:
            benchmark_run_id = self.create_id()

        return benchmark_run_id
        

    def run(self):
        """
        """
        benchmark_run_ids = []
        for inference_config in self.experiment.inference_configs:
            benchmark_run_id = self.get_benchmark_run_id()
            if benchmark_run_id:
                benchmark_run_ids.append(benchmark_run_id)
            for case in self.experiment.benchmarking_manager.cases:
                if self.experiment_config["experiment"]["reset_model_each_run"]:
                    self.experiment.generator.prepare()
                
                if "messages" in case:
                    inference_config["messages"] = case["messages"]

                param_changes = self.get_param_changes(inference_config)
                self.reload_generator_if_needed(inference_config, param_changes)


                with Benchmarker() as timer:
                    output = self.experiment.generator.generate()
                    output = self.processing_manager.process_outputs(
                        output, case
                    )

                artifacts = self.add_timing(output.batch, timer.execution_time)
                artifacts = self.add_case_id(artifacts, case["case_id"])

                batch_filenames = self.save_output_to_disk(artifacts)

                for i, artifact in enumerate(artifacts):
                    run_context = self.build_run_context(
                        benchmark_run_id,
                        artifact,
                        batch_filenames[i]
                    )
                    self.save_metadata("artifacts", run_context)
                    self.save_generation_timing("measurements", run_context)

                    if "checks" not in case:
                        continue

                    self.run_checks(case, artifact, run_context)

        self.save_metadata("experiments", run_context)

        self.experiment.benchmarking_manager.evaluate_benchmarks(benchmark_run_ids)


    def save_config(self):
        config = copy.deepcopy(self.experiment.config)
        config["experiment"]["experiment_id"] = self.experiment.experiment_id
        config["experiment"]["artifact_folder"] = str(self.output_folder)
        config["experiment"]["experiment_folder"] = str(self.experiment_folder)

        self.experiment_config_path = Path(self.experiment_folder / "experiment.yaml")
        self.storage_manager.dump_config(config, self.experiment_config_path)
