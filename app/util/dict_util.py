def combine(*dictionaries):
    """
    Recursively merges dictionaries.
    """
    def deep_merge(base, nxt):
        for key, value in nxt.items():
            # Check whether both the base and the new value are dictionaries.
            if (key in base and 
                isinstance(base[key], dict) and 
                isinstance(value, dict)):
                # Merge the sub-dictionaries.
                deep_merge(base[key], value)
            else:
                # Otherwise, overwrite or add standard value.
                base[key] = value
        return base

    combined_dict = {}
    for dictionary in dictionaries:
        deep_merge(combined_dict, dictionary)
        
    return combined_dict
