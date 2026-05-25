from enum import Enum


class WeatherLocationType(str, Enum):
    PROVINCE = "province"
    CITY = "city"
    VILLAGE = "village"
    GPS = "gps"


class WeatherProvider(str, Enum):
    MOCK = "mock"
    OPENWEATHER = "openweather"


class WeatherForecastType(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"


class WeatherAlertType(str, Enum):
    FROST = "frost"
    HEAT = "heat"
    HEAVY_RAIN = "heavy_rain"
    STRONG_WIND = "strong_wind"
    DROUGHT = "drought"
    HAIL = "hail"
    SPRAYING_NOT_RECOMMENDED = "spraying_not_recommended"


class WeatherAlertSeverity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WeatherAlertStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    EXPIRED = "expired"
    DISABLED = "disabled"
