# Farm Net Weather API

## Purpose

Weather foundation provides weather locations, current weather, forecasts, agricultural alerts, provider configuration, cache-aware refresh, and automatic weather alert generation.

## Scope

Current foundation supports:

```text
province/city/village/GPS style locations
current weather snapshots
hourly forecast records
automatic weather alert rules
admin weather management
mobile weather foundation
admin-panel weather foundation
```

## Providers

Supported providers:

```text
mock
openweather
```

Security rule:

```text
Real API keys must not be stored in code, docs, migrations, or commits.
Provider configs use api_key_ref such as OPENWEATHER_API_KEY.
The actual key must stay in ignored .env.
```

## User/Public APIs

### List weather locations

```http
GET /api/v1/weather/locations
```

Public endpoint.

Query parameters:

| Name | Type | Description |
| --- | --- | --- |
| page | int | Default 1 |
| page_size | int | Default 20, max 100 |
| q | string | Search display_name |
| country_code | string | Example IR |
| location_type | string | province/city/village/gps |

### Create GPS weather location

```http
POST /api/v1/weather/locations/gps
```

Required permission:

```text
weather.read
```

Body:

```json
{
  "latitude": 35.6892,
  "longitude": 51.3890,
  "display_name": "Tehran GPS",
  "timezone": "Asia/Tehran"
}
```

### Current weather

```http
GET /api/v1/weather/current?location_id=1
```

Public endpoint.

Returns latest cached snapshot. If no snapshot exists, project `success_response` may return empty data.

### Forecast

```http
GET /api/v1/weather/forecast?location_id=1
```

Public endpoint.

Returns cached forecast rows.

### Active alerts

```http
GET /api/v1/weather/alerts?location_id=1
```

Public endpoint.

Returns active weather alerts for location.

### Refresh weather

```http
POST /api/v1/weather/refresh?location_id=1&provider=mock
```

Required permission:

```text
weather.read
```

This endpoint is cache-aware and does not force provider calls if DB cache is fresh.

## Admin APIs

### Provider configs

```http
GET /api/v1/admin/weather/provider-configs
PATCH /api/v1/admin/weather/provider-configs/{config_id}
```

Required permissions:

```text
weather.admin_read
weather.provider_manage
```

Patch body example:

```json
{
  "is_active": true,
  "priority": 50,
  "api_key_ref": "OPENWEATHER_API_KEY",
  "base_url": "https://api.openweathermap.org/data/2.5",
  "settings_json": {
    "units": "metric"
  }
}
```

### Admin locations

```http
GET /api/v1/admin/weather/locations
GET /api/v1/admin/weather/locations/{location_id}
```

Required permission:

```text
weather.admin_read
```

### Cache status

```http
GET /api/v1/admin/weather/locations/{location_id}/cache-status
```

Required permission:

```text
weather.admin_read
```

Response includes:

```text
current_stale
forecast_stale
weather_stale
current_ttl_minutes
forecast_ttl_minutes
```

### Admin refresh

```http
POST /api/v1/admin/weather/refresh?location_id=1&provider=mock&force=true
```

Required permission:

```text
weather.admin_manage
```

Rules:

```text
force=true  -> provider refresh always runs
force=false -> refresh runs only if DB cache is stale
```

### Alert rules

```http
GET  /api/v1/admin/weather/alert-rules
POST /api/v1/admin/weather/alert-rules/seed
```

Required permission:

```text
weather.alert_manage
```

Default rules:

```text
frost: temperature_c <= 2
heat: temperature_c >= 38
heavy_rain: precipitation_mm >= 20
strong_wind: wind_speed_mps >= 12
spraying_not_recommended:
  wind_speed_mps >= 8 OR precipitation_probability >= 0.6
```

### Alerts

```http
GET  /api/v1/admin/weather/alerts
POST /api/v1/admin/weather/alerts/evaluate?location_id=1
```

Required permissions:

```text
weather.admin_read
weather.alert_manage
```

Evaluate runs automatic rules against cached forecasts and creates non-duplicate alerts.

## Notification Integration

When new weather alerts are created, admins/super-admins receive in-app notifications.

Event type:

```text
weather.alert_created
```

Notification target in current foundation:

```text
admin
super_admin
```

Regular user weather subscriptions are not implemented yet.

## Permissions

```text
weather.public_read
weather.read
weather.admin_read
weather.admin_manage
weather.alert_manage
weather.provider_manage
```

Role mapping:

```text
user: weather.public_read, weather.read
shop_owner: weather.public_read, weather.read
consultant: weather.public_read, weather.read
lessor: weather.public_read, weather.read
support: weather.public_read, weather.read, weather.admin_read
admin: all weather permissions
super_admin: all weather permissions
```

## Cache Policy

Current DB-based cache TTL:

```text
current weather: 30 minutes
forecast: 180 minutes
```

Redis is intentionally not required for the foundation. DB cache logic is provider-independent.

## Security Notes

- OpenWeather API key must stay in `.env`.
- API responses expose only `api_key_ref`, never the real key.
- User refresh is cache-aware.
- Admin refresh can be forced.
- Public endpoints read cached data only.
