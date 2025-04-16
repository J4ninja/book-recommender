def truncate_with_ellipsis(text, max_length):
    return text if len(text) <= max_length else text[:max_length - 3] + '...'