from typing import Dict


def get_dict_with_prefix_keys(dictionary: Dict, prefix: str):
    return {prefix + str(key): val for key, val in dictionary.items()}
