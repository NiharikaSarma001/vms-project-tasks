from enum import Enum

class FileFormat(str, Enum):
    csv = "csv"
    xlsx = "xlsx"
    json = "json"