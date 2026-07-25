from enum import Enum


class FarmStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class CropCycleStatus(str, Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CultivationMode(str, Enum):
    SINGLE = "single"
    INTERCROP = "intercrop"
