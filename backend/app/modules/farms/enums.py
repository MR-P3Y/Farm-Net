from enum import Enum


class FarmStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
