from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.modules.admin.schemas import (
    AdminPermissionOut,
    AdminRoleOut,
    AdminUserDetailOut,
    AdminUserListItemOut,
)
from app.modules.auth.enums import UserStatus
from app.modules.auth.exceptions import UserNotFoundError, ValidationAuthError
from app.modules.auth.models import AuthPermission, AuthRole, AuthUser
from app.modules.auth.repository import AuthRepository


class AdminAuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.auth_repo = AuthRepository(db)

    def list_users(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        q: str | None = None,
        status: str | None = None,
    ) -> tuple[list[AdminUserListItemOut], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        query = self.db.query(AuthUser)

        if status:
            query = query.filter(AuthUser.status == status)

        if q:
            like = f"%{q.strip().lower()}%"
            query = query.filter(
                or_(
                    AuthUser.email.ilike(like),
                    AuthUser.phone.ilike(like),
                )
            )

        total = query.count()

        users = (
            query.order_by(AuthUser.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        items = [
            AdminUserListItemOut(
                id=user.id,
                email=user.email,
                phone=user.phone,
                status=user.status,
                is_email_verified=user.is_email_verified,
                is_phone_verified=user.is_phone_verified,
                roles=self.auth_repo.get_user_role_codes(user.id),
            )
            for user in users
        ]

        return items, total

    def get_user_detail(self, user_id: int) -> AdminUserDetailOut:
        user = self.auth_repo.get_user_by_id(user_id)

        if user is None:
            raise UserNotFoundError()

        return AdminUserDetailOut(
            id=user.id,
            email=user.email,
            phone=user.phone,
            status=user.status,
            is_email_verified=user.is_email_verified,
            is_phone_verified=user.is_phone_verified,
            roles=self.auth_repo.get_user_role_codes(user.id),
            permissions=self.auth_repo.get_user_permission_codes(user.id),
        )

    def update_user_status(
        self,
        *,
        user_id: int,
        status: str,
    ) -> AdminUserDetailOut:
        allowed_statuses = {item.value for item in UserStatus}

        if status not in allowed_statuses:
            raise ValidationAuthError(
                message="Invalid user status",
                details={"allowed_statuses": sorted(allowed_statuses)},
            )

        user = self.auth_repo.get_user_by_id(user_id)

        if user is None:
            raise UserNotFoundError()

        user.status = status
        self.db.commit()
        self.db.refresh(user)

        return self.get_user_detail(user.id)

    def list_roles(self) -> list[AdminRoleOut]:
        roles = self.db.query(AuthRole).order_by(AuthRole.code.asc()).all()

        return [
            AdminRoleOut(
                id=role.id,
                code=role.code,
                name=role.name,
                description=role.description,
                is_system=role.is_system,
                is_active=role.is_active,
            )
            for role in roles
        ]

    def list_permissions(
        self,
        *,
        module: str | None = None,
    ) -> list[AdminPermissionOut]:
        query = self.db.query(AuthPermission)

        if module:
            query = query.filter(AuthPermission.module == module)

        permissions = query.order_by(
            AuthPermission.module.asc(),
            AuthPermission.code.asc(),
        ).all()

        return [
            AdminPermissionOut(
                id=permission.id,
                code=permission.code,
                name=permission.name,
                module=permission.module,
                description=permission.description,
                is_system=permission.is_system,
                is_active=permission.is_active,
            )
            for permission in permissions
        ]
