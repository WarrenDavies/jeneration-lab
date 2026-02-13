import uuid
import datetime

from jenerationutils.jenerationrecord import registry as recorder_registry

from jenerationlab.metrics.base_metrics_manager import BaseMetricsManager
from jenerationlab.schemas.registry import get_schema_class

class BenchmarkEvaluator(BaseMetricsManager):
    """
    """

    def __init__(self, experiment_id, core_config, benchmarking_config, storage_manager):
        self.experiment_id = experiment_id
        self.core_config = core_config
        self.benchmarking_config = benchmarking_config
        self.storage_manager = storage_manager
        self.GenerationRecordClass = recorder_registry.get_class(core_config["output_data_type"])


    def filter_to_benchmarking_run(self, df, benchmark_run_id):
        benchmark_run_id_mask = df["benchmark_run_id"] == benchmark_run_id
        df = df[benchmark_run_id_mask]
        return df


    def evaluate_cases(self, benchmark_run_id):
        df_checks = self.import_data_to_df("checks")
        df_run = self.filter_to_benchmarking_run(df_checks, benchmark_run_id)
        df_case_scores = df_run.groupby('case_id')['score'].sum().reset_index()
        case_scores = df_case_scores.to_dict('records')
        return case_scores


    def get_case_config_by_id(self, case_id):
        for case in self.benchmarking_config["cases"]:
            if case['case_id'] == case_id:
                return case
        return None


    def build_case_result_record(self, score):
        case = self.get_case_config_by_id(score["case_id"])
        required_check_score = case["scoring"]["min"]
        sum_of_check_scores = score["score"]
        passed = 1 if sum_of_check_scores >= required_check_score else 0

        record = score
        record["case_result_id"] = uuid.uuid4().hex[:8]
        record["sum_of_check_scores"] = record["score"]
        record["experiment_id"] = self.experiment_id
        record["ts"] = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        record["required_check_score"] = required_check_score
        record["sum_of_check_scores"] = sum_of_check_scores
        record["passed"] = passed

        return record


    def save_metadata(self, dataset_name, run_context):
        SchemaClass = get_schema_class(dataset_name)
        metadata_record = self.GenerationRecordClass(
            schema = SchemaClass,
            generation_metadata = run_context
        )
        generation_data_row = metadata_record.create_data_row()
        self.storage_manager.data_connections[dataset_name].append_data(generation_data_row)


    def evaluate(self, benchmark_run_ids):
        for benchmark_run_id in benchmark_run_ids:
            case_scores = self.evaluate_cases(benchmark_run_id)

            for case_score in case_scores:
                case_result_record = self.build_case_result_record(case_score)
                self.save_metadata("case_results", case_result_record)