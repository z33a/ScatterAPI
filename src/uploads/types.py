# External imports
from enum import Enum

class UploadTypes(Enum):
    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"

class OrderByTypes(Enum):
    TITLE = "title"
    ID = "id"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"

class OrderByDirectionTypes(Enum):
    ASC = "asc"
    DESC = "desc"