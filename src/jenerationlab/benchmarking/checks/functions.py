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
        "passed": passed
    }


@register("count_lines")
def count_lines(params, output):
    lines = output.splitlines()
    number_of_lines =  str(sum(1 for line in lines if line.strip()))
    passed = number_of_lines == params["expected"]
    return {
        "actual": number_of_lines,
        "expected": params["expected"],
        "passed": passed
    }
