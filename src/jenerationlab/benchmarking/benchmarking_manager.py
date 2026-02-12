from jenerationlab.benchmarking.checks.functions import CHECKS_REGISTRY

DEFAULT_CONFIG = {
    "default": True,
    "cases": [
        {"case_id": None}
    ]
}


class BenchmarkingManager():
    """
    """

    def __init__(self, benchmarking_config = DEFAULT_CONFIG):
        self.benchmarking_config = benchmarking_config
        self.CHECKS_REGISTRY = CHECKS_REGISTRY


    def run_check(self, check_name, params, output):
        check_func = self.CHECKS_REGISTRY[check_name]
        check_result = check_func(params, output)
        return check_result


    def remove_message_variables(self, variables):
        return [
            variable
            for variable in variables
            if variable.name != "messages"
        ]


    def create_cases(self):
        self.cases = self.benchmarking_config["cases"]
        if "benchmark_system_prompt" in self.benchmarking_config:
            for case in self.cases:
                case["messages"] = [self.benchmarking_config["benchmark_system_prompt"]] + case["messages"]
