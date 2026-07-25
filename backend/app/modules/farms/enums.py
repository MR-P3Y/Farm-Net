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


class SoilTexture(str, Enum):
    SANDY = "sandy"
    LOAMY = "loamy"
    CLAY = "clay"
    SILTY = "silty"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class WaterSourceType(str, Enum):
    WELL = "well"
    SPRING = "spring"
    RIVER = "river"
    CANAL = "canal"
    RESERVOIR = "reservoir"
    MUNICIPAL = "municipal"
    OTHER = "other"


class IrrigationMethod(str, Enum):
    SURFACE = "surface"
    DRIP = "drip"
    SPRINKLER = "sprinkler"
    SUBSURFACE = "subsurface"
    RAINFED = "rainfed"
    OTHER = "other"


class LabSubjectType(str, Enum):
    SOIL = "soil"
    WATER = "water"


class LabMetric(str, Enum):
    PH = "ph"
    ELECTRICAL_CONDUCTIVITY = "electrical_conductivity"
    ORGANIC_MATTER = "organic_matter"
    NITROGEN = "nitrogen"
    PHOSPHORUS = "phosphorus"
    POTASSIUM = "potassium"
    TDS = "tds"
    SAR = "sar"


class FarmOperationType(str, Enum):
    LAND_PREPARATION = "land_preparation"
    PLANTING = "planting"
    IRRIGATION = "irrigation"
    FERTILIZING = "fertilizing"
    SPRAYING = "spraying"
    WEEDING = "weeding"
    PRUNING = "pruning"
    MONITORING = "monitoring"
    OTHER = "other"


class FarmRecordSubjectType(str, Enum):
    CYCLE = "cycle"
    OPERATION = "operation"
    HARVEST = "harvest"
