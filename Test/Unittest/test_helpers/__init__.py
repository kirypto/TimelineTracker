def get_fully_qualified_name(class_type: type):
    return f"{class_type.__module__}.{class_type.__name__}"
