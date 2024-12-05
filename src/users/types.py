# External imports
from enum import Enum

class UserRoles(Enum):
    USER = "user"
    ADMIN = "admin"
    SYSTEM = "system" # System accounts cannot login (contains accounts like 'Anonymous')
    BOT = "bot" # Just informational for the users

class UserStatuses(Enum):
    NORMAL = "normal"
    BANNED = "banned" # User cannot login
    DELETED = "deleted" # Alongside setting 'deleted_at' in the database
    MUTED = "muted" # User cannot create new uploads or engage in comments