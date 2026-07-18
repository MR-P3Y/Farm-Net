from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.auth.exceptions import ValidationAuthError
from app.modules.products.models import ProductCategory
from app.modules.products.repository import ProductRepository
from app.modules.products.schemas import ProductCategoryCreateIn, ProductCategoryOut, ProductCategoryUpdateIn


class ProductCategoryService:
    def __init__(self, db: Session) -> None:
        self.repo = ProductRepository(db)

    def list_categories(self, *, active_only: bool, q: str | None = None) -> list[ProductCategoryOut]:
        return [self._out(row) for row in self.repo.list_categories(active_only=active_only, q=q)]

    def create(self, payload: ProductCategoryCreateIn) -> ProductCategoryOut:
        self._validate_parent(parent_id=payload.parent_id, category_id=None)
        self._ensure_slug(payload.slug)
        row = self.repo.create_category(**payload.model_dump())
        self._commit()
        self.repo.refresh(row)
        return self._out(row)

    def update(self, *, category_id: int, payload: ProductCategoryUpdateIn) -> ProductCategoryOut:
        row = self.repo.get_category_for_admin(category_id=category_id)
        if row is None:
            raise ValidationAuthError(message="Product category not found")
        changes = payload.model_dump(exclude_unset=True)
        if changes.get("name", row.name) is None or changes.get("slug", row.slug) is None:
            raise ValidationAuthError(message="Product category name and slug are required")
        if "parent_id" in changes:
            self._validate_parent(parent_id=changes["parent_id"], category_id=category_id)
        if changes.get("slug") and changes["slug"] != row.slug:
            self._ensure_slug(changes["slug"])
        for key, value in changes.items():
            setattr(row, key, value)
        self._commit()
        self.repo.refresh(row)
        return self._out(row)

    def _validate_parent(self, *, parent_id: int | None, category_id: int | None) -> None:
        if parent_id is None:
            return
        if parent_id == category_id:
            raise ValidationAuthError(message="Category cannot be its own parent")
        parent = self.repo.get_category_for_admin(category_id=parent_id)
        if parent is None:
            raise ValidationAuthError(message="Parent category not found")
        cursor: ProductCategory | None = parent
        visited: set[int] = set()
        while cursor is not None and cursor.id not in visited:
            if cursor.id == category_id:
                raise ValidationAuthError(message="Category hierarchy cycle is not allowed")
            visited.add(cursor.id)
            cursor = self.repo.get_category_for_admin(category_id=cursor.parent_id) if cursor.parent_id else None

    def _ensure_slug(self, slug: str) -> None:
        if self.repo.get_category_by_slug(slug=slug):
            raise ValidationAuthError(message="Product category slug already exists")

    def _commit(self) -> None:
        try:
            self.repo.commit()
        except IntegrityError as exc:
            self.repo.rollback()
            raise ValidationAuthError(message="Product category conflicts with existing data") from exc

    def _out(self, row: ProductCategory) -> ProductCategoryOut:
        children, products = self.repo.category_counts(category_id=row.id)
        return ProductCategoryOut(
            id=row.id, parent_id=row.parent_id, name=row.name, slug=row.slug,
            description=row.description, sort_order=row.sort_order, is_active=row.is_active,
            children_count=children, products_count=products,
            created_at=row.created_at.isoformat(), updated_at=row.updated_at.isoformat(),
        )
