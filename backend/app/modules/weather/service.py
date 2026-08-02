from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.notifications.enums import NotificationEventType
from app.modules.notifications.service import NotificationService
from app.modules.weather.enums import (
    WeatherAlertSeverity,
    WeatherAlertStatus,
    WeatherAlertType,
    WeatherLocationType,
    WeatherProvider,
)
from app.modules.weather.models import (
    WeatherAlert,
    WeatherAlertRule,
    WeatherForecast,
    WeatherLocation,
    WeatherSnapshot,
)
from app.modules.weather.providers.base import WeatherProviderClient, WeatherProviderLocation
from app.modules.weather.providers.mock_provider import MockWeatherProviderClient
from app.modules.weather.providers.openweather_provider import OpenWeatherProviderClient
from app.modules.geo.models import GeoCity, GeoProvince
from app.modules.weather.repository import WeatherRepository
from app.modules.weather.schemas import (
    WeatherAlertEvaluationOut,
    WeatherAlertOut,
    WeatherAlertRuleOut,
    WeatherForecastOut,
    WeatherGpsLocationIn,
    WeatherLocationCreateIn,
    WeatherLocationOut,
    WeatherProviderConfigOut,
    WeatherProviderConfigUpdateIn,
    WeatherSnapshotOut,
)


class WeatherService:
    CURRENT_WEATHER_TTL_MINUTES = 30
    FORECAST_TTL_MINUTES = 180

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = WeatherRepository(db)

    def seed_default_provider_configs(self) -> list[WeatherProviderConfigOut]:
        rows = [
            self.repo.upsert_provider_config(
                provider=WeatherProvider.MOCK.value,
                base_url=None,
                api_key_ref=None,
                is_active=True,
                priority=100,
                settings_json={"description": "Local mock weather provider"},
            ),
            self.repo.upsert_provider_config(
                provider=WeatherProvider.OPENWEATHER.value,
                base_url="https://api.openweathermap.org/data/2.5",
                api_key_ref="OPENWEATHER_API_KEY",
                is_active=False,
                priority=200,
                settings_json={"units": "metric"},
            ),
        ]

        self.repo.commit()

        return [WeatherProviderConfigOut.model_validate(row) for row in rows]

    def seed_default_alert_rules(self) -> list[WeatherAlertRuleOut]:
        defaults = [
            {
                "alert_type": WeatherAlertType.FROST.value,
                "severity": WeatherAlertSeverity.HIGH.value,
                "title_template": "هشدار سرمازدگی",
                "body_template": (
                    "دمای پیش‌بینی‌شده به {temperature_c} درجه رسیده است. "
                    "برای محافظت از محصولات حساس اقدام کنید."
                ),
                "rule_json": {"temperature_c_lte": 2},
            },
            {
                "alert_type": WeatherAlertType.HEAT.value,
                "severity": WeatherAlertSeverity.HIGH.value,
                "title_template": "هشدار گرمای شدید",
                "body_template": (
                    "دمای پیش‌بینی‌شده به {temperature_c} درجه رسیده است. "
                    "آبیاری و محافظت گرمایی را بررسی کنید."
                ),
                "rule_json": {"temperature_c_gte": 38},
            },
            {
                "alert_type": WeatherAlertType.HEAVY_RAIN.value,
                "severity": WeatherAlertSeverity.MEDIUM.value,
                "title_template": "هشدار بارش سنگین",
                "body_template": (
                    "بارش پیش‌بینی‌شده {precipitation_mm} میلی‌متر است. "
                    "زهکشی و برنامه عملیات مزرعه را بررسی کنید."
                ),
                "rule_json": {"precipitation_mm_gte": 20},
            },
            {
                "alert_type": WeatherAlertType.STRONG_WIND.value,
                "severity": WeatherAlertSeverity.MEDIUM.value,
                "title_template": "هشدار باد شدید",
                "body_template": (
                    "سرعت باد پیش‌بینی‌شده {wind_speed_mps} متر بر ثانیه است. "
                    "از سم‌پاشی یا عملیات حساس خودداری کنید."
                ),
                "rule_json": {"wind_speed_mps_gte": 12},
            },
            {
                "alert_type": WeatherAlertType.SPRAYING_NOT_RECOMMENDED.value,
                "severity": WeatherAlertSeverity.MEDIUM.value,
                "title_template": "سم‌پاشی توصیه نمی‌شود",
                "body_template": (
                    "به دلیل باد یا احتمال بارش، سم‌پاشی در این بازه توصیه نمی‌شود."
                ),
                "rule_json": {
                    "any": [
                        {"wind_speed_mps_gte": 8},
                        {"precipitation_probability_gte": 0.6},
                    ]
                },
            },
        ]

        rows: list[WeatherAlertRule] = []

        for item in defaults:
            row = self.repo.get_alert_rule_by_type(alert_type=item["alert_type"])

            if row is None:
                row = WeatherAlertRule(
                    alert_type=item["alert_type"],
                    severity=item["severity"],
                    title_template=item["title_template"],
                    body_template=item["body_template"],
                    rule_json=item["rule_json"],
                    is_active=True,
                )
                self.repo.add_alert_rule(row)
            else:
                row.severity = item["severity"]
                row.title_template = item["title_template"]
                row.body_template = item["body_template"]
                row.rule_json = item["rule_json"]
                row.is_active = True

            rows.append(row)

        self.repo.commit()

        for row in rows:
            self.repo.refresh(row)

        return [WeatherAlertRuleOut.model_validate(row) for row in rows]

    def list_alert_rules(self) -> list[WeatherAlertRuleOut]:
        rows = self.repo.list_alert_rules()

        return [WeatherAlertRuleOut.model_validate(row) for row in rows]

    def list_provider_configs(self) -> list[WeatherProviderConfigOut]:
        rows = self.repo.list_provider_configs()

        return [WeatherProviderConfigOut.model_validate(row) for row in rows]

    def update_provider_config(
        self,
        *,
        config_id: int,
        payload: WeatherProviderConfigUpdateIn,
    ) -> WeatherProviderConfigOut:
        row = self.repo.get_provider_config_by_id(config_id=config_id)

        if row is None:
            raise ValidationAuthError(
                message="Weather provider config not found",
                details={"config_id": config_id},
            )

        if payload.priority is not None and payload.priority < 1:
            raise ValidationAuthError(
                message="Invalid weather provider priority",
                details={"priority": payload.priority},
            )

        if payload.base_url is not None:
            row.base_url = payload.base_url

        if payload.api_key_ref is not None:
            row.api_key_ref = payload.api_key_ref

        if payload.is_active is not None:
            row.is_active = payload.is_active

        if payload.priority is not None:
            row.priority = payload.priority

        if payload.settings_json is not None:
            row.settings_json = payload.settings_json

        self.repo.commit()
        self.repo.refresh(row)

        return WeatherProviderConfigOut.model_validate(row)

    def create_location(
        self,
        *,
        payload: WeatherLocationCreateIn,
    ) -> WeatherLocationOut:
        self._validate_location_type(payload.location_type)
        self._validate_coordinates(payload.latitude, payload.longitude)

        existing = self.repo.find_location_by_coordinates(
            latitude=payload.latitude,
            longitude=payload.longitude,
        )

        if existing is not None:
            return WeatherLocationOut.model_validate(existing)

        row = WeatherLocation(
            country_code=payload.country_code.upper() if payload.country_code else None,
            province_id=payload.province_id,
            city_id=payload.city_id,
            village_id=payload.village_id,
            province_name=payload.province_name,
            city_name=payload.city_name,
            village_name=payload.village_name,
            display_name=payload.display_name,
            location_type=payload.location_type,
            latitude=payload.latitude,
            longitude=payload.longitude,
            timezone=payload.timezone,
            is_active=True,
        )

        self.repo.add_location(row)
        self.repo.commit()
        self.repo.refresh(row)

        return WeatherLocationOut.model_validate(row)

    def create_gps_location(
        self,
        *,
        payload: WeatherGpsLocationIn,
    ) -> WeatherLocationOut:
        base_name = payload.display_name or "Current location"
        display_name = base_name
        try:
            provider = self._provider(provider_override=None)
            place = provider.reverse_geocode(
                latitude=payload.latitude,
                longitude=payload.longitude,
                language="fa",
            )
            display_name = f"{base_name} — {place.name}"
        except (ValidationAuthError, NotImplementedError):
            pass

        existing = self.repo.find_nearby_gps_location(
            latitude=payload.latitude,
            longitude=payload.longitude,
        )
        if existing is not None:
            existing.display_name = display_name
            self.repo.commit()
            self.repo.refresh(existing)
            return WeatherLocationOut.model_validate(existing)

        return self.create_location(
            payload=WeatherLocationCreateIn(
                country_code=None,
                display_name=display_name,
                location_type=WeatherLocationType.GPS.value,
                latitude=payload.latitude,
                longitude=payload.longitude,
                timezone=payload.timezone,
            )
        )

    def create_geo_location(self, *, province_id: int, city_id: int) -> WeatherLocationOut:
        city = self.db.query(GeoCity).filter(
            GeoCity.id == city_id,
            GeoCity.province_id == province_id,
            GeoCity.is_active == True,  # noqa: E712
        ).one_or_none()
        province = self.db.query(GeoProvince).filter(
            GeoProvince.id == province_id,
            GeoProvince.is_active == True,  # noqa: E712
        ).one_or_none()
        if city is None or province is None:
            raise ValidationAuthError(message="Selected province or city is invalid")
        provider = self._provider(provider_override=None)
        if not isinstance(provider, OpenWeatherProviderClient):
            raise ValidationAuthError(message="Active weather provider does not support geocoding")
        latitude, longitude = provider.geocode(query=f"{city.name}, {province.name}")
        return self.create_location(
            payload=WeatherLocationCreateIn(
                country_code="IR",
                province_id=province.id,
                city_id=city.id,
                province_name=province.name,
                city_name=city.name,
                display_name=f"{city.name}، {province.name}",
                location_type=WeatherLocationType.CITY.value,
                latitude=latitude,
                longitude=longitude,
                timezone="Asia/Tehran",
            )
        )

    def list_locations(
        self,
        *,
        q: str | None,
        country_code: str | None,
        location_type: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[WeatherLocationOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if location_type is not None:
            self._validate_location_type(location_type)

        rows, total = self.repo.list_locations_paginated(
            q=q,
            country_code=country_code,
            location_type=location_type,
            page=page,
            page_size=page_size,
        )

        return [WeatherLocationOut.model_validate(row) for row in rows], total

    def get_location_admin(
        self,
        *,
        location_id: int,
    ) -> WeatherLocationOut:
        row = self.repo.get_location_any_status(location_id=location_id)

        if row is None:
            raise ValidationAuthError(
                message="Weather location not found",
                details={"location_id": location_id},
            )

        return WeatherLocationOut.model_validate(row)

    def refresh_location_weather(
        self,
        *,
        location_id: int,
        provider_override: str | None = None,
    ) -> tuple[WeatherSnapshotOut, list[WeatherForecastOut]]:
        location = self.repo.get_location_by_id(location_id=location_id)

        if location is None:
            raise ValidationAuthError(
                message="Weather location not found",
                details={"location_id": location_id},
            )

        provider = self._provider(provider_override=provider_override)

        provider_location = WeatherProviderLocation(
            latitude=location.latitude,
            longitude=location.longitude,
            display_name=location.display_name,
        )

        current = provider.get_current(location=provider_location)
        forecasts = provider.get_forecast(location=provider_location)

        snapshot = WeatherSnapshot(
            location_id=location.id,
            provider=current.provider,
            temperature_c=current.temperature_c,
            feels_like_c=current.feels_like_c,
            humidity_percent=current.humidity_percent,
            wind_speed_mps=current.wind_speed_mps,
            wind_direction_deg=current.wind_direction_deg,
            pressure_hpa=current.pressure_hpa,
            condition_code=current.condition_code,
            condition_text=current.condition_text,
            raw_json=current.raw_json,
            observed_at=current.observed_at,
        )

        self.repo.add_snapshot(snapshot)

        self.repo.delete_forecasts_for_provider(
            location_id=location.id,
            provider=current.provider,
        )

        forecast_rows: list[WeatherForecast] = []

        for item in forecasts:
            forecast = WeatherForecast(
                location_id=location.id,
                provider=item.provider,
                forecast_type=item.forecast_type,
                forecast_time=item.forecast_time,
                temperature_c=item.temperature_c,
                min_temperature_c=item.min_temperature_c,
                max_temperature_c=item.max_temperature_c,
                humidity_percent=item.humidity_percent,
                precipitation_mm=item.precipitation_mm,
                precipitation_probability=item.precipitation_probability,
                wind_speed_mps=item.wind_speed_mps,
                condition_code=item.condition_code,
                condition_text=item.condition_text,
                raw_json=item.raw_json,
            )
            self.repo.add_forecast(forecast)
            forecast_rows.append(forecast)

        self.repo.commit()
        self.repo.refresh(snapshot)

        for row in forecast_rows:
            self.repo.refresh(row)

        return (
            WeatherSnapshotOut.model_validate(snapshot),
            [WeatherForecastOut.model_validate(row) for row in forecast_rows],
        )

    def is_current_weather_stale(
        self,
        *,
        location_id: int,
        ttl_minutes: int | None = None,
    ) -> bool:
        row = self.repo.latest_snapshot(location_id=location_id)

        if row is None:
            return True

        ttl = ttl_minutes or self.CURRENT_WEATHER_TTL_MINUTES
        cutoff = datetime.utcnow() - timedelta(minutes=ttl)

        return row.observed_at.replace(tzinfo=None) < cutoff

    def is_forecast_stale(
        self,
        *,
        location_id: int,
        forecast_type: str | None = None,
        ttl_minutes: int | None = None,
    ) -> bool:
        latest_created_at = self.repo.latest_forecast_created_at(
            location_id=location_id,
            forecast_type=forecast_type,
        )

        if latest_created_at is None:
            return True

        ttl = ttl_minutes or self.FORECAST_TTL_MINUTES
        cutoff = datetime.utcnow() - timedelta(minutes=ttl)

        return latest_created_at.replace(tzinfo=None) < cutoff

    def is_weather_cache_stale(
        self,
        *,
        location_id: int,
    ) -> bool:
        return self.is_current_weather_stale(
            location_id=location_id
        ) or self.is_forecast_stale(location_id=location_id)

    def refresh_location_weather_if_stale(
        self,
        *,
        location_id: int,
        provider_override: str | None = None,
        force: bool = False,
    ) -> tuple[WeatherSnapshotOut | None, list[WeatherForecastOut], bool]:
        location = self.repo.get_location_by_id(location_id=location_id)

        if location is None:
            raise ValidationAuthError(
                message="Weather location not found",
                details={"location_id": location_id},
            )

        if force or self.is_weather_cache_stale(location_id=location_id):
            snapshot, forecasts = self.refresh_location_weather(
                location_id=location_id,
                provider_override=provider_override,
            )
            return snapshot, forecasts, True

        snapshot = self.latest_snapshot(location_id=location_id)
        forecasts = self.list_forecasts(location_id=location_id)

        return snapshot, forecasts, False

    def latest_snapshot(
        self,
        *,
        location_id: int,
    ) -> WeatherSnapshotOut | None:
        row = self.repo.latest_snapshot(location_id=location_id)

        if row is None:
            return None

        return WeatherSnapshotOut.model_validate(row)

    def current_weather(
        self,
        *,
        location_id: int,
    ) -> WeatherSnapshotOut | None:
        location = self.repo.get_location_by_id(location_id=location_id)

        if location is None:
            raise ValidationAuthError(
                message="Weather location not found",
                details={"location_id": location_id},
            )

        return self.latest_snapshot(location_id=location_id)

    def list_forecasts(
        self,
        *,
        location_id: int,
        forecast_type: str | None = None,
    ) -> list[WeatherForecastOut]:
        rows = self.repo.list_forecasts(
            location_id=location_id,
            forecast_type=forecast_type,
        )

        return [WeatherForecastOut.model_validate(row) for row in rows]

    def forecast(
        self,
        *,
        location_id: int,
        forecast_type: str | None,
    ) -> list[WeatherForecastOut]:
        location = self.repo.get_location_by_id(location_id=location_id)

        if location is None:
            raise ValidationAuthError(
                message="Weather location not found",
                details={"location_id": location_id},
            )

        return self.list_forecasts(
            location_id=location_id,
            forecast_type=forecast_type,
        )

    def active_alerts(
        self,
        *,
        location_id: int,
    ) -> list[WeatherAlertOut]:
        location = self.repo.get_location_by_id(location_id=location_id)

        if location is None:
            raise ValidationAuthError(
                message="Weather location not found",
                details={"location_id": location_id},
            )

        rows = self.repo.list_active_alerts(location_id=location_id)

        return [WeatherAlertOut.model_validate(row) for row in rows]

    def list_admin_alerts(
        self,
        *,
        location_id: int | None,
        alert_type: str | None,
        status: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[WeatherAlertOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        if alert_type is not None:
            self._validate_alert_type(alert_type)

        if status is not None:
            self._validate_alert_status(status)

        rows, total = self.repo.list_admin_alerts(
            location_id=location_id,
            alert_type=alert_type,
            status=status,
            page=page,
            page_size=page_size,
        )

        return [WeatherAlertOut.model_validate(row) for row in rows], total

    def evaluate_alert_rules_for_location(
        self,
        *,
        location_id: int,
    ) -> WeatherAlertEvaluationOut:
        location = self.repo.get_location_by_id(location_id=location_id)

        if location is None:
            raise ValidationAuthError(
                message="Weather location not found",
                details={"location_id": location_id},
            )

        rules = self.repo.list_active_alert_rules()
        forecasts = self.repo.list_forecasts(location_id=location_id, limit=120)

        created = 0
        skipped = 0

        for rule in rules:
            for forecast in forecasts:
                if not self._rule_matches_forecast(rule.rule_json, forecast):
                    continue

                existing = self.repo.find_duplicate_active_alert(
                    location_id=location_id,
                    rule_id=rule.id,
                    alert_type=rule.alert_type,
                    starts_at=forecast.forecast_time,
                )

                if existing is not None:
                    skipped += 1
                    continue

                alert = WeatherAlert(
                    location_id=location_id,
                    rule_id=rule.id,
                    alert_type=rule.alert_type,
                    severity=rule.severity,
                    status=WeatherAlertStatus.ACTIVE.value,
                    title=rule.title_template,
                    body=self._render_alert_body(
                        template=rule.body_template,
                        forecast=forecast,
                    ),
                    starts_at=forecast.forecast_time,
                    ends_at=None,
                    is_active=True,
                    payload_json={
                        "forecast_id": forecast.id,
                        "forecast_time": forecast.forecast_time.isoformat(),
                        "rule_json": rule.rule_json,
                        "temperature_c": self._decimal_to_str(forecast.temperature_c),
                        "precipitation_mm": self._decimal_to_str(
                            forecast.precipitation_mm
                        ),
                        "precipitation_probability": self._decimal_to_str(
                            forecast.precipitation_probability
                        ),
                        "wind_speed_mps": self._decimal_to_str(
                            forecast.wind_speed_mps
                        ),
                    },
                )

                self.repo.add_alert(alert)

                self._notify_admins_for_weather_alert(
                    alert=alert,
                    location=location,
                )

                created += 1

        self.repo.commit()

        return WeatherAlertEvaluationOut(
            location_id=location_id,
            evaluated_rules=len(rules),
            created_alerts=created,
            skipped_duplicates=skipped,
        )

    def _notify_admins_for_weather_alert(
        self,
        *,
        alert: WeatherAlert,
        location: WeatherLocation,
    ) -> None:
        recipient_ids = self.repo.list_weather_admin_recipient_user_ids()

        if not recipient_ids:
            return

        NotificationService(self.db).create_event_and_notify_many(
            event_type=NotificationEventType.WEATHER_ALERT_CREATED.value,
            recipient_user_ids=recipient_ids,
            title=f"هشدار آب‌وهوا: {alert.title}",
            body=f"{location.display_name}: {alert.body}",
            actor_user_id=None,
            source_type="weather_alert",
            source_id=str(alert.id),
            payload_json={
                "weather_alert_id": alert.id,
                "location_id": alert.location_id,
                "location_name": location.display_name,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "starts_at": alert.starts_at.isoformat(),
            },
            action_url=f"/weather/alerts?location_id={alert.location_id}",
            priority=(
                "high" if alert.severity in {"high", "critical"} else "normal"
            ),
            commit=False,
        )

    def _rule_matches_forecast(
        self,
        rule_json: dict,
        forecast: WeatherForecast,
    ) -> bool:
        if "any" in rule_json:
            return any(
                self._rule_matches_forecast(item, forecast)
                for item in rule_json["any"]
            )

        if "all" in rule_json:
            return all(
                self._rule_matches_forecast(item, forecast)
                for item in rule_json["all"]
            )

        for key, threshold in rule_json.items():
            value = self._forecast_metric(forecast, key)

            if value is None:
                return False

            if key.endswith("_lte"):
                if value > Decimal(str(threshold)):
                    return False

            elif key.endswith("_gte"):
                if value < Decimal(str(threshold)):
                    return False

            else:
                raise ValidationAuthError(
                    message="Unsupported weather alert rule operator",
                    details={"operator": key},
                )

        return True

    def _forecast_metric(
        self,
        forecast: WeatherForecast,
        key: str,
    ) -> Decimal | None:
        metric_name = key.removesuffix("_lte").removesuffix("_gte")

        value = getattr(forecast, metric_name, None)

        if value is None:
            return None

        return Decimal(str(value))

    def _render_alert_body(
        self,
        *,
        template: str,
        forecast: WeatherForecast,
    ) -> str:
        values = {
            "temperature_c": self._decimal_to_str(forecast.temperature_c) or "-",
            "min_temperature_c": self._decimal_to_str(
                forecast.min_temperature_c
            )
            or "-",
            "max_temperature_c": self._decimal_to_str(
                forecast.max_temperature_c
            )
            or "-",
            "humidity_percent": self._decimal_to_str(forecast.humidity_percent)
            or "-",
            "precipitation_mm": self._decimal_to_str(forecast.precipitation_mm)
            or "-",
            "precipitation_probability": self._decimal_to_str(
                forecast.precipitation_probability
            )
            or "-",
            "wind_speed_mps": self._decimal_to_str(forecast.wind_speed_mps) or "-",
        }

        try:
            return template.format(**values)
        except Exception:
            return template

    def _decimal_to_str(self, value: object) -> str | None:
        if value is None:
            return None

        return str(value)

    def _provider(
        self,
        *,
        provider_override: str | None,
    ) -> WeatherProviderClient:
        if provider_override:
            provider_name = provider_override
            config = None
        else:
            config = self.repo.get_active_provider_config()
            provider_name = config.provider if config else WeatherProvider.MOCK.value

        if provider_name == WeatherProvider.MOCK.value:
            return MockWeatherProviderClient()

        if provider_name == WeatherProvider.OPENWEATHER.value:
            base_url = (
                config.base_url
                if config and config.base_url
                else "https://api.openweathermap.org/data/2.5"
            )
            api_key_ref = (
                config.api_key_ref if config and config.api_key_ref else "OPENWEATHER_API_KEY"
            )

            return OpenWeatherProviderClient(
                base_url=base_url,
                api_key_ref=api_key_ref,
            )

        raise ValidationAuthError(
            message="Unsupported weather provider",
            details={"provider": provider_name},
        )

    def _validate_location_type(self, location_type: str) -> None:
        allowed = {item.value for item in WeatherLocationType}

        if location_type not in allowed:
            raise ValidationAuthError(
                message="Invalid weather location type",
                details={"allowed": sorted(allowed)},
            )

    def _validate_coordinates(
        self,
        latitude: Decimal,
        longitude: Decimal,
    ) -> None:
        if latitude < Decimal("-90") or latitude > Decimal("90"):
            raise ValidationAuthError(
                message="Invalid latitude",
                details={"latitude": str(latitude)},
            )

        if longitude < Decimal("-180") or longitude > Decimal("180"):
            raise ValidationAuthError(
                message="Invalid longitude",
                details={"longitude": str(longitude)},
            )

    def _validate_alert_type(self, alert_type: str) -> None:
        allowed = {item.value for item in WeatherAlertType}

        if alert_type not in allowed:
            raise ValidationAuthError(
                message="Invalid weather alert type",
                details={"allowed": sorted(allowed)},
            )

    def _validate_alert_status(self, status: str) -> None:
        allowed = {item.value for item in WeatherAlertStatus}

        if status not in allowed:
            raise ValidationAuthError(
                message="Invalid weather alert status",
                details={"allowed": sorted(allowed)},
            )
