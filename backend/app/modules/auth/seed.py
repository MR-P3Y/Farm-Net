from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.modules.auth.models import (
    AuthPermission,
    AuthRole,
    AuthRolePermission,
    AuthUser,
    AuthUserRole,
)
from app.modules.auth.enums import UserStatus
from app.modules.auth.utils import normalize_iran_phone


@dataclass(frozen=True)
class RoleSeed:
    code: str
    name: str
    description: str


@dataclass(frozen=True)
class PermissionSeed:
    code: str
    name: str
    module: str
    description: str


BASE_ROLES: list[RoleSeed] = [
    RoleSeed("user", "User", "Base user role"),
    RoleSeed("shop_owner", "Shop Owner", "Approved shop owner"),
    RoleSeed("service_provider", "Service Provider", "Approved service provider"),
    RoleSeed("lessor", "Lessor", "Agricultural equipment lessor"),
    RoleSeed("consultant", "Consultant", "Approved agriculture consultant"),
    RoleSeed("support", "Support", "Customer support role"),
    RoleSeed("content_manager", "Content Manager", "Content and moderation manager"),
    RoleSeed("finance_admin", "Finance Admin", "Finance management role"),
    RoleSeed("verification_admin", "Verification Admin", "Documents and verification reviewer"),
    RoleSeed("admin", "Admin", "General admin role"),
    RoleSeed("super_admin", "Super Admin", "Full system access"),
    RoleSeed("data_client", "Data Client", "Contract-based data access client"),
]


BASE_PERMISSIONS: list[PermissionSeed] = [
    PermissionSeed("dashboard.read", "Read dashboard", "dashboard", "View admin dashboard"),

    PermissionSeed("users.read", "Read users", "users", "View users list"),
    PermissionSeed("users.read_detail", "Read user detail", "users", "View user details"),
    PermissionSeed("users.update_status", "Update user status", "users", "Suspend/restore users"),
    PermissionSeed("users.manage_roles", "Manage user roles", "users", "Assign/remove user roles"),

    PermissionSeed("roles.read", "Read roles", "roles", "View roles"),
    PermissionSeed("roles.create", "Create roles", "roles", "Create roles"),
    PermissionSeed("roles.update", "Update roles", "roles", "Update roles"),
    PermissionSeed("roles.delete", "Delete roles", "roles", "Delete roles"),
    PermissionSeed("permissions.read", "Read permissions", "permissions", "View permissions"),
    PermissionSeed("permissions.assign", "Assign permissions", "permissions", "Assign permissions to roles"),

    PermissionSeed("profiles.read", "Read profiles", "profiles", "View profiles"),
    PermissionSeed("profiles.update", "Update profiles", "profiles", "Update own profile"),
    PermissionSeed("profiles.read_private", "Read private profiles", "profiles", "View private profile fields"),

    PermissionSeed("geo.read", "Read geo data", "geo", "View geo data"),
    PermissionSeed("geo.manage", "Manage geo data", "geo", "Manage geo data"),
    PermissionSeed("geo.seed", "Seed geo data", "geo", "Seed provinces/cities/villages"),

    PermissionSeed("notifications.read", "Read own notifications", "notifications", "Allows user to read own in-app notifications."),
    PermissionSeed("notifications.manage", "Manage own notifications", "notifications", "Allows user to mark, archive, or delete own notifications."),
    PermissionSeed("notifications.admin_read", "Admin read notifications", "notifications", "Allows admin to read notification records."),
    PermissionSeed("notifications.admin_manage", "Admin manage notifications", "notifications", "Allows admin to manage notification records."),
    PermissionSeed("notifications.system_message", "Send system notification", "notifications", "Allows admin to send system messages through notifications."),

    PermissionSeed("media.upload", "Upload media", "media", "Upload files to media storage"),
    PermissionSeed("media.read", "Read own media", "media", "Read current user's media files"),
    PermissionSeed("media.public_read", "Read public media", "media", "Read public media files"),
    PermissionSeed("media.private_read", "Read private media", "media", "Read private media files owned by the current user"),
    PermissionSeed("media.delete", "Delete own media", "media", "Soft delete current user's media files"),
    PermissionSeed("media.admin_read", "Admin read media", "media", "Admin can list and inspect media files"),
    PermissionSeed("media.admin_manage", "Admin manage media", "media", "Admin can manage media files and moderation status"),

    PermissionSeed("documents.read", "Read documents", "documents", "View documents"),
    PermissionSeed("documents.review", "Review documents", "documents", "Review documents"),
    PermissionSeed("documents.approve", "Approve documents", "documents", "Approve documents"),
    PermissionSeed("documents.reject", "Reject documents", "documents", "Reject documents"),

    PermissionSeed("verification.read", "Read verification", "verification", "View verification requests"),
    PermissionSeed("verification.review", "Review verification", "verification", "Review verification requests"),
    PermissionSeed("verification.approve", "Approve verification", "verification", "Approve verification requests"),
    PermissionSeed("verification.reject", "Reject verification", "verification", "Reject verification requests"),
    PermissionSeed("verification.needs_revision", "Needs revision verification", "verification", "Mark verification as needs revision"),

    PermissionSeed("stores.read", "Read stores", "stores", "Read own store data"),
    PermissionSeed("stores.create", "Create store", "stores", "Create own store"),
    PermissionSeed("stores.update", "Update store", "stores", "Update own store"),
    PermissionSeed("stores.submit", "Submit store", "stores", "Submit store for admin review"),
    PermissionSeed("stores.manage_members", "Manage store members", "stores", "Manage own store members"),
    PermissionSeed("stores.admin_read", "Admin read stores", "stores", "Admin can list and read stores"),
    PermissionSeed("stores.admin_review", "Admin review stores", "stores", "Admin can review stores"),
    PermissionSeed("stores.approve", "Approve stores", "stores", "Admin can approve stores"),
    PermissionSeed("stores.reject", "Reject stores", "stores", "Admin can reject stores"),
    PermissionSeed("stores.suspend", "Suspend stores", "stores", "Admin can suspend stores"),
    PermissionSeed("stores.public_read", "Public read stores", "stores", "Read public approved stores"),

    PermissionSeed("contracts.read", "Read contracts", "contracts", "View contracts"),
    PermissionSeed("contracts.create", "Create contracts", "contracts", "Create contract templates"),
    PermissionSeed("contracts.update", "Update contracts", "contracts", "Update contract templates"),
    PermissionSeed("contracts.activate", "Activate contracts", "contracts", "Activate contract templates"),
    PermissionSeed("contracts.deactivate", "Deactivate contracts", "contracts", "Deactivate contract templates"),
    PermissionSeed("contracts.review_signed_pdf", "Review signed PDF", "contracts", "Review signed contract PDFs"),

    PermissionSeed("billing.plans.read", "Read billing plans", "billing", "View billing plans"),
    PermissionSeed("billing.plans.create", "Create billing plans", "billing", "Create billing plans"),
    PermissionSeed("billing.plans.update", "Update billing plans", "billing", "Update billing plans"),
    PermissionSeed("billing.plans.delete", "Delete billing plans", "billing", "Delete billing plans"),
    PermissionSeed("billing.subscriptions.read", "Read subscriptions", "billing", "View subscriptions"),
    PermissionSeed("billing.subscriptions.activate", "Activate subscriptions", "billing", "Activate subscriptions"),
    PermissionSeed("billing.subscriptions.cancel", "Cancel subscriptions", "billing", "Cancel subscriptions"),
    PermissionSeed("billing.usage.read", "Read billing usage", "billing", "View feature usage"),

    PermissionSeed("cart.read", "Read cart", "cart", "Read current user's cart"),
    PermissionSeed("cart.update", "Update cart", "cart", "Add, update or remove cart items"),

    PermissionSeed("orders.read", "Read own orders", "orders", "Read current user's orders"),
    PermissionSeed("orders.create", "Create orders", "orders", "Create order from cart checkout"),
    PermissionSeed("orders.cancel", "Cancel own orders", "orders", "Cancel current user's pending orders"),
    PermissionSeed("orders.seller_read", "Seller read orders", "orders", "Seller can read orders for own store"),
    PermissionSeed("orders.seller_update", "Seller update orders", "orders", "Seller can update operational order status"),
    PermissionSeed("orders.admin_read", "Admin read orders", "orders", "Admin can list and inspect all orders"),
    PermissionSeed("orders.admin_update", "Admin update orders", "orders", "Admin can update order status and admin notes"),

    PermissionSeed("payments.read", "Read own payments", "payments", "Read current user's payments"),
    PermissionSeed("payments.create", "Create payments", "payments", "Create payment attempt for own order"),
    PermissionSeed("payments.admin_read", "Admin read payments", "payments", "Admin can list and inspect payments"),
    PermissionSeed("payments.admin_update", "Admin update payments", "payments", "Admin can update payment status in supported flows"),

    PermissionSeed("commission.read", "Read commission settings", "commission", "Read platform commission settings"),
    PermissionSeed("commission.update", "Update commission settings", "commission", "Update platform commission settings"),

    PermissionSeed("finance.invoices.read", "Read invoices", "finance", "View invoices"),
    PermissionSeed("finance.invoices.read_detail", "Read invoice detail", "finance", "View invoice details"),
    PermissionSeed("finance.transactions.read", "Read transactions", "finance", "View transactions"),
    PermissionSeed("finance.payments.read", "Read payments", "finance", "View payment attempts"),
    PermissionSeed("finance.payments.verify_manual", "Manual payment verify", "finance", "Manually verify payments"),
    PermissionSeed("finance.refunds.create", "Create refunds", "finance", "Create refunds"),
    PermissionSeed("finance.settlements.read", "Read settlements", "finance", "View settlements"),
    PermissionSeed("finance.settlements.manage", "Manage settlements", "finance", "Manage settlements"),

    PermissionSeed("shops.read", "Read shops", "store", "View shops"),
    PermissionSeed("shops.read_detail", "Read shop detail", "store", "View shop details"),
    PermissionSeed("shops.approve", "Approve shops", "store", "Approve shops"),
    PermissionSeed("shops.reject", "Reject shops", "store", "Reject shops"),
    PermissionSeed("shops.suspend", "Suspend shops", "store", "Suspend shops"),
    PermissionSeed("shops.restore", "Restore shops", "store", "Restore shops"),

    PermissionSeed("shop_members.read", "Read shop members", "store", "View shop members"),
    PermissionSeed("shop_members.manage", "Manage shop members", "store", "Manage shop members"),

    PermissionSeed("store_categories.read", "Read store categories", "store", "View store categories"),
    PermissionSeed("store_categories.create", "Create store categories", "store", "Create store categories"),
    PermissionSeed("store_categories.update", "Update store categories", "store", "Update store categories"),
    PermissionSeed("store_categories.delete", "Delete store categories", "store", "Delete store categories"),

    PermissionSeed("products.read", "Read products", "products", "Read own store products"),
    PermissionSeed("products.create", "Create products", "products", "Create products for own approved store"),
    PermissionSeed("products.update", "Update products", "products", "Update own store products"),
    PermissionSeed("products.delete", "Delete products", "products", "Soft delete or archive own store products"),
    PermissionSeed("products.publish", "Publish products", "products", "Publish own store products"),
    PermissionSeed("products.unpublish", "Unpublish products", "products", "Unpublish own store products"),
    PermissionSeed("products.manage_images", "Manage product images", "products", "Manage product image metadata"),
    PermissionSeed("products.admin_read", "Admin read products", "products", "Admin can list and inspect products"),
    PermissionSeed("products.suspend", "Suspend products", "products", "Admin can suspend products for violations"),
    PermissionSeed("products.restore", "Restore products", "products", "Admin can restore suspended products"),
    PermissionSeed("products.public_read", "Public read products", "products", "Read public published products"),

    PermissionSeed("promotions.read", "Read promotions", "promotion", "View promotions"),
    PermissionSeed("promotions.create", "Create promotions", "promotion", "Create promotions"),
    PermissionSeed("promotions.update", "Update promotions", "promotion", "Update promotions"),
    PermissionSeed("promotions.activate", "Activate promotions", "promotion", "Activate promotions"),
    PermissionSeed("promotions.cancel", "Cancel promotions", "promotion", "Cancel promotions"),
    PermissionSeed("promotion_packages.read", "Read promotion packages", "promotion", "View promotion packages"),
    PermissionSeed("promotion_packages.create", "Create promotion packages", "promotion", "Create promotion packages"),
    PermissionSeed("promotion_packages.update", "Update promotion packages", "promotion", "Update promotion packages"),
    PermissionSeed("promotion_packages.delete", "Delete promotion packages", "promotion", "Delete promotion packages"),

    PermissionSeed("services.read", "Read services", "services", "View services"),
    PermissionSeed("services.approve", "Approve services", "services", "Approve services"),
    PermissionSeed("services.reject", "Reject services", "services", "Reject services"),
    PermissionSeed("services.suspend", "Suspend services", "services", "Suspend services"),
    PermissionSeed("service_categories.read", "Read service categories", "services", "View service categories"),
    PermissionSeed("service_categories.create", "Create service categories", "services", "Create service categories"),
    PermissionSeed("service_categories.update", "Update service categories", "services", "Update service categories"),
    PermissionSeed("service_categories.delete", "Delete service categories", "services", "Delete service categories"),

    PermissionSeed("rental_equipment.read", "Read rental equipment", "rental", "View rental equipment"),
    PermissionSeed("rental_equipment.approve", "Approve rental equipment", "rental", "Approve rental equipment"),
    PermissionSeed("rental_equipment.reject", "Reject rental equipment", "rental", "Reject rental equipment"),
    PermissionSeed("rental_equipment.suspend", "Suspend rental equipment", "rental", "Suspend rental equipment"),

    PermissionSeed("consultants.read", "Read consultants", "consultants", "View consultants"),
    PermissionSeed("consultants.approve", "Approve consultants", "consultants", "Approve consultants"),
    PermissionSeed("consultants.reject", "Reject consultants", "consultants", "Reject consultants"),
    PermissionSeed("consultants.suspend", "Suspend consultants", "consultants", "Suspend consultants"),
    PermissionSeed("consult_specialties.read", "Read consult specialties", "consultants", "View specialties"),
    PermissionSeed("consult_specialties.create", "Create consult specialties", "consultants", "Create specialties"),
    PermissionSeed("consult_specialties.update", "Update consult specialties", "consultants", "Update specialties"),
    PermissionSeed("consult_specialties.delete", "Delete consult specialties", "consultants", "Delete specialties"),
    PermissionSeed("consult_requests.read", "Read consult requests", "consultants", "View consult requests"),
    PermissionSeed("consult_requests.manage", "Manage consult requests", "consultants", "Manage consult requests"),

    PermissionSeed(
        "weather.public_read",
        "Public read weather",
        "weather",
        "Allows public access to weather locations, current weather, forecasts, and public alerts.",
    ),
    PermissionSeed(
        "weather.read",
        "Read weather",
        "weather",
        "Allows authenticated users to read weather data.",
    ),
    PermissionSeed(
        "weather.admin_read",
        "Admin read weather",
        "weather",
        "Allows admin users to read weather records and provider settings.",
    ),
    PermissionSeed(
        "weather.admin_manage",
        "Admin manage weather",
        "weather",
        "Allows admin users to manage weather locations and refresh weather data.",
    ),
    PermissionSeed(
        "weather.alert_manage",
        "Manage weather alerts",
        "weather",
        "Allows admin users to manage weather alert rules and alerts.",
    ),
    PermissionSeed(
        "weather.provider_manage",
        "Manage weather providers",
        "weather",
        "Allows admin users to manage weather provider configuration.",
    ),

    PermissionSeed("ai.requests.read", "Read AI requests", "ai", "View AI requests"),
    PermissionSeed("ai.feedback.read", "Read AI feedback", "ai", "View AI feedback"),
    PermissionSeed("ai.knowledge_sources.read", "Read AI knowledge sources", "ai", "View knowledge sources"),
    PermissionSeed("ai.knowledge_sources.create", "Create AI knowledge sources", "ai", "Create knowledge sources"),
    PermissionSeed("ai.knowledge_sources.update", "Update AI knowledge sources", "ai", "Update knowledge sources"),
    PermissionSeed("ai.usage.read", "Read AI usage", "ai", "View AI usage"),

    PermissionSeed("social.public_read", "Public read social", "social", "Allows public users to read published public social posts."),
    PermissionSeed("social.read", "Read social", "social", "Allows authenticated users to read social community content."),
    PermissionSeed("social.post_create", "Create social posts", "social", "Allows users to create social posts."),
    PermissionSeed("social.post_manage_own", "Manage own social posts", "social", "Allows users to edit or delete their own social posts."),
    PermissionSeed("social.comment_create", "Create social comments", "social", "Allows users to create comments on social posts."),
    PermissionSeed("social.comment_manage_own", "Manage own social comments", "social", "Allows users to edit or delete their own comments."),
    PermissionSeed("social.react", "React to social content", "social", "Allows users to react to posts and comments."),
    PermissionSeed("social.bookmark", "Bookmark social posts", "social", "Allows users to bookmark social posts."),
    PermissionSeed("social.report", "Report social content", "social", "Allows users to report posts and comments."),
    PermissionSeed("social.admin_read", "Admin read social", "social", "Allows admins to read social content and reports."),
    PermissionSeed("social.admin_moderate", "Moderate social content", "social", "Allows admins to moderate posts, comments, and reports."),
    PermissionSeed("social.admin_manage", "Admin manage social", "social", "Allows admins to manage social categories and settings."),

    PermissionSeed("data_clients.read", "Read data clients", "data_access", "View data clients"),
    PermissionSeed("data_clients.create", "Create data clients", "data_access", "Create data clients"),
    PermissionSeed("data_clients.update", "Update data clients", "data_access", "Update data clients"),
    PermissionSeed("data_clients.suspend", "Suspend data clients", "data_access", "Suspend data clients"),
    PermissionSeed("data_access.contracts.read", "Read data contracts", "data_access", "View data access contracts"),
    PermissionSeed("data_access.contracts.manage", "Manage data contracts", "data_access", "Manage data access contracts"),
    PermissionSeed("data_access.exports.read", "Read data exports", "data_access", "View data exports"),
    PermissionSeed("data_access.exports.approve", "Approve data exports", "data_access", "Approve data exports"),
    PermissionSeed("data_access.logs.read", "Read data access logs", "data_access", "View data access logs"),

    PermissionSeed("reports.read", "Read reports", "reports", "View reports"),
    PermissionSeed("reports.export", "Export reports", "reports", "Export reports"),
    PermissionSeed("reports.finance", "Finance reports", "reports", "View finance reports"),
    PermissionSeed("reports.users", "User reports", "reports", "View user reports"),
    PermissionSeed("reports.store", "Store reports", "reports", "View store reports"),
    PermissionSeed("reports.ai", "AI reports", "reports", "View AI reports"),
    PermissionSeed("reports.social", "Social reports", "reports", "View social reports"),

    PermissionSeed("settings.read", "Read settings", "settings", "View settings"),
    PermissionSeed("settings.update", "Update settings", "settings", "Update settings"),
    PermissionSeed("feature_flags.read", "Read feature flags", "settings", "View feature flags"),
    PermissionSeed("feature_flags.update", "Update feature flags", "settings", "Update feature flags"),
]

RETIRED_PERMISSION_CODES = {
    "products.read_detail",
    "products.approve",
    "products.reject",
}

REMOVED_PERMISSION_CODES = {
    "commission.create",
    "commission.deactivate",
    "notifications.manage_channels",
    "notifications.manage_templates",
    "notifications.send_test",
    "notifications.view_delivery_logs",
    "weather.manage_alerts",
    "weather.manage_locations",
    "social.posts.read",
    "social.posts.remove",
    "social.comments.read",
    "social.comments.remove",
    "social.reports.read",
    "social.reports.resolve",
    "social.users.block",
}

RETIRED_ROLE_PERMISSION_CODES: dict[str, set[str]] = {
    "support": {
        "products.read",
        "products.read_detail",
    },
    "admin": {
        "products.read",
        "products.read_detail",
        "products.approve",
        "products.reject",
    },
}


def seed_roles(db: Session) -> dict[str, AuthRole]:
    roles_by_code: dict[str, AuthRole] = {}

    for item in BASE_ROLES:
        role = db.query(AuthRole).filter(AuthRole.code == item.code).one_or_none()

        if role is None:
            role = AuthRole(
                code=item.code,
                name=item.name,
                description=item.description,
                is_system=True,
                is_active=True,
            )
            db.add(role)
            db.flush()
        else:
            role.name = item.name
            role.description = item.description
            role.is_system = True
            role.is_active = True

        roles_by_code[item.code] = role

    return roles_by_code


def seed_permissions(db: Session) -> dict[str, AuthPermission]:
    permissions_by_code: dict[str, AuthPermission] = {}

    for item in BASE_PERMISSIONS:
        permission = (
            db.query(AuthPermission)
            .filter(AuthPermission.code == item.code)
            .one_or_none()
        )

        if permission is None:
            permission = AuthPermission(
                code=item.code,
                name=item.name,
                module=item.module,
                description=item.description,
                is_system=True,
                is_active=True,
            )
            db.add(permission)
            db.flush()
        else:
            permission.name = item.name
            permission.module = item.module
            permission.description = item.description
            permission.is_system = True
            permission.is_active = True

        permissions_by_code[item.code] = permission

    return permissions_by_code


def assign_all_permissions_to_super_admin(
    db: Session,
    super_admin_role: AuthRole,
    permissions_by_code: dict[str, AuthPermission],
) -> None:
    for permission in permissions_by_code.values():
        exists = (
            db.query(AuthRolePermission)
            .filter(
                AuthRolePermission.role_id == super_admin_role.id,
                AuthRolePermission.permission_id == permission.id,
            )
            .one_or_none()
        )

        if exists is None:
            db.add(
                AuthRolePermission(
                    role_id=super_admin_role.id,
                    permission_id=permission.id,
                )
            )


def retire_permissions(db: Session) -> None:
    retired = (
        db.query(AuthPermission)
        .filter(AuthPermission.code.in_(RETIRED_PERMISSION_CODES))
        .all()
    )

    if not retired:
        return

    retired_ids = [permission.id for permission in retired]

    (
        db.query(AuthRolePermission)
        .filter(AuthRolePermission.permission_id.in_(retired_ids))
        .delete(synchronize_session=False)
    )

    for permission in retired:
        permission.is_active = False


def remove_retired_role_permissions(
    db: Session,
    roles_by_code: dict[str, AuthRole],
) -> None:
    for role_code, permission_codes in RETIRED_ROLE_PERMISSION_CODES.items():
        role = roles_by_code.get(role_code)

        if role is None:
            continue

        permission_ids = [
            row[0]
            for row in (
                db.query(AuthPermission.id)
                .filter(AuthPermission.code.in_(permission_codes))
                .all()
            )
        ]

        if not permission_ids:
            continue

        (
            db.query(AuthRolePermission)
            .filter(
                AuthRolePermission.role_id == role.id,
                AuthRolePermission.permission_id.in_(permission_ids),
            )
            .delete(synchronize_session=False)
        )


def delete_removed_permissions(db: Session) -> None:
    removed_ids = [
        row[0]
        for row in (
            db.query(AuthPermission.id)
            .filter(AuthPermission.code.in_(REMOVED_PERMISSION_CODES))
            .all()
        )
    ]

    if not removed_ids:
        return

    (
        db.query(AuthRolePermission)
        .filter(AuthRolePermission.permission_id.in_(removed_ids))
        .delete(synchronize_session=False)
    )
    (
        db.query(AuthPermission)
        .filter(AuthPermission.id.in_(removed_ids))
        .delete(synchronize_session=False)
    )


def assign_default_permissions(
    db: Session,
    roles_by_code: dict[str, AuthRole],
    permissions_by_code: dict[str, AuthPermission],
) -> None:
    role_permissions: dict[str, list[str]] = {
        "user": [
            "profiles.update",
            "geo.read",
            "notifications.read",
            "notifications.manage",
            "weather.public_read",
            "weather.read",
            "social.public_read",
            "social.read",
            "social.post_create",
            "social.post_manage_own",
            "social.comment_create",
            "social.comment_manage_own",
            "social.react",
            "social.bookmark",
            "social.report",
            "media.upload",
            "media.read",
            "media.private_read",
            "media.delete",
            "cart.read",
            "cart.update",
            "orders.read",
            "orders.create",
            "orders.cancel",
            "payments.read",
            "payments.create",
        ],
        "support": [
            "users.read",
            "users.read_detail",
            "shops.read",
            "shops.read_detail",
            "verification.read",
            "notifications.read",
            "notifications.manage",
            "notifications.admin_read",
            "weather.public_read",
            "weather.read",
            "weather.admin_read",
            "social.public_read",
            "social.read",
            "social.post_create",
            "social.post_manage_own",
            "social.comment_create",
            "social.comment_manage_own",
            "social.react",
            "social.bookmark",
            "social.report",
            "social.admin_read",
            "social.admin_moderate",
            "orders.admin_read",
            "payments.admin_read",
            "media.admin_read",
        ],
        "shop_owner": [
            "notifications.read",
            "notifications.manage",
            "weather.public_read",
            "weather.read",
            "social.public_read",
            "social.read",
            "social.post_create",
            "social.post_manage_own",
            "social.comment_create",
            "social.comment_manage_own",
            "social.react",
            "social.bookmark",
            "social.report",
            "media.upload",
            "media.read",
            "media.private_read",
            "media.delete",
            "media.public_read",
            "cart.read",
            "cart.update",
            "orders.read",
            "orders.create",
            "orders.cancel",
            "payments.read",
            "payments.create",
            "stores.read",
            "stores.create",
            "stores.update",
            "stores.submit",
            "stores.manage_members",
            "products.read",
            "products.create",
            "products.update",
            "products.delete",
            "products.publish",
            "products.unpublish",
            "products.manage_images",
            "orders.seller_read",
            "orders.seller_update",
        ],
        "lessor": [
            "notifications.read",
            "notifications.manage",
            "weather.public_read",
            "weather.read",
            "social.public_read",
            "social.read",
            "social.post_create",
            "social.post_manage_own",
            "social.comment_create",
            "social.comment_manage_own",
            "social.react",
            "social.bookmark",
            "social.report",
        ],
        "consultant": [
            "notifications.read",
            "notifications.manage",
            "weather.public_read",
            "weather.read",
            "social.public_read",
            "social.read",
            "social.post_create",
            "social.post_manage_own",
            "social.comment_create",
            "social.comment_manage_own",
            "social.react",
            "social.bookmark",
            "social.report",
        ],
        "verification_admin": [
            "documents.read",
            "documents.review",
            "documents.approve",
            "documents.reject",
            "verification.read",
            "verification.review",
            "verification.approve",
            "verification.reject",
            "verification.needs_revision",
            "contracts.read",
            "contracts.review_signed_pdf",
            "shops.read",
            "shops.read_detail",
            "consultants.read",
            "services.read",
        ],
        "finance_admin": [
            "finance.invoices.read",
            "finance.invoices.read_detail",
            "finance.transactions.read",
            "finance.payments.read",
            "billing.subscriptions.read",
            "commission.read",
        ],
        "content_manager": [
            "store_categories.read",
            "store_categories.create",
            "store_categories.update",
            "service_categories.read",
            "service_categories.create",
            "service_categories.update",
            "consult_specialties.read",
            "consult_specialties.create",
            "consult_specialties.update",
        ],
        "admin": [
            "dashboard.read",
            "users.read",
            "users.read_detail",
            "stores.admin_read",
            "stores.admin_review",
            "stores.approve",
            "stores.reject",
            "stores.suspend",
            "products.admin_read",
            "products.suspend",
            "products.restore",
            "orders.admin_read",
            "orders.admin_update",
            "payments.admin_read",
            "payments.admin_update",
            "commission.read",
            "commission.update",
            "media.admin_read",
            "media.admin_manage",
            "media.private_read",
            "media.public_read",
            "shops.read",
            "shops.read_detail",
            "verification.read",
            "finance.invoices.read",
            "notifications.read",
            "notifications.manage",
            "notifications.admin_read",
            "notifications.admin_manage",
            "notifications.system_message",
            "weather.public_read",
            "weather.read",
            "weather.admin_read",
            "weather.admin_manage",
            "weather.alert_manage",
            "weather.provider_manage",
            "social.public_read",
            "social.read",
            "social.post_create",
            "social.post_manage_own",
            "social.comment_create",
            "social.comment_manage_own",
            "social.react",
            "social.bookmark",
            "social.report",
            "social.admin_read",
            "social.admin_moderate",
            "social.admin_manage",
        ],
        "data_client": [
            "data_access.exports.read",
            "reports.read",
        ],
    }

    for role_code, permission_codes in role_permissions.items():
        role = roles_by_code.get(role_code)

        if role is None:
            continue

        for permission_code in permission_codes:
            permission = permissions_by_code.get(permission_code)

            if permission is None:
                raise RuntimeError(
                    f"Permission '{permission_code}' is referenced but not seeded"
                )

            exists = (
                db.query(AuthRolePermission)
                .filter(
                    AuthRolePermission.role_id == role.id,
                    AuthRolePermission.permission_id == permission.id,
                )
                .one_or_none()
            )

            if exists is None:
                db.add(
                    AuthRolePermission(
                        role_id=role.id,
                        permission_id=permission.id,
                    )
                )


def create_or_update_super_admin(
    db: Session,
    super_admin_role: AuthRole,
) -> AuthUser:
    settings = get_settings()

    email = settings.super_admin_email.strip().lower()
    raw_phone = settings.super_admin_phone
    password = settings.super_admin_password

    if not email:
        raise RuntimeError("SUPER_ADMIN_EMAIL is required")

    if not password:
        raise RuntimeError("SUPER_ADMIN_PASSWORD is required")

    phone = normalize_iran_phone(raw_phone) if raw_phone else None

    user = db.query(AuthUser).filter(AuthUser.email == email).one_or_none()

    if user is None:
        user = AuthUser(
            email=email,
            phone=phone,
            password_hash=hash_password(password),
            status=UserStatus.ACTIVE.value,
            is_email_verified=True,
            is_phone_verified=bool(phone),
        )
        db.add(user)
        db.flush()
    else:
        user.phone = phone or user.phone
        user.status = UserStatus.ACTIVE.value
        user.is_email_verified = True

        if phone:
            user.is_phone_verified = True

        # For development/bootstrap, keep password synced with env.
        user.password_hash = hash_password(password)

    exists = (
        db.query(AuthUserRole)
        .filter(
            AuthUserRole.user_id == user.id,
            AuthUserRole.role_id == super_admin_role.id,
        )
        .one_or_none()
    )

    if exists is None:
        db.add(
            AuthUserRole(
                user_id=user.id,
                role_id=super_admin_role.id,
                assigned_by=None,
            )
        )

    return user


def seed_auth(db: Session) -> dict[str, int | str]:
    roles_by_code = seed_roles(db)
    permissions_by_code = seed_permissions(db)
    retire_permissions(db)
    remove_retired_role_permissions(db, roles_by_code)
    delete_removed_permissions(db)

    super_admin_role = roles_by_code["super_admin"]

    assign_all_permissions_to_super_admin(
        db=db,
        super_admin_role=super_admin_role,
        permissions_by_code=permissions_by_code,
    )
    assign_default_permissions(
        db=db,
        roles_by_code=roles_by_code,
        permissions_by_code=permissions_by_code,
    )

    super_admin = create_or_update_super_admin(
        db=db,
        super_admin_role=super_admin_role,
    )

    db.commit()

    return {
        "roles": len(roles_by_code),
        "permissions": len(permissions_by_code),
        "super_admin_id": super_admin.id,
        "super_admin_email": super_admin.email or "",
    }
