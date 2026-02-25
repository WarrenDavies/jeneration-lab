from jenerationlab.processing.processors.functions import PROCESSORS_REGISTRY


class ProcessingManager():
    """
    """
    def __init__(self):
        self.PROCESSORS_REGISTRY = PROCESSORS_REGISTRY


    def run_processing_func(self, processor_name, params, output):
        processor_func = self.PROCESSORS_REGISTRY[processor_name]
        processor_result = processor_func(output, **params)
        return processor_result


    def process_outputs(self, output, case_config):

        if "processing" not in case_config:
            return output

        for artifact in output.batch:

            processed_output = artifact.data
            for processing_function in case_config["processing"]:
                if "params" not in processing_function:
                    params = {}
                else:
                    params = processing_function["params"]

                processed_output = self.run_processing_func(
                    processing_function["function"],
                    params,
                    processed_output
                )

            artifact.data = processed_output
        return output
