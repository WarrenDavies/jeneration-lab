from pathlib import Path
import uuid
import datetime

from jenerationlab.metrics import registry as metrics_registry
from jenerationutils.jenerationrecord import registry as recorder_registry
from jenerationlab.schemas.measurements import MeasurementSchema
from jenerationlab.metrics.base_metrics_manager import BaseMetricsManager


class MetricsManager(BaseMetricsManager):
    """
    """
    def __init__(self, core_config, experiment_config, storage_manager):
        super().__init__(core_config, experiment_config, storage_manager)
        self.metric_calculators = self.get_metrics_calculators()


    def get_metrics_calculators(self):
        metric_calculators = {}

        for metric_calculator in self.experiment_config["metrics"]:
            metric_calculators[metric_calculator] = (
                metrics_registry.get_object(metric_calculator)
            )

        return metric_calculators


    def save_rating(self, measurement_record):
        data_row = measurement_record.create_data_row()
        self.storage_manager.data_connections["measurements"].append_data(
            data_row
        )


    def calculate_metrics(self):
        
        for metric_name in self.experiment_config["metrics"]:
            queue = self.get_queue(metric_name)
            for artifact_id in queue:
                artifact = self.get_artifact(artifact_id)
                metric_value = self.metric_calculators[metric_name].calculate(artifact)

                measurement_record = self.build_measurement_record(
                    artifact_id,
                    metric_name,
                    metric_value
                )
                measurement_record = self.GenerationRecordClass(
                    schema=MeasurementSchema,
                    generation_metadata = measurement_record
                )
                self.save_metric(measurement_record)
