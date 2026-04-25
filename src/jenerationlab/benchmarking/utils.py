import csv
import yaml
import copy

DEFAULT_PROCESSING = []

DEFAULT_CHECKS = [
    {
        "function": "is_exact",
        "params": { }
    }
]

DEFAULT_SCORING = {
    "min": 1
}


def get_param(default_case_params, case, param):
    if param in case:
        if case[param]:
            return case[param]
    else:
        case_param = copy.deepcopy(default_case_params[param])
        if param == "checks":
            print("in csv", case["answer"])
            case_param[0]["params"]["expected"] = case["answer"]
            print("in dict", case_param[0]["params"]["expected"])
        return case_param


def csv_to_llm_benchmark_config(
    input_csv_path, 
    output_config_path,
    benchmark_title,
    benchmark_system_prompt = None,
    processing = DEFAULT_PROCESSING,
    checks = DEFAULT_CHECKS,
    scoring = DEFAULT_SCORING,
):
    config = {}

    if benchmark_system_prompt:
        config["benchmark_system_prompt"] = {
            "role": "system",
            "content": benchmark_system_prompt
        }
    
    benchmark_title = benchmark_title.replace(" ", "_")

    default_case_params = {
        "processing": processing,
        "checks": checks,
        "scoring": scoring
    }

    cases = []
    with open(input_csv_path, mode='r', encoding='utf-8') as file:

        reader = csv.DictReader(file)
        for i, case in enumerate(reader):
            case_dict = {
                "case_id": benchmark_title + "_" + str(i),
                "messages": [{
                    "role": "user",
                    "content": case["question"]
                }],
                "processing": get_param(default_case_params, case, "processing"),
                "checks": get_param(default_case_params, case, "checks"),
                "scoring": get_param(default_case_params, case, "scoring"),
            }
            cases.append(case_dict)

    config["cases"] = cases

    print(config["cases"])

    with open(output_config_path, 'w') as file:
        yaml.dump(config, file, sort_keys=False)  




