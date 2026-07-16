import 'package:farm_net/features/services/data/service_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('ServiceOffer', () {
    test('parses public offer, provider, category and media', () {
      final offer = ServiceOffer.fromJson({
        'id': 7,
        'provider_profile_id': 3,
        'category_id': 2,
        'title': 'آزمایش خاک',
        'slug': 'soil-test',
        'pricing_type': 'fixed',
        'price_amount': '250000',
        'currency': 'TOMAN',
        'province_name': 'گلستان',
        'city_name': 'گرگان',
        'category': {'id': 2, 'title': 'آزمایشگاهی'},
        'provider': {
          'id': 3,
          'display_name': 'آزمایشگاه سبز',
          'is_verified': true,
          'completed_requests_count': 14,
        },
        'media': [
          {
            'id': 9,
            'public_url': '/api/v1/media/public/soil.jpg',
            'is_primary': true,
          },
        ],
        'primary_media': {
          'id': 9,
          'public_url': '/api/v1/media/public/soil.jpg',
          'is_primary': true,
        },
      });

      expect(offer.id, 7);
      expect(offer.priceAmount, 250000);
      expect(offer.location, 'گلستان، گرگان');
      expect(offer.category?.title, 'آزمایشگاهی');
      expect(offer.provider?.resolvedName, 'آزمایشگاه سبز');
      expect(offer.provider?.isVerified, isTrue);
      expect(offer.primaryMedia?.publicUrl, contains('soil.jpg'));
    });

    test('handles optional public fields and negotiable pricing', () {
      final offer = ServiceOffer.fromJson({
        'id': 8,
        'provider_profile_id': 4,
        'title': 'برداشت محصول',
        'pricing_type': 'negotiable',
        'currency': 'TOMAN',
      });

      expect(offer.media, isEmpty);
      expect(offer.primaryMedia, isNull);
      expect(offer.provider, isNull);
      expect(offer.location, isEmpty);
      expect(offer.priceAmount, isNull);
    });
  });

  test('provider summary has safe name and location fallbacks', () {
    final provider = ServiceProviderSummary.fromJson({
      'id': 1,
      'name': 'گروه خدمات مزرعه',
      'province_name': 'فارس',
      'city_name': 'شیراز',
    });
    expect(provider.resolvedName, 'گروه خدمات مزرعه');
    expect(provider.location, 'فارس، شیراز');
    expect(provider.completedRequestsCount, 0);
  });

  group('ServiceRequest', () {
    test('parses hardened detail and exact status log names', () {
      final request = ServiceRequest.fromJson({
        'id': 21,
        'offer_id': 7,
        'offer_title': 'آزمایش خاک',
        'provider_display_name': 'آزمایشگاه سبز',
        'title': 'آزمایش زمین شمالی',
        'description': 'نمونه‌برداری و آزمایش کامل خاک',
        'contact_method': 'in_app',
        'status': 'accepted',
        'budget_amount': '350000.00',
        'currency': 'TOMAN',
        'created_at': '2026-07-16T10:00:00',
        'status_logs': [
          {
            'id': 1,
            'old_status': 'open',
            'new_status': 'accepted',
            'note': 'پذیرفته شد',
            'created_at': '2026-07-16T11:00:00',
          },
        ],
      });
      expect(request.canCancel, isTrue);
      expect(request.budgetAmount, 350000);
      expect(request.statusLogs.single.oldStatus, 'open');
      expect(request.statusLogs.single.newStatus, 'accepted');
    });

    test('terminal requests cannot be cancelled', () {
      final request = ServiceRequest.fromJson({
        'id': 22,
        'title': 'برداشت',
        'status': 'completed',
        'currency': 'TOMAN',
        'created_at': '2026-07-16T10:00:00',
      });
      expect(request.canCancel, isFalse);
    });

    test('serializes only populated create fields', () {
      const input = ServiceRequestInput(
        offerId: 7,
        title: 'آزمایش خاک',
        description: 'آزمایش کامل زمین',
        contactMethod: 'visit',
        provinceId: 1,
        provinceName: 'تهران',
      );
      expect(input.toJson()['offer_id'], 7);
      expect(input.toJson()['contact_method'], 'visit');
      expect(input.toJson()['province_name'], 'تهران');
      expect(input.toJson().containsKey('city_id'), isFalse);
      expect(input.toJson().containsKey('budget_amount'), isFalse);
    });
  });
}
