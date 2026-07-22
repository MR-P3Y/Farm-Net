import '../../auth/data/auth_models.dart';

enum ActivitySectionKind { personal, shop, services, rental, consultant }

enum ActivityActionId {
  profile,
  verifications,
  notifications,
  finance,
  buyerOrders,
  serviceRequests,
  rentalRequests,
  consultationRequests,
  shopProfile,
  shopProducts,
  sellerOrders,
  serviceProviderProfile,
  serviceOffers,
  serviceWorkbench,
  lessorProfile,
  rentalEquipment,
  rentalWorkbench,
  consultantProfile,
  consultantWorkbench,
}

class ActivityAction {
  const ActivityAction({
    required this.id,
    required this.title,
    required this.route,
  });

  final ActivityActionId id;
  final String title;
  final String route;
}

class ActivitySection {
  const ActivitySection({
    required this.kind,
    required this.title,
    required this.actions,
    this.roleCode,
    this.isSetupSection = false,
  });

  final ActivitySectionKind kind;
  final String title;
  final String? roleCode;
  final bool isSetupSection;
  final List<ActivityAction> actions;
}

class ProfessionalRoleJourney {
  const ProfessionalRoleJourney({
    required this.roleCode,
    required this.title,
    required this.isActive,
    required this.setupRoute,
    required this.setupLabel,
  });

  final String roleCode;
  final String title;
  final bool isActive;
  final String setupRoute;
  final String setupLabel;
}

class ActivityCatalog {
  ActivityCatalog._();

  static List<ActivitySection> forUser(AuthUser user) {
    final permissions = user.permissions.toSet();
    final roles = user.roles.toSet();
    final sections = <ActivitySection>[
      ActivitySection(
        kind: ActivitySectionKind.personal,
        title: 'فعالیت‌های شخصی من',
        actions: [
          const ActivityAction(
            id: ActivityActionId.profile,
            title: 'پروفایل من',
            route: '/profile',
          ),
          const ActivityAction(
            id: ActivityActionId.verifications,
            title: 'تأیید هویت و مدارک',
            route: '/verifications',
          ),
          if (_has(permissions, 'notifications.read'))
            const ActivityAction(
              id: ActivityActionId.notifications,
              title: 'اعلان‌های من',
              route: '/notifications',
            ),
          if (_has(permissions, 'wallet.read_own'))
            const ActivityAction(
              id: ActivityActionId.finance,
              title: 'مرکز مالی من',
              route: '/finance',
            ),
          if (_has(permissions, 'orders.read'))
            const ActivityAction(
              id: ActivityActionId.buyerOrders,
              title: 'سفارش‌های خرید من',
              route: '/orders',
            ),
          if (_has(permissions, 'service_requests.read_own'))
            const ActivityAction(
              id: ActivityActionId.serviceRequests,
              title: 'درخواست‌های خدمات من',
              route: '/services/requests',
            ),
          if (_has(permissions, 'rental_requests.read_own'))
            const ActivityAction(
              id: ActivityActionId.rentalRequests,
              title: 'درخواست‌های اجاره من',
              route: '/rentals/requests',
            ),
          if (_has(permissions, 'consult_requests.read_own'))
            const ActivityAction(
              id: ActivityActionId.consultationRequests,
              title: 'درخواست‌های مشاوره من',
              route: '/consultants/requests',
            ),
        ],
      ),
    ];

    _addSection(
      sections,
      roles: roles,
      permissions: permissions,
      roleCode: 'shop_owner',
      kind: ActivitySectionKind.shop,
      title: 'فروشگاه و فروش من',
      setupPermissions: const {'stores.create', 'stores.update'},
      actions: [
        if (_hasAny(permissions, const {'stores.create', 'stores.update'}))
          const ActivityAction(
            id: ActivityActionId.shopProfile,
            title: 'فروشگاه من',
            route: '/my-store',
          ),
        if (_hasAny(permissions, const {'products.read', 'products.create'}))
          const ActivityAction(
            id: ActivityActionId.shopProducts,
            title: 'محصولات من',
            route: '/my-products',
          ),
        if (_has(permissions, 'orders.seller_read'))
          const ActivityAction(
            id: ActivityActionId.sellerOrders,
            title: 'سفارش‌های فروش من',
            route: '/seller/orders',
          ),
      ],
    );

    _addSection(
      sections,
      roles: roles,
      permissions: permissions,
      roleCode: 'service_provider',
      kind: ActivitySectionKind.services,
      title: 'فعالیت خدمات‌دهندگی من',
      setupPermissions: const {'service_providers.profile_manage'},
      actions: [
        if (_has(permissions, 'service_providers.profile_manage'))
          const ActivityAction(
            id: ActivityActionId.serviceProviderProfile,
            title: 'پروفایل خدمات‌دهنده',
            route: '/services/me/provider-profile',
          ),
        if (_hasAny(permissions, const {
          'service_offers.create',
          'service_offers.update',
          'service_offers.submit',
        }))
          const ActivityAction(
            id: ActivityActionId.serviceOffers,
            title: 'خدمات قابل ارائه من',
            route: '/services/me/offers',
          ),
        if (_has(permissions, 'service_requests.manage_assigned'))
          const ActivityAction(
            id: ActivityActionId.serviceWorkbench,
            title: 'میزکار درخواست‌های خدمات',
            route: '/services/workbench',
          ),
      ],
    );

    _addSection(
      sections,
      roles: roles,
      permissions: permissions,
      roleCode: 'lessor',
      kind: ActivitySectionKind.rental,
      title: 'فعالیت اجاره‌دهندگی من',
      setupPermissions: const {'rental_lessors.profile_manage'},
      actions: [
        if (_has(permissions, 'rental_lessors.profile_manage'))
          const ActivityAction(
            id: ActivityActionId.lessorProfile,
            title: 'پروفایل موجر',
            route: '/rentals/me/lessor-profile',
          ),
        if (_hasAny(permissions, const {
          'rental_equipment.create',
          'rental_equipment.update',
        }))
          const ActivityAction(
            id: ActivityActionId.rentalEquipment,
            title: 'تجهیزات اجاره‌ای من',
            route: '/rentals/me/equipment',
          ),
        if (_has(permissions, 'rental_requests.manage_assigned'))
          const ActivityAction(
            id: ActivityActionId.rentalWorkbench,
            title: 'میزکار درخواست‌های اجاره',
            route: '/rentals/workbench',
          ),
      ],
    );

    _addSection(
      sections,
      roles: roles,
      permissions: permissions,
      roleCode: 'consultant',
      kind: ActivitySectionKind.consultant,
      title: 'فعالیت مشاوره من',
      setupPermissions: const {'consultants.profile_manage'},
      actions: [
        if (_has(permissions, 'consultants.profile_manage'))
          const ActivityAction(
            id: ActivityActionId.consultantProfile,
            title: 'پروفایل مشاور',
            route: '/consultants/me/profile',
          ),
        if (_has(permissions, 'consult_requests.manage_assigned'))
          const ActivityAction(
            id: ActivityActionId.consultantWorkbench,
            title: 'میزکار درخواست‌های مشاوره',
            route: '/consultants/workbench',
          ),
      ],
    );

    return List.unmodifiable(sections);
  }

  static List<ProfessionalRoleJourney> professionalRolesForUser(AuthUser user) {
    final roles = user.roles.toSet();
    return List.unmodifiable([
      ProfessionalRoleJourney(
        roleCode: 'shop_owner',
        title: 'فروشنده و مالک فروشگاه',
        isActive: roles.contains('shop_owner'),
        setupRoute: '/verifications',
        setupLabel: 'درخواست تأیید فروشندگی',
      ),
      ProfessionalRoleJourney(
        roleCode: 'service_provider',
        title: 'خدمات‌دهنده کشاورزی',
        isActive: roles.contains('service_provider'),
        setupRoute: '/services/me/provider-profile',
        setupLabel: 'تکمیل پروفایل خدمات‌دهنده',
      ),
      ProfessionalRoleJourney(
        roleCode: 'lessor',
        title: 'موجر تجهیزات',
        isActive: roles.contains('lessor'),
        setupRoute: '/verifications',
        setupLabel: 'درخواست تأیید موجر',
      ),
      ProfessionalRoleJourney(
        roleCode: 'consultant',
        title: 'مشاور کشاورزی',
        isActive: roles.contains('consultant'),
        setupRoute: '/consultants/me/profile',
        setupLabel: 'تکمیل پروفایل مشاور',
      ),
    ]);
  }

  static void _addSection(
    List<ActivitySection> sections, {
    required Set<String> roles,
    required Set<String> permissions,
    required String roleCode,
    required ActivitySectionKind kind,
    required String title,
    required Set<String> setupPermissions,
    required List<ActivityAction> actions,
  }) {
    if (actions.isEmpty) return;
    final hasRole = roles.contains(roleCode);
    final canSetUp = _hasAny(permissions, setupPermissions);
    if (!hasRole && !canSetUp) return;

    sections.add(
      ActivitySection(
        kind: kind,
        title: title,
        roleCode: roleCode,
        isSetupSection: !hasRole,
        actions: List.unmodifiable(actions),
      ),
    );
  }

  static bool _has(Set<String> permissions, String permission) =>
      permissions.contains(permission);

  static bool _hasAny(Set<String> permissions, Set<String> required) =>
      required.any(permissions.contains);
}
