import datetime
from typing import Union
from peewee import BooleanField, IntegerField, DecimalField, CharField, FixedCharField
from peewee import DateField, DateTimeField, ForeignKeyField


bool_filter = {
    "type": bool,
}


def get_bool_filter_condition(value: bool, field):
    assert type(value) == bool
    return field == value


integer_filter = {
    "oneOf": [
        {
            "type": "integer",
        },
        {
            "type": "object",
            "properties": {
                "min": {
                    "type": "integer",
                },
                "max": {
                    "type": "integer",
                },
                "equal": {
                    "type": "integer",
                },
            },
            "additionalProperties": False,
        }
    ],
}


def get_integer_filter_condition(value: Union[dict, int], field):
    if isinstance(value, int):
        return field == value
    else:
        assert type(value) == dict

        condition = True
        if "min" in value:
            condition = condition & (field >= value["min"])
        if "max" in value:
            condition = condition & (field <= value["max"])
        if "equal" in value:
            condition = condition & (field == value["equal"])

        return condition


decimal_filter = {
    "oneOf": [
        {
            "type": "number",
        },
        {
            "type": "object",
            "properties": {
                "min": {
                    "type": "number",
                },
                "max": {
                    "type": "number",
                },
                "equal": {
                    "type": "number",
                },
            },
            "additionalProperties": False,
        }
    ],
}


def get_decimal_filter_condition(value: Union[dict, float], field):
    if isinstance(value, float):
        return field == value
    else:
        assert type(value) == dict

        condition = True
        if "min" in value:
            condition = condition & (field >= value["min"])
        if "max" in value:
            condition = condition & (field <= value["max"])
        if "equal" in value:
            condition = condition & (field == value["equal"])

        return condition


string_filter = {
    "oneOf": [
        {
            "type": "string",
        },
        {
            "type": "object",
            "properties": {
                "equal": {
                    "type": "string",
                },
                "like": {
                    "type": "string",
                },
            },
            "additionalProperties": False,
        }
    ],
}


def get_string_filter_condition(value: Union[dict, str], field):
    if isinstance(value, str):
        return field == value
    else:
        assert type(value) == dict

        condition = True
        if "equal" in value:
            condition = condition & (field == value["equal"])
        if "like" in value:
            condition = condition & (field % value["like"])

        return condition


date_filter = {
    "oneOf": [
        {
            "type": "string",
            "format": "date",
        },
        {
            "type": "object",
            "properties": {
                "excBefore": {
                    "type": "string",
                    "format": "date",
                },
                "incBefore": {
                    "type": "string",
                    "format": "date",
                },
                "excAfter": {
                    "type": "string",
                    "format": "date",
                },
                "incAfter": {
                    "type": "string",
                    "format": "date",
                },
                "at": {
                    "type": "string",
                    "format": "date",
                },
            },
            "additionalProperties": False,
        }
    ],
}


datetime_filter = {
    "oneOf": [
        {
            "type": "string",
            "format": "date-time",
        },
        {
            "type": "object",
            "properties": {
                "excBefore": {
                    "type": "string",
                    "format": "date-time",
                },
                "incBefore": {
                    "type": "string",
                    "format": "date-time",
                },
                "excAfter": {
                    "type": "string",
                    "format": "date-time",
                },
                "incAfter": {
                    "type": "string",
                    "format": "date-time",
                },
                "at": {
                    "type": "string",
                    "format": "date-time",
                },
            },
            "additionalProperties": False,
        }
    ],
}


def get_datetime_filter_condition(value: Union[dict, str], field):
    def to_datetime(s: str) -> datetime.datetime:
        return datetime.datetime.fromisoformat(s)

    if isinstance(value, str):
        return field == to_datetime(str)
    else:
        assert type(value) == dict

        condition = True
        if "excBefore" in value:
            condition = condition & (field < to_datetime(value["excBefore"]))
        if "incBefore" in value:
            condition = condition & (field <= to_datetime(value["incBefore"]))
        if "excAfter" in value:
            condition = condition & (field > to_datetime(value["excAfter"]))
        if "incAfter" in value:
            condition = condition & (field >= to_datetime(value["incAfter"]))
        if "at" in value:
            condition = condition & (field == to_datetime(value["at"]))

        return condition


foreign_key_filter = {
    "oneOf": [
        {
            "type": "integer",
        },
        {
            "type": "object",
        },
    ],
}


def get_foreign_key_filter_condition(value: Union[dict, int], field):
    if isinstance(value, int):
        return field == value
    else:
        assert type(value) == dict
        return get_filter_condition(value, field.rel_model)


field_handler_map = {
    BooleanField: get_bool_filter_condition,
    IntegerField: get_integer_filter_condition,
    DecimalField: get_decimal_filter_condition,
    CharField: get_string_filter_condition,
    FixedCharField: get_string_filter_condition,
    DateField: get_datetime_filter_condition,
    DateTimeField: get_datetime_filter_condition,
    ForeignKeyField: get_foreign_key_filter_condition,
}


def get_filter_condition(d: dict, model: type):
    condition = True
    for (key, value) in d.items():
        field = getattr(model, key)
        field_type = type(field)
        if field_type in field_handler_map:
            cond = field_handler_map[field_type](value, field)
        else:
            cond = (field == value)
        condition = condition & cond
    return condition
