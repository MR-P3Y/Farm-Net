from datetime import datetime

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.modules.auth.models import AuthUser
from app.modules.farms.models import FarmPlotWeatherLink
from app.modules.farms.repository import FarmRepository
from app.modules.farms.schemas import (
    FarmWeatherAlertOut,
    FarmWeatherContextOut,
    FarmWeatherForecastOut,
    FarmWeatherSnapshotOut,
)
from app.modules.farms.service import FarmPlotService, FarmService
from app.modules.notifications.enums import NotificationEventType
from app.modules.notifications.service import NotificationService
from app.modules.weather.enums import WeatherAlertStatus
from app.modules.weather.models import (
    WeatherAlert,
    WeatherForecast,
    WeatherLocation,
    WeatherSnapshot,
)
from app.modules.weather.providers.base import WeatherProviderLocation
from app.modules.weather.service import WeatherService


class FarmWeatherService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.farm_repo = FarmRepository(db)
        self.plot_service = FarmPlotService(db)
        self.plot_service.repo = self.farm_repo
        self.weather = WeatherService(db)

    def context(
        self, *, user: AuthUser, farm_id: int, plot_id: int, force: bool = False
    ) -> FarmWeatherContextOut:
        location, coordinate_changed = self._location(
            user=user, farm_id=farm_id, plot_id=plot_id
        )
        refreshed = force or coordinate_changed or self.weather.is_weather_cache_stale(
            location_id=location.id
        )
        if refreshed:
            self._refresh(location)
            self._evaluate_alerts(location=location, owner_user_id=user.id)
        return FarmWeatherContextOut(
            farm_id=farm_id,
            plot_id=plot_id,
            snapshot=self._snapshot(location.id),
            forecasts=self._forecasts(location.id),
            alerts=self._alerts(location.id),
            refreshed=refreshed,
        )

    def alerts(
        self, *, user: AuthUser, farm_id: int, plot_id: int
    ) -> list[FarmWeatherAlertOut]:
        location, _ = self._location(user=user, farm_id=farm_id, plot_id=plot_id)
        return self._alerts(location.id)

    def _location(self, *, user, farm_id, plot_id) -> tuple[WeatherLocation, bool]:
        farm = self.plot_service._farm_for_update(user.id, farm_id)
        FarmService._require_active(farm)
        plot = self.plot_service._plot(user.id, farm_id, plot_id, True)
        FarmService._require_active(plot)
        if plot.latitude is None or plot.longitude is None:
            raise AppException(
                "FARM_WEATHER_COORDINATES_REQUIRED",
                "Plot latitude and longitude are required for contextual weather",
                422,
            )
        link = self.db.query(FarmPlotWeatherLink).filter(
            FarmPlotWeatherLink.plot_id == plot.id
        ).one_or_none()
        if link is None:
            location = WeatherLocation(
                owner_user_id=user.id,
                visibility="private",
                country_code="IR",
                province_id=plot.province_id,
                city_id=plot.city_id,
                village_id=plot.village_id,
                display_name="Private farm weather context",
                location_type="gps",
                latitude=plot.latitude,
                longitude=plot.longitude,
                timezone="Asia/Tehran",
                is_active=True,
            )
            self.db.add(location)
            self.db.flush()
            link = FarmPlotWeatherLink(
                plot_id=plot.id, weather_location_id=location.id
            )
            self.db.add(link)
            self.db.flush()
            self.farm_repo.add_audit(
                farm_id=farm_id, actor_user_id=user.id,
                action="weather.linked", target_type="plot", target_id=plot.id,
            )
            self.db.commit()
            self.db.refresh(location)
            return location, True
        location = self.weather.repo.get_location_by_id(
            location_id=link.weather_location_id, owner_user_id=user.id
        )
        if location is None:
            raise AppException(
                "FARM_WEATHER_LINK_INVALID", "Private Farm weather link is unavailable", 409
            )
        changed = (
            location.latitude != plot.latitude or location.longitude != plot.longitude
        )
        if changed:
            location.latitude = plot.latitude
            location.longitude = plot.longitude
            location.province_id = plot.province_id
            location.city_id = plot.city_id
            location.village_id = plot.village_id
            self.farm_repo.add_audit(
                farm_id=farm_id, actor_user_id=user.id,
                action="weather.location_synced", target_type="plot", target_id=plot.id,
            )
            self.db.commit()
            self.db.refresh(location)
        return location, changed

    def _refresh(self, location: WeatherLocation) -> None:
        provider = self.weather._provider(provider_override=None)
        provider_location = WeatherProviderLocation(
            latitude=location.latitude,
            longitude=location.longitude,
            display_name="Private farm weather context",
        )
        current = provider.get_current(location=provider_location)
        forecasts = provider.get_forecast(location=provider_location)
        snapshot = WeatherSnapshot(
            location_id=location.id, provider=current.provider,
            temperature_c=current.temperature_c, feels_like_c=current.feels_like_c,
            humidity_percent=current.humidity_percent,
            wind_speed_mps=current.wind_speed_mps,
            wind_direction_deg=current.wind_direction_deg,
            pressure_hpa=current.pressure_hpa,
            condition_code=current.condition_code,
            condition_text=current.condition_text,
            raw_json=current.raw_json, observed_at=current.observed_at,
        )
        self.weather.repo.add_snapshot(snapshot)
        self.weather.repo.delete_forecasts_for_provider(
            location_id=location.id, provider=current.provider
        )
        for item in forecasts:
            self.weather.repo.add_forecast(WeatherForecast(
                location_id=location.id, provider=item.provider,
                forecast_type=item.forecast_type, forecast_time=item.forecast_time,
                temperature_c=item.temperature_c,
                min_temperature_c=item.min_temperature_c,
                max_temperature_c=item.max_temperature_c,
                humidity_percent=item.humidity_percent,
                precipitation_mm=item.precipitation_mm,
                precipitation_probability=item.precipitation_probability,
                wind_speed_mps=item.wind_speed_mps,
                condition_code=item.condition_code,
                condition_text=item.condition_text, raw_json=item.raw_json,
            ))
        self.db.commit()

    def _evaluate_alerts(self, *, location: WeatherLocation, owner_user_id: int) -> None:
        for rule in self.weather.repo.list_active_alert_rules():
            for forecast in self.weather.repo.list_forecasts(
                location_id=location.id, limit=120
            ):
                if not self.weather._rule_matches_forecast(rule.rule_json, forecast):
                    continue
                duplicate = self.weather.repo.find_duplicate_active_alert(
                    location_id=location.id, rule_id=rule.id,
                    alert_type=rule.alert_type, starts_at=forecast.forecast_time,
                )
                if duplicate is not None:
                    continue
                alert = WeatherAlert(
                    location_id=location.id, rule_id=rule.id,
                    alert_type=rule.alert_type, severity=rule.severity,
                    status=WeatherAlertStatus.ACTIVE.value,
                    title=rule.title_template,
                    body=self.weather._render_alert_body(
                        template=rule.body_template, forecast=forecast
                    ),
                    starts_at=forecast.forecast_time, ends_at=None,
                    is_active=True,
                    payload_json={"forecast_time": forecast.forecast_time.isoformat()},
                )
                self.weather.repo.add_alert(alert)
                NotificationService(self.db).create_event_and_notify_many(
                    event_type=NotificationEventType.WEATHER_ALERT_CREATED.value,
                    recipient_user_ids=[owner_user_id],
                    title=alert.title, body=alert.body, actor_user_id=None,
                    source_type="farm_weather_alert", source_id=str(alert.id),
                    payload_json={
                        "farm_weather_alert_id": alert.id,
                        "alert_type": alert.alert_type,
                        "severity": alert.severity,
                    },
                    action_url="/my-activity/farms",
                    priority="high" if alert.severity in {"high", "critical"} else "normal",
                    commit=False,
                )
        self.db.commit()

    def _snapshot(self, location_id: int):
        row = self.weather.repo.latest_snapshot(location_id=location_id)
        if row is None:
            return None
        return FarmWeatherSnapshotOut.model_validate(row, from_attributes=True)

    def _forecasts(self, location_id: int):
        return [
            FarmWeatherForecastOut.model_validate(row, from_attributes=True)
            for row in self.weather.repo.list_forecasts(location_id=location_id)
        ]

    def _alerts(self, location_id: int):
        now = datetime.utcnow()
        rows = self.weather.repo.list_active_alerts(location_id=location_id)
        return [
            FarmWeatherAlertOut.model_validate(row, from_attributes=True)
            for row in rows
            if row.ends_at is None or row.ends_at.replace(tzinfo=None) >= now
        ]
