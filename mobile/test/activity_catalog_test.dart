import 'package:farm_net/features/activity/data/activity_catalog.dart';
import 'package:farm_net/features/auth/data/auth_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  AuthUser user({
    List<String> roles = const ['user'],
    List<String> permissions = const [],
  }) => AuthUser(
    id: 1,
    status: 'active',
    isEmailVerified: true,
    isPhoneVerified: true,
    roles: roles,
    permissions: permissions,
  );

  test('personal actions are permission aware and always include identity', () {
    final sections = ActivityCatalog.forUser(
      user(
        permissions: const [
          'notifications.read',
          'orders.read',
          'reviews.read_own',
        ],
      ),
    );

    expect(sections.single.kind, ActivitySectionKind.personal);
    expect(
      sections.single.actions.map((action) => action.id),
      containsAll([
        ActivityActionId.profile,
        ActivityActionId.verifications,
        ActivityActionId.notifications,
        ActivityActionId.buyerOrders,
        ActivityActionId.reviews,
      ]),
    );
    expect(
      sections.single.actions.map((action) => action.id),
      isNot(contains(ActivityActionId.finance)),
    );
  });

  test('base user sees provider setup without assigned workbench actions', () {
    final sections = ActivityCatalog.forUser(
      user(
        permissions: const [
          'service_providers.profile_manage',
          'consultants.profile_manage',
        ],
      ),
    );

    final service = sections.firstWhere(
      (section) => section.kind == ActivitySectionKind.services,
    );
    final consultant = sections.firstWhere(
      (section) => section.kind == ActivitySectionKind.consultant,
    );
    expect(service.isSetupSection, isTrue);
    expect(consultant.isSetupSection, isTrue);
    expect(service.actions.single.id, ActivityActionId.serviceProviderProfile);
    expect(consultant.actions.single.id, ActivityActionId.consultantProfile);
  });

  test('approved shop owner receives only permission-backed actions', () {
    final sections = ActivityCatalog.forUser(
      user(
        roles: const ['user', 'shop_owner'],
        permissions: const [
          'stores.update',
          'products.read',
          'orders.seller_read',
        ],
      ),
    );
    final shop = sections.firstWhere(
      (section) => section.kind == ActivitySectionKind.shop,
    );

    expect(shop.isSetupSection, isFalse);
    expect(shop.actions.map((action) => action.id), [
      ActivityActionId.shopProfile,
      ActivityActionId.shopProducts,
      ActivityActionId.sellerOrders,
    ]);
  });

  test('approved service provider receives profile offers and workbench', () {
    final sections = ActivityCatalog.forUser(
      user(
        roles: const ['user', 'service_provider'],
        permissions: const [
          'service_providers.profile_manage',
          'service_offers.create',
          'service_offers.update',
          'service_requests.manage_assigned',
        ],
      ),
    );
    final services = sections.firstWhere(
      (section) => section.kind == ActivitySectionKind.services,
    );

    expect(services.isSetupSection, isFalse);
    expect(services.actions.map((action) => action.id), [
      ActivityActionId.serviceProviderProfile,
      ActivityActionId.serviceOffers,
      ActivityActionId.serviceWorkbench,
    ]);
  });

  test('approved lessor receives profile equipment and workbench', () {
    final sections = ActivityCatalog.forUser(
      user(
        roles: const ['user', 'lessor'],
        permissions: const [
          'rental_lessors.profile_manage',
          'rental_equipment.create',
          'rental_equipment.manage_pricing',
          'rental_requests.manage_assigned',
        ],
      ),
    );
    final rental = sections.firstWhere(
      (section) => section.kind == ActivitySectionKind.rental,
    );

    expect(rental.isSetupSection, isFalse);
    expect(rental.actions.map((action) => action.id), [
      ActivityActionId.lessorProfile,
      ActivityActionId.rentalEquipment,
      ActivityActionId.rentalWorkbench,
    ]);
  });

  test('approved consultant receives profile and assigned workbench', () {
    final sections = ActivityCatalog.forUser(
      user(
        roles: const ['user', 'consultant'],
        permissions: const [
          'consultants.profile_manage',
          'consult_requests.manage_assigned',
        ],
      ),
    );
    final consultant = sections.firstWhere(
      (section) => section.kind == ActivitySectionKind.consultant,
    );

    expect(consultant.isSetupSection, isFalse);
    expect(consultant.actions.map((action) => action.id), [
      ActivityActionId.consultantProfile,
      ActivityActionId.consultantWorkbench,
    ]);
  });

  test('multi-role user receives independent ordered role sections', () {
    final sections = ActivityCatalog.forUser(
      user(
        roles: const ['user', 'service_provider', 'lessor', 'consultant'],
        permissions: const [
          'service_providers.profile_manage',
          'service_requests.manage_assigned',
          'rental_lessors.profile_manage',
          'rental_requests.manage_assigned',
          'consultants.profile_manage',
          'consult_requests.manage_assigned',
        ],
      ),
    );

    expect(sections.map((section) => section.kind), [
      ActivitySectionKind.personal,
      ActivitySectionKind.services,
      ActivitySectionKind.rental,
      ActivitySectionKind.consultant,
    ]);
    expect(
      sections.skip(1).every((section) => !section.isSetupSection),
      isTrue,
    );
  });

  test('professional role journeys are complete ordered and role driven', () {
    final journeys = ActivityCatalog.professionalRolesForUser(
      user(
        roles: const [
          'user',
          'consultant',
          'shop_owner',
          'consultant',
          'admin',
        ],
      ),
    );

    expect(journeys.map((journey) => journey.roleCode), [
      'shop_owner',
      'service_provider',
      'lessor',
      'consultant',
    ]);
    expect(
      journeys
          .where((journey) => journey.isActive)
          .map((journey) => journey.roleCode),
      ['shop_owner', 'consultant'],
    );
    expect(
      journeys.firstWhere((journey) => journey.roleCode == 'lessor').setupRoute,
      '/verifications',
    );
    expect(
      journeys
          .firstWhere((journey) => journey.roleCode == 'service_provider')
          .setupRoute,
      '/services/me/provider-profile',
    );
  });
}
