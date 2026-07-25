from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from app.modules.farms.models import FarmCrop, FarmCropCategory, FarmMeasurementUnit


@dataclass(frozen=True)
class MeasurementUnitSeed:
    code: str
    title: str
    symbol: str
    dimension: str
    factor_to_base: Decimal
    is_base: bool
    sort_order: int


@dataclass(frozen=True)
class CropCategorySeed:
    code: str
    title: str
    sort_order: int


@dataclass(frozen=True)
class CropSeed:
    category_code: str
    code: str
    title: str
    scientific_name: str
    cycle_type: str
    sort_order: int


MEASUREMENT_UNITS = (
    MeasurementUnitSeed("square_meter", "متر مربع", "m²", "area", Decimal("1"), True, 10),
    MeasurementUnitSeed("hectare", "هکتار", "ha", "area", Decimal("10000"), False, 20),
    MeasurementUnitSeed("kilogram", "کیلوگرم", "kg", "mass", Decimal("1"), True, 30),
    MeasurementUnitSeed("tonne", "تن", "t", "mass", Decimal("1000"), False, 40),
    MeasurementUnitSeed("liter", "لیتر", "L", "volume", Decimal("1"), True, 50),
    MeasurementUnitSeed("cubic_meter", "متر مکعب", "m³", "volume", Decimal("1000"), False, 60),
    MeasurementUnitSeed("meter", "متر", "m", "length", Decimal("1"), True, 70),
    MeasurementUnitSeed("piece", "عدد", "عدد", "count", Decimal("1"), True, 80),
)

CROP_CATEGORIES = (
    CropCategorySeed("cereals", "غلات", 10),
    CropCategorySeed("legumes", "حبوبات", 20),
    CropCategorySeed("vegetables", "سبزی و صیفی", 30),
    CropCategorySeed("orchard_fruits", "میوه‌های باغی", 40),
    CropCategorySeed("nuts", "محصولات آجیلی", 50),
    CropCategorySeed("industrial", "محصولات صنعتی", 60),
    CropCategorySeed("medicinal", "گیاهان دارویی و ادویه‌ای", 70),
)

CROPS = (
    CropSeed("cereals", "wheat", "گندم", "Triticum aestivum", "annual", 10),
    CropSeed("cereals", "barley", "جو", "Hordeum vulgare", "annual", 20),
    CropSeed("cereals", "rice", "برنج", "Oryza sativa", "annual", 30),
    CropSeed("legumes", "chickpea", "نخود", "Cicer arietinum", "annual", 40),
    CropSeed("vegetables", "tomato", "گوجه‌فرنگی", "Solanum lycopersicum", "annual", 50),
    CropSeed("vegetables", "potato", "سیب‌زمینی", "Solanum tuberosum", "annual", 60),
    CropSeed("vegetables", "onion", "پیاز", "Allium cepa", "annual", 70),
    CropSeed("orchard_fruits", "apple", "سیب", "Malus domestica", "perennial", 80),
    CropSeed("orchard_fruits", "pomegranate", "انار", "Punica granatum", "perennial", 90),
    CropSeed("orchard_fruits", "citrus", "مرکبات", "Citrus spp.", "perennial", 100),
    CropSeed("nuts", "pistachio", "پسته", "Pistacia vera", "perennial", 110),
    CropSeed("industrial", "cotton", "پنبه", "Gossypium spp.", "annual", 120),
    CropSeed("medicinal", "saffron", "زعفران", "Crocus sativus", "perennial", 130),
)


def seed_farm_references(db: Session) -> dict[str, int]:
    for item in MEASUREMENT_UNITS:
        row = (
            db.query(FarmMeasurementUnit)
            .filter(FarmMeasurementUnit.code == item.code)
            .one_or_none()
        )
        if row is None:
            row = FarmMeasurementUnit(code=item.code)
            db.add(row)
        row.title = item.title
        row.symbol = item.symbol
        row.dimension = item.dimension
        row.factor_to_base = item.factor_to_base
        row.is_base = item.is_base
        row.is_active = True
        row.sort_order = item.sort_order

    categories: dict[str, FarmCropCategory] = {}
    for item in CROP_CATEGORIES:
        row = (
            db.query(FarmCropCategory)
            .filter(FarmCropCategory.code == item.code)
            .one_or_none()
        )
        if row is None:
            row = FarmCropCategory(code=item.code)
            db.add(row)
        row.title = item.title
        row.sort_order = item.sort_order
        row.is_active = True
        categories[item.code] = row

    db.flush()
    for item in CROPS:
        row = db.query(FarmCrop).filter(FarmCrop.code == item.code).one_or_none()
        if row is None:
            row = FarmCrop(code=item.code)
            db.add(row)
        row.category_id = categories[item.category_code].id
        row.title = item.title
        row.scientific_name = item.scientific_name
        row.default_cycle_type = item.cycle_type
        row.sort_order = item.sort_order
        row.is_active = True

    db.commit()
    return {
        "measurement_units": len(MEASUREMENT_UNITS),
        "crop_categories": len(CROP_CATEGORIES),
        "crops": len(CROPS),
    }
