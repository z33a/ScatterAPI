# External imports
from sqlmodel import SQLModel
from enum import Enum

# Enum to define different schema types
class MetadataType(str, Enum):
    REDDIT = "reddit"
    RULE34 = "rule34"
    OTHER = "other"

# Define Pydantic models for valid JSON data
class RedditSchema(SQLModel):
    author: str | None
    author_flair_text: str | None
    created_utc: float
    distinguished: str | None
    edited: float | None
    id: str
    is_original_content: bool
    is_self: bool
    link_flair_template_id: str | None
    link_flair_text: str | None
    locked: bool
    name: str
    num_comments: int
    over_18: bool
    permalink: str
    score: int
    selftext: str | None
    spoiler: bool
    stickied: bool
    subreddit: str
    title: str
    upvote_ratio: float
    url: str

class Rule34Schema(SQLModel): # Just a placeholder
    title: str
    description: str
    likes: int

# A dictionary mapping metadata types to json schemas (SQLModel/PyDantic models)
metadata_schemas = {
    MetadataType.REDDIT: RedditSchema,
    MetadataType.RULE34: Rule34Schema
}