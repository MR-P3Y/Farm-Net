# Farm Net API - Geo

Geo APIs provide Iran geographic lookup data for profile, store, service, consultant, equipment rental, filtering, and admin workflows.

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
