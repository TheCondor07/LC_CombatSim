def format_sources(sources):
    source_info = ""
    for source in sources:
        source_info += f"{source[0]}: "
        if source[1] >= 0:
            source_info += "+"
        source_info += str(source[1]) + ", "

    return source_info[:-2]