def format_tuples(t):
    """A helper function to format tuples in dropdowns.

    Args:
        t (tuple): A tuple made of an id and name, e.g. (project_id, project_name)
    """
    if isinstance(t, tuple):
        return f"{t[0]} (id: {t[1]})"
    else:
        return str(t)
