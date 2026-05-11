# Iran Cities Dataset v3

This directory contains the CSV files used to seed Farm Net geo tables.

## Files

- `ostan.csv` -> `geo_provinces`
- `shahrestan.csv` -> `geo_counties`
- `bakhsh.csv` -> `geo_districts`
- `dehestan.csv` -> `geo_rural_districts`
- `shahr.csv` -> `geo_cities`
- `abadi.csv` -> `geo_villages`

## Usage

Seed script:

```bash
python scripts/seed_geo.py
```
