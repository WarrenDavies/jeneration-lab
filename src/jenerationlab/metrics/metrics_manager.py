from pathlib import Path

from jenerationlab.metrics import registry


class MetricsManager():
    """
    """
    def __init__(self, config, storage_manager):
        self.config = config["metrics"]
        self.experiment_config = config["experiment"]
        self.storage_manager = storage_manager
        self.artifact_folder = self.experiment_config["artifact_folder"]
        self.metric_calculators = self.get_metrics_calculators()
        self.df_all_measurements = self.import_data_to_df("measurements")
        self.df_artifacts = self.import_data_to_df("artifacts")       


    def import_data_to_df(self, data_source):
        conn = self.storage_manager.data_connections[data_source]
        df = conn.to_pandas()
        
        return df


    def filter_to_experiment(self, df, experiment_id):
        experiment_mask = df["experiment_id"] == experiment_id
        df = df[experiment_mask]
        return df


    def filter_to_rows_with_measurement(self, df, measurement_name):
        measurement_name_mask = df["measurement_name"] == measurement_name
        df = df[measurement_name_mask]
        return df


    def get_queue(self, metric_name):
        """
        Logic to get uncompleted metrics within a given experiment.
        """
        df_artifacts = self.filter_to_experiment(
            self.df_artifacts,
            self.experiment_config["experiment_id"]
        )
        df_measurements = self.filter_to_experiment(
            self.df_all_measurements,
            self.experiment_config["experiment_id"]
        )
        df_artifacts_with_metric = self.filter_to_rows_with_measurement(
            df_measurements,
            metric_name,
        )

        all_artifacts = df_artifacts["artifact_id"].tolist()
        artifacts_with_metrics = df_artifacts_with_metric["artifact_id"].tolist()
        queue = list(set(all_artifacts) - set(artifacts_with_metrics))
        
        return queue


    def get_metrics_calculators(self):
        metric_calculators = {}

        for metric_calculator in self.config:
            metric_calculators[metric_calculator] = (
                registry.get_object(metric_calculator)
            )

        return metric_calculators


    def get_file_path(self, artifact_id):
        artifact_mask = self.df_artifacts["artifact_id"] == artifact_id
        df_artifact = self.df_artifacts[artifact_mask]
        file_name = df_artifact["filename"].iat[0]
        return file_name


    def get_text_artifact(self, artifact_id):

        file_name = self.get_file_path(artifact_id)
        file_path = Path(self.artifact_folder) / file_name
        file_path = str(file_path)
        with open(file_path, "r", encoding="utf-8") as file:
            text_artifact = file.read()
        return text_artifact


    def get_image_artifact(self, artifact_id):
        pass


    def get_artifact(self, artifact_id):
        GET_ARTIFACT_FUNC_REGISTRY = {
            "image": self.get_image_artifact,
            "text": self.get_text_artifact
        }

        func = GET_ARTIFACT_FUNC_REGISTRY[
            self.experiment_config["generation_format"]
        ]

        return func(artifact_id)

    
    def calculate_metrics(self):
        
        for metric in self.config:
            queue = self.get_queue(metric)
            for task in queue:
                artifact = self.get_artifact(task)
                self.metric_calculators[metric].calculate(artifact)