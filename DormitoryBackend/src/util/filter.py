def get_filter_condition(d: dict, model: type):
    condition = True
    for (key, value) in d.items():
        condition = condition & (getattr(model, key) == value)
    return condition
