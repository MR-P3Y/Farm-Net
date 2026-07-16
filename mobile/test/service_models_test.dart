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

  test('owner provider profile parses moderation fields and helpers', () {
    final profile = ServiceProviderProfileOwner.fromJson({
      'id': 4,
      'user_id': 9,
      'status': 'rejected',
      'display_name': 'گروه خدمات سبز',
      'admin_note': 'تکمیل سوابق',
      'categories': [
        {'id': 2, 'title': 'سم‌پاشی'},
      ],
    });
    expect(profile.canEdit, isTrue);
    expect(profile.canSubmit, isTrue);
    expect(profile.isApproved, isFalse);
    expect(profile.statusLabelFa, 'ردشده');
    expect(profile.adminNote, 'تکمیل سوابق');
    expect(profile.categories.single.id, 2);
  });

  test('provider profile input serializes category and media IDs', () {
    const input = ServiceProviderProfileInput(
      categoryIds: [2, 5],
      displayName: 'خدمات سبز',
      avatarMediaFileId: 18,
    );
    expect(input.toJson()['category_ids'], [2, 5]);
    expect(input.toJson()['avatar_media_file_id'], 18);
  });

  test('owner offer parses media and submit eligibility', () {
    final offer = ServiceOfferOwner.fromJson({
      'id': 7,
      'provider_profile_id': 4,
      'title': 'سم‌پاشی',
      'slug': 'spraying',
      'status': 'draft',
      'pricing_type': 'hectare',
      'price_amount': '500000',
      'currency': 'TOMAN',
      'media': [
        {'id': 3, 'media_file_id': 19, 'is_primary': true},
      ],
    });
    expect(offer.canEdit, isTrue);
    expect(offer.canSubmit, isTrue);
    expect(offer.media.single.mediaFileId, 19);
    expect(offer.priceAmount, 500000);
  });

  test('offer input maps uploaded media to backend contract', () {
    const input = ServiceOfferInput(
      title: 'سم‌پاشی',
      slug: 'spraying',
      pricingType: 'fixed',
      priceAmount: 100,
      mediaFileIds: [11, 12],
    );
    final media = input.toJson()['media_items'] as List;
    expect(media.first['media_file_id'], 11);
    expect(media.first['is_primary'], isTrue);
    expect(media.last['is_primary'], isFalse);
  });

  group('provider workbench', () {
    test('parses assigned request operational fields and timeline', () {
      final request = ServiceRequest.fromJson({
        'id': 91,
        'requester_user_id': 12,
        'offer_title': 'سم‌پاشی',
        'category_title': 'عملیات مزرعه',
        'title': 'سم‌پاشی باغ',
        'status': 'open',
        'currency': 'TOMAN',
        'province_name': 'فارس',
        'city_name': 'شیراز',
        'created_at': '2026-07-16T08:00:00',
        'status_logs': [
          {
            'id': 1,
            'old_status': null,
            'new_status': 'open',
            'created_at': '2026-07-16T08:00:00',
          },
        ],
      });
      expect(request.requesterUserId, 12);
      expect(request.offerTitle, 'سم‌پاشی');
      expect(request.statusLogs.single.oldStatus, isNull);
      expect(request.canAccept, isTrue);
      expect(request.canReject, isTrue);
    });

    test('provider transitions expose only valid actions', () {
      ServiceRequest request(String status) => ServiceRequest.fromJson({
        'id': 1,
        'title': 'کار',
        'status': status,
        'currency': 'TOMAN',
        'created_at': '2026-07-16T08:00:00',
      });
      expect(request('open').providerNextStatuses, ['accepted', 'rejected']);
      expect(request('accepted').providerNextStatuses, ['in_progress']);
      expect(request('in_progress').providerNextStatuses, ['completed']);
      for (final status in ['completed', 'rejected', 'cancelled']) {
        expect(request(status).providerNextStatuses, isEmpty);
      }
      expect(request('in_progress').statusLabelFa, 'در حال انجام');
    });

    test('status update payload omits empty note', () {
      const empty = ServiceRequestStatusUpdateInput(
        status: 'accepted',
        note: ' ',
      );
      const noted = ServiceRequestStatusUpdateInput(
        status: 'rejected',
        note: 'نامناسب',
      );
      expect(empty.toJson(), {'status': 'accepted'});
      expect(noted.toJson(), {'status': 'rejected', 'note': 'نامناسب'});
    });
  });
}
