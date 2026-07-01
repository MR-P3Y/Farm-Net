import 'package:farm_net/features/consultants/data/consultant_models.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  group('ConsultantProfileModel', () {
    test('parses public consultant list item safely', () {
      final consultant = ConsultantProfileModel.fromJson({
        'consultant_id': 12,
        'user_id': 4,
        'display_name': 'مشاور خاک',
        'title': 'متخصص تغذیه گیاه',
        'province_name': 'گلستان',
        'city_name': 'گرگان',
        'status': 'approved',
        'is_verified': true,
        'is_featured': false,
        'rating_average': 4.5,
        'reviews_count': 8,
        'requests_count': 19,
        'completed_requests_count': 15,
        'specialties': [
          {'id': 2, 'code': 'soil', 'title': 'خاک'},
        ],
      });

      expect(consultant.id, 12);
      expect(consultant.resolvedName, 'مشاور خاک');
      expect(consultant.locationText, 'گلستان، گرگان');
      expect(consultant.specialties.single.title, 'خاک');
    });

    test('falls back when optional public fields are missing', () {
      final consultant = ConsultantProfileModel.fromJson({
        'id': 9,
        'user_id': 5,
      });

      expect(consultant.id, 9);
      expect(consultant.resolvedName, 'مشاور');
      expect(consultant.locationText, 'موقعیت ثبت نشده');
      expect(consultant.specialties, isEmpty);
    });

    test('parses owner-only consultant profile fields for me profile', () {
      final consultant = ConsultantProfileModel.fromJson({
        'id': 15,
        'user_id': 9,
        'display_name': 'مشاور باغبانی',
        'phone': '09120000000',
        'email': 'consultant@example.com',
        'status': 'rejected',
        'is_verified': false,
        'is_featured': false,
        'rating_average': 0,
        'reviews_count': 0,
        'requests_count': 0,
        'completed_requests_count': 0,
        'admin_note': 'نیاز به تکمیل توضیحات',
        'submitted_at': '2026-07-01T10:00:00',
      });

      expect(consultant.phone, '09120000000');
      expect(consultant.email, 'consultant@example.com');
      expect(consultant.adminNote, 'نیاز به تکمیل توضیحات');
      expect(consultant.submittedAt, '2026-07-01T10:00:00');
    });

    test('serializes consultant profile input for save API', () {
      const input = ConsultantProfileInput(
        displayName: 'مشاور خاک',
        title: 'متخصص تغذیه گیاه',
        bio: 'تجربه مشاوره باغ و زراعت',
        experienceYears: 8,
        phone: '09120000000',
        email: 'consultant@example.com',
        provinceName: 'گلستان',
        cityName: 'گرگان',
        specialtyIds: [2, 5],
      );

      expect(input.toJson(), {
        'display_name': 'مشاور خاک',
        'title': 'متخصص تغذیه گیاه',
        'bio': 'تجربه مشاوره باغ و زراعت',
        'experience_years': 8,
        'phone': '09120000000',
        'email': 'consultant@example.com',
        'province_name': 'گلستان',
        'city_name': 'گرگان',
        'specialty_ids': [2, 5],
      });
    });
  });

  group('ConsultationRequestModel', () {
    test('parses nested consultant and specialty safely', () {
      final request = ConsultationRequestModel.fromJson({
        'id': 31,
        'requester_user_id': 7,
        'consultant_profile_id': 12,
        'specialty_id': 2,
        'title': 'زردی برگ',
        'description': 'برگ‌ها زرد شده‌اند و رشد کم شده است.',
        'contact_method': 'in_app',
        'status': 'open',
        'budget_amount': '2500000.00',
        'currency': 'IRR',
        'created_at': '2026-06-30T10:00:00',
        'updated_at': '2026-06-30T10:00:00',
        'consultant': {
          'id': 12,
          'user_id': 4,
          'display_name': 'مشاور خاک',
          'status': 'approved',
          'is_verified': true,
          'is_featured': false,
          'rating_average': 4.5,
          'reviews_count': 8,
          'requests_count': 19,
          'completed_requests_count': 15,
          'specialties': [],
        },
        'specialty': {'id': 2, 'code': 'soil', 'title': 'خاک'},
      });

      expect(request.id, 31);
      expect(request.canCancel, isTrue);
      expect(request.consultant?.resolvedName, 'مشاور خاک');
      expect(request.specialty?.title, 'خاک');
    });

    test('cancelled requests cannot be cancelled again', () {
      final request = ConsultationRequestModel.fromJson({
        'id': 32,
        'requester_user_id': 7,
        'title': 'درخواست لغوشده',
        'description': 'این درخواست قبلاً لغو شده است.',
        'contact_method': 'phone',
        'status': 'cancelled',
        'currency': 'IRR',
        'created_at': '2026-06-30T10:00:00',
        'updated_at': '2026-06-30T10:00:00',
      });

      expect(request.canCancel, isFalse);
      expect(request.consultant, isNull);
      expect(request.specialty, isNull);
    });

    test('consultant workbench exposes valid next status actions', () {
      final openRequest = ConsultationRequestModel.fromJson({
        'id': 33,
        'requester_user_id': 7,
        'title': 'درخواست باز',
        'description': 'برای میزکار مشاور',
        'contact_method': 'in_app',
        'status': 'open',
        'currency': 'IRR',
        'created_at': '2026-06-30T10:00:00',
        'updated_at': '2026-06-30T10:00:00',
      });
      final completedRequest = ConsultationRequestModel.fromJson({
        'id': 34,
        'requester_user_id': 7,
        'title': 'درخواست تکمیل‌شده',
        'description': 'دیگر قابل مدیریت نیست.',
        'contact_method': 'in_app',
        'status': 'completed',
        'currency': 'IRR',
        'created_at': '2026-06-30T10:00:00',
        'updated_at': '2026-06-30T10:00:00',
      });

      expect(openRequest.consultantNextStatuses, ['accepted', 'rejected']);
      expect(openRequest.canConsultantManage, isTrue);
      expect(completedRequest.consultantNextStatuses, isEmpty);
      expect(completedRequest.canConsultantManage, isFalse);
    });
  });
}
