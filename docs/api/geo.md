# Farm Net API - Geo

Geo APIs provide Iran geographic lookup data for profile, store, service,
consultant, equipment rental, filtering, and admin workflows. They also provide
a controlled, authenticated place-search boundary for Farm Plot selection.

Base path:

```text
/api/v1/geo
```

## Data Source

Iran Cities Dataset v3 is stored in:

```text
data/geo/iran-cities/v3/csv/
```

Seed command:

```bash
python scripts/seed_geo.py
```

Seeded tables:

```text
geo_provinces
geo_counties
geo_districts
geo_rural_districts
geo_cities
geo_villages
```

## Endpoints

### Search for a Farm location

```http
GET /api/v1/geo/search?q=قلات%20شیراز&language=fa&limit=5
Authorization: Bearer <access_token>
```

This route requires `farms.manage_own`. Search is submitted explicitly; it is
not an autocomplete API. The Backend queries the configured Nominatim provider,
limits results to Iran by default, and maps unambiguous provider address names
to Farm-Net's internal Province/County/District/City/Village IDs.

```json
{
  "success": true,
  "data": [
    {
      "reference": "49a8a26ef3c6c3a62463bd8d",
      "display_name": "قلات، شهرستان شیراز، استان فارس، ایران",
      "short_name": "قلات",
      "latitude": "29.8051",
      "longitude": "52.4897",
      "category": "place",
      "place_type": "village",
      "country_code": "ir",
      "province_id": 17,
      "county_id": 174,
      "district_id": null,
      "rural_district_id": null,
      "city_id": null,
      "village_id": 12345,
      "provider": "openstreetmap",
      "attribution": "© OpenStreetMap contributors"
    }
  ],
  "message": "OK",
  "meta": {"count": 1, "cached": false, "trace_id": "..."}
}
```

Provider names are advisory. Only IDs that resolve uniquely against active
internal Geo records are returned. Coordinates remain usable when no internal
name match exists.

### Resolve a selected map point

```http
GET /api/v1/geo/reverse?latitude=29.8051000&longitude=52.4897000&language=fa
Authorization: Bearer <access_token>
```

This route also requires `farms.manage_own` and returns one object with the same
shape as a search result. Mobile uses it after a user explicitly chooses a map
point or device location. Failure is non-blocking for Plot creation: the chosen
coordinates can still be saved.

Both endpoints return `Cache-Control: no-store`. The Backend enforces its normal
per-client search limit, hashes cache keys, caches provider responses for the
configured bounded TTL, and permits no more than one public-provider request per
second across the application. The public Nominatim defaults are replaceable by
configuration. Submitted search text or coordinates are sent to the configured
provider; raw provider payloads are not written to the Farm database.

### List provinces

```http
GET /api/v1/geo/provinces
```

Response:

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "آذربایجان شرقی",
      "amar_code": "3"
    }
  ],
  "message": "OK",
  "meta": {
    "count": 31,
    "trace_id": "..."
  }
}
```

### List counties

```http
GET /api/v1/geo/counties?province_id=1
```

Query parameters:

| Name        | Type | Required | Description                 |
| ----------- | ---: | -------: | --------------------------- |
| province_id |  int |       no | Filter counties by province |

### List districts

```http
GET /api/v1/geo/districts?county_id=5
```

Query parameters:

| Name        | Type | Required | Description        |
| ----------- | ---: | -------: | ------------------ |
| province_id |  int |       no | Filter by province |
| county_id   |  int |       no | Filter by county   |

### List rural districts

```http
GET /api/v1/geo/rural-districts?district_id=222
```

Query parameters:

| Name        | Type | Required | Description        |
| ----------- | ---: | -------: | ------------------ |
| province_id |  int |       no | Filter by province |
| county_id   |  int |       no | Filter by county   |
| district_id |  int |       no | Filter by district |

### List cities

```http
GET /api/v1/geo/cities?province_id=1
GET /api/v1/geo/cities?q=تبریز
```

Query parameters:

| Name        |   Type | Required | Description         |
| ----------- | -----: | -------: | ------------------- |
| province_id |    int |       no | Filter by province  |
| county_id   |    int |       no | Filter by county    |
| district_id |    int |       no | Filter by district  |
| q           | string |       no | Search by city name |

### List villages

```http
GET /api/v1/geo/villages?page=1&page_size=20
GET /api/v1/geo/villages?q=اسلام
```

Villages are paginated because the table contains many records.

Query parameters:

| Name              |   Type | Required | Description                    |
| ----------------- | -----: | -------: | ------------------------------ |
| page              |    int |       no | Default: 1                     |
| page_size         |    int |       no | Default: 50, max: 100          |
| province_id       |    int |       no | Filter by province             |
| county_id         |    int |       no | Filter by county               |
| district_id       |    int |       no | Filter by district             |
| rural_district_id |    int |       no | Filter by rural district       |
| q                 | string |       no | Search by village name or diag |

Response meta for villages:

```json
{
  "page": 1,
  "page_size": 20,
  "total": 98100,
  "total_pages": 4905,
  "trace_id": "..."
}
```

## Validation Rules

* Geo IDs must be positive integers.
* Village list must stay paginated.
* Geo data is read-only in MVP.
* Admin management for Geo data is not part of Phase 6.
