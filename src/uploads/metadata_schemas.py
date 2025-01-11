# External imports
from enum import Enum

# Enum to define different schema types
class MetadataTypes(str, Enum):
    REDDIT = "reddit"
    NHENTAI = "nhentai"
    OTHER = "other"

reddit_schema = {
    "type": "object",
    "properties": {
        "author": {"type": ["string", "null"]},
        "author_flair_text": {"type": ["string", "null"]},
        "created_utc": {"type": "number"},
        "distinguished": {"type": ["string", "null"]},
        "edited": {"type": ["number", "null"]},
        "id": {"type": "string"},
        "is_original_content": {"type": "boolean"},
        "is_self": {"type": "boolean"},
        "link_flair_template_id": {"type": ["string", "null"]},
        "link_flair_text": {"type": ["string", "null"]},
        "locked": {"type": "boolean"},
        "name": {"type": "string"},
        "num_comments": {"type": "integer"},
        "over_18": {"type": "boolean"},
        "permalink": {"type": "string"},
        "score": {"type": "integer"},
        "selftext": {"type": ["string", "null"]},
        "spoiler": {"type": "boolean"},
        "stickied": {"type": "boolean"},
        "subreddit": {"type": "string"},
        "title": {"type": "string"},
        "upvote_ratio": {"type": "number"},
        "url": {"type": "string"}
    },
    "required": [
        "created_utc", "id", "is_original_content", "is_self", "locked",
        "name", "num_comments", "over_18", "permalink", "score", "spoiler",
        "stickied", "subreddit", "title", "upvote_ratio", "url"
    ]
}

nhentai_schema = {
    "type": "object",
    "properties": {
        "title1": {
            "type": "object",
            "properties": {
                "before": {"type": ["string", "null"]},
                "pretty": {"type": "string"},
                "after": {"type": ["string", "null"]}
            },
            "required": ["pretty"]
        },
        "title2": {
            "type": "object",
            "properties": {
                "before": {"type": ["string", "null"]},
                "pretty": {"type": ["string", "null"]},
                "after": {"type": ["string", "null"]}
            },
        },
        "id": {"type": "string"},
        "parodies": {
            "type": "array",
            "items": {"type": ["string", "null"]}
        },
        "characters": {
            "type": "array",
            "items": {"type": ["string", "null"]}
        },
        "tags": {
            "type": "array",
            "items": {"type": "string"}
        },
        "artists": {
            "type": "array",
            "items": {"type": "string"}
        },
        "groups": {
            "type": "array",
            "items": {"type": ["string", "null"]}
        },
        "languages": {
            "type": "array",
            "items": {"type": "string"}
        },
        "categories": {
            "type": "array",
            "items": {"type": "string"}
        },
        "pages": {"type": "integer"},
        "uploaded": {"type": "number"}
    },
    "required": [
        "title1", "title2", "id", "parodies", "characters", "tags", 
        "artists", "groups", "languages", "categories", "pages", "uploaded"
    ]
}

# A dictionary mapping metadata types to json schemas (SQLModel/PyDantic models)
metadata_schemas = {
    MetadataTypes.REDDIT: reddit_schema,
    MetadataTypes.NHENTAI: nhentai_schema
}