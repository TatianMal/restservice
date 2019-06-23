from collections import OrderedDict
import json
import datetime

from db import VALIDATED_CURRENCIES, VALIDATED_COUNTRIES


def create_dict(fields, data, one_rec=False):
    headers = [str(field).split(".")[1] for field in fields]
    result = []
    for row in data:
        row = row.values()
        record = OrderedDict(zip(headers, row))
        if one_rec:
            return record
        result.append(record)
    return result


def encode(data):
    return json.dumps(data, indent=4, default=date_converter).encode('utf-8')


def date_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def check_params(table_fields, params):
    headers = [str(field).split(".")[1] for field in table_fields if str(field).split(".")[1] != "id"]
    result = {"validated": False, "code": 400, "errors": []}

    if len(headers) != len(params.keys()):
        result["errors"].append("Not enough count of parameters")
        return result
    if not all([key in headers for key in params.keys()]):
        result["errors"].append("Invalid parameters")
        return result
    else:
        for key, value in params.items():
            if key == "country":
                if value not in VALIDATED_COUNTRIES:
                    result["errors"].append("Invalid value in {} field.".format(key))
                continue
            elif key == "currency":
                if value not in VALIDATED_CURRENCIES:
                    result["errors"].append("Invalid value in {} field".format(key))
                continue
            elif key == "date_transfer":
                try:
                    datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                except ValueError as exc:
                    result["errors"].append("Invalid value in {} field. Valid format: yyyy-mm-dd hh:mm:ss".format(key))
                continue
            elif type(value) != int:
                result["errors"].append("Invalid value in {} field. Valid type: int".format(key))

        if result["errors"]:
            result["code"] = 422
            return result

        result["validated"] = True
        return result
