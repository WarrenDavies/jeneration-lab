import re

CHECKS_REGISTRY = {}

def register(name):
    def decorator(func):
        CHECKS_REGISTRY[name] = func
        return func
    return decorator


@register("is_exact")
def is_exact(params, output):
    passed = output == params["expected"]
    return {
        "actual": output,
        "expected": params["expected"],
        "score": 1 if passed else 0
    }


@register("count_lines")
def count_lines(params, output):
    lines = output.splitlines()
    number_of_lines = str(sum(1 for line in lines if line.strip()))
    passed = number_of_lines == params["expected"]
    return {
        "actual": str(number_of_lines),
        "expected": params["expected"],
        "score": 1 if passed else 0
    }


@register("contains")
def contains(params, output):
    contains = params["substring"] in output
    passed = contains == params["expected"]
    return {
        "actual": str(contains),
        "expected": params["expected"],
        "score": 1 if passed else 0
    }


@register("contains_word")
def contains_word(params, output):
    pattern = r'\b' + re.escape(params["substring"]) + r'\b'
    contains = bool(re.search(pattern, output))
    passed = str(contains).lower() == str(params["expected"]).lower()
    return {
        "actual": str(contains),
        "expected": params["expected"],
        "score": 1 if passed else 0
    }
    