import typing as tp
import json

from decimal import Decimal


def decode_typed_json(json_value: str) -> tp.Any:
    """
    Returns deserialized object from json string.
    Checks __custom_key_type__ in object's keys to choose appropriate type.

    :param json_value: serialized object in json format
    :return: deserialized object
    """
    data = json.loads(json_value)

    def process(obj: tp.Any) -> tp.Any:
        if isinstance(obj, dict):
            if "__custom_key_type__" in obj:
                key_type = obj.pop("__custom_key_type__")
                type_map = {"int": int, "float": float, "decimal": Decimal}
                converter = type_map[key_type]
                return {converter(k): process(v) for k, v in obj.items()}
            else:
                return {k: process(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [process(item) for item in obj]
        else:
            return obj

    return process(data)
