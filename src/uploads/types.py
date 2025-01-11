# External imports
from enum import Enum

# Internal imports
from uploads.metadata_models import MetadataTypes

class OrderByTypes(Enum):
    TITLE = "title"
    ID = "id"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"

class OrderByDirectionTypes(Enum):
    ASC = "asc"
    DESC = "desc"

class OrderByReddit(Enum):
    CREATED_UTC = "created_utc"
    TITLE_METADATA = "title_metadata"

order_by_metadata = {
    MetadataTypes.REDDIT: OrderByReddit
}