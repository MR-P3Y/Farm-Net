from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.modules.weather.models import (
    WeatherAlert,
    WeatherAlertRule,
    WeatherForecast,
    WeatherLocation,
    WeatherProviderConfig,
    WeatherSnapshot,
)


class WeatherRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, row: object) -> None:
        self.db.refresh(row)

    def add_location(self, row: WeatherLocation) -> WeatherLocation:
        self.db.add(row)
        self.db.flush()
        return row

    def get_location_by_id(self, *, location_id: int) -> WeatherLocation | None:
        return (
            self.db.query(WeatherLocation)
            .filter(
                WeatherLocation.id == location_id,
                WeatherLocation.is_active == True,  # noqa: E712
            )
            .one_or_none()
        )

    def get_location_any_status(
        self,
        *,
        location_id: int,
    ) -> WeatherLocation | None:
        return (
            self.db.query(WeatherLocation)
            .filter(WeatherLocation.id == location_id)
            .one_or_none()
        )

    def list_locations(self, *, limit: int = 100) -> list[WeatherLocation]:
        return (
            self.db.query(WeatherLocation)
            .filter(WeatherLocation.is_active == True)  # noqa: E712
            .order_by(WeatherLocation.id.desc())
            .limit(limit)
            .all()
        )

    def list_locations_paginated(
        self,
        *,
        q: str | None = None,
        country_code: str | None = None,
        location_type: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[WeatherLocation], int]:
        query = self.db.query(WeatherLocation).filter(
            WeatherLocation.is_active == True  # noqa: E712
        )

        if q:
            like = f"%{q}%"
            query = query.filter(WeatherLocation.display_name.like(like))

        if country_code:
            query = query.filter(WeatherLocation.country_code == country_code.upper())

        if location_type:
            query = query.filter(WeatherLocation.location_type == location_type)

        total = query.count()

        rows = (
            query.order_by(WeatherLocation.display_name.asc(), WeatherLocation.id.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return rows, total

    def find_location_by_coordinates(
        self,
        *,
        latitude: Decimal,
        longitude: Decimal,
    ) -> WeatherLocation | None:
        return (
            self.db.query(WeatherLocation)
            .filter(
                WeatherLocation.latitude == latitude,
                WeatherLocation.longitude == longitude,
                WeatherLocation.is_active == True,  # noqa: E712
            )
            .one_or_none()
        )

    def upsert_provider_config(
        self,
        *,
        provider: str,
        base_url: str | None,
        api_key_ref: str | None,
        is_active: bool,
        priority: int,
        settings_json: dict | None,
    ) -> WeatherProviderConfig:
        row = (
            self.db.query(WeatherProviderConfig)
            .filter(WeatherProviderConfig.provider == provider)
            .one_or_none()
        )

        if row is None:
            row = WeatherProviderConfig(
                provider=provider,
                base_url=base_url,
                api_key_ref=api_key_ref,
                is_active=is_active,
                priority=priority,
                settings_json=settings_json,
            )
            self.db.add(row)
            self.db.flush()
            return row

        row.base_url = base_url
        row.api_key_ref = api_key_ref
        row.is_active = is_active
        row.priority = priority
        row.settings_json = settings_json

        self.db.flush()
        return row

    def get_active_provider_config(self) -> WeatherProviderConfig | None:
        return (
            self.db.query(WeatherProviderConfig)
            .filter(WeatherProviderConfig.is_active == True)  # noqa: E712
            .order_by(WeatherProviderConfig.priority.asc(), WeatherProviderConfig.id.asc())
            .first()
        )

    def list_provider_configs(self) -> list[WeatherProviderConfig]:
        return (
            self.db.query(WeatherProviderConfig)
            .order_by(
                WeatherProviderConfig.priority.asc(),
                WeatherProviderConfig.id.asc(),
            )
            .all()
        )

    def get_provider_config_by_id(
        self,
        *,
        config_id: int,
    ) -> WeatherProviderConfig | None:
        return (
            self.db.query(WeatherProviderConfig)
            .filter(WeatherProviderConfig.id == config_id)
            .one_or_none()
        )

    def add_snapshot(self, row: WeatherSnapshot) -> WeatherSnapshot:
        self.db.add(row)
        self.db.flush()
        return row

    def latest_snapshot(self, *, location_id: int) -> WeatherSnapshot | None:
        return (
            self.db.query(WeatherSnapshot)
            .filter(WeatherSnapshot.location_id == location_id)
            .order_by(WeatherSnapshot.observed_at.desc(), WeatherSnapshot.id.desc())
            .first()
        )

    def delete_forecasts_for_provider(
        self,
        *,
        location_id: int,
        provider: str,
    ) -> None:
        (
            self.db.query(WeatherForecast)
            .filter(
                WeatherForecast.location_id == location_id,
                WeatherForecast.provider == provider,
            )
            .delete(synchronize_session=False)
        )
        self.db.flush()

    def add_forecast(self, row: WeatherForecast) -> WeatherForecast:
        self.db.add(row)
        self.db.flush()
        return row

    def list_forecasts(
        self,
        *,
        location_id: int,
        forecast_type: str | None = None,
        limit: int = 40,
    ) -> list[WeatherForecast]:
        query = self.db.query(WeatherForecast).filter(
            WeatherForecast.location_id == location_id
        )

        if forecast_type:
            query = query.filter(WeatherForecast.forecast_type == forecast_type)

        return query.order_by(WeatherForecast.forecast_time.asc()).limit(limit).all()

    def latest_forecast_created_at(
        self,
        *,
        location_id: int,
        forecast_type: str | None = None,
    ) -> datetime | None:
        query = self.db.query(WeatherForecast).filter(
            WeatherForecast.location_id == location_id
        )

        if forecast_type:
            query = query.filter(WeatherForecast.forecast_type == forecast_type)

        row = query.order_by(
            WeatherForecast.created_at.desc(),
            WeatherForecast.id.desc(),
        ).first()

        return row.created_at if row else None

    def list_active_alerts(
        self,
        *,
        location_id: int,
        limit: int = 20,
    ) -> list[WeatherAlert]:
        return (
            self.db.query(WeatherAlert)
            .filter(
                WeatherAlert.location_id == location_id,
                WeatherAlert.is_active == True,  # noqa: E712
                WeatherAlert.status == "active",
            )
            .order_by(WeatherAlert.starts_at.desc(), WeatherAlert.id.desc())
            .limit(limit)
            .all()
        )

    def add_alert_rule(self, row: WeatherAlertRule) -> WeatherAlertRule:
        self.db.add(row)
        self.db.flush()
        return row

    def get_alert_rule_by_type(
        self,
        *,
        alert_type: str,
    ) -> WeatherAlertRule | None:
        return (
            self.db.query(WeatherAlertRule)
            .filter(WeatherAlertRule.alert_type == alert_type)
            .one_or_none()
        )

    def list_active_alert_rules(self) -> list[WeatherAlertRule]:
        return (
            self.db.query(WeatherAlertRule)
            .filter(WeatherAlertRule.is_active == True)  # noqa: E712
            .order_by(WeatherAlertRule.id.asc())
            .all()
        )

    def list_alert_rules(self) -> list[WeatherAlertRule]:
        return self.db.query(WeatherAlertRule).order_by(WeatherAlertRule.id.asc()).all()

    def add_alert(self, row: WeatherAlert) -> WeatherAlert:
        self.db.add(row)
        self.db.flush()
        return row

    def find_duplicate_active_alert(
        self,
        *,
        location_id: int,
        rule_id: int | None,
        alert_type: str,
        starts_at: datetime,
    ) -> WeatherAlert | None:
        return (
            self.db.query(WeatherAlert)
            .filter(
                WeatherAlert.location_id == location_id,
                WeatherAlert.rule_id == rule_id,
                WeatherAlert.alert_type == alert_type,
                WeatherAlert.starts_at == starts_at,
                WeatherAlert.status == "active",
                WeatherAlert.is_active == True,  # noqa: E712
            )
            .one_or_none()
        )

    def list_admin_alerts(
        self,
        *,
        location_id: int | None = None,
        alert_type: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[WeatherAlert], int]:
        query = self.db.query(WeatherAlert)

        if location_id:
            query = query.filter(WeatherAlert.location_id == location_id)

        if alert_type:
            query = query.filter(WeatherAlert.alert_type == alert_type)

        if status:
            query = query.filter(WeatherAlert.status == status)

        total = query.count()

        rows = (
            query.order_by(WeatherAlert.created_at.desc(), WeatherAlert.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return rows, total
