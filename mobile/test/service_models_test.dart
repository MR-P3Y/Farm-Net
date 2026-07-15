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
}
