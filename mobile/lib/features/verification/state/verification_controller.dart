import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../documents/data/document_api.dart';
import '../../documents/data/document_models.dart';
import '../../documents/data/document_repository.dart';
import '../data/verification_api.dart';
import '../data/verification_models.dart';
import '../data/verification_repository.dart';
import 'verification_state.dart';

final verificationControllerProvider =
    StateNotifierProvider<VerificationController, VerificationState>((ref) {
      return VerificationController(
        documentRepository: ref.watch(documentRepositoryProvider),
        verificationRepository: ref.watch(verificationRepositoryProvider),
      );
    });

class VerificationController extends StateNotifier<VerificationState> {
  VerificationController({
    required DocumentRepository documentRepository,
    required VerificationRepository verificationRepository,
  }) : _documentRepository = documentRepository,
       _verificationRepository = verificationRepository,
       super(VerificationState.initial());

  final DocumentRepository _documentRepository;
  final VerificationRepository _verificationRepository;

  Future<void> load() async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final requestsFuture = _verificationRepository.listMine();
      final documentsFuture = _documentRepository.listMyDocuments();

      final requests = await requestsFuture;
      final documents = await documentsFuture;

      state = state.copyWith(
        isLoading: false,
        requests: requests,
        documents: documents,
      );
    } on VerificationApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } on DocumentApiException catch (error) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: error.error.message,
      );
    } catch (_) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'خطا در دریافت درخواست‌های تأیید',
      );
    }
  }

  Future<bool> createDocumentAndSubmitVerification({
    required DocumentCreateInput documentInput,
    required VerificationCreateInput verificationInput,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final document = await _documentRepository.createDocument(documentInput);
      final verification = await _verificationRepository.create(
        verificationInput,
      );

      await _verificationRepository.attachDocument(
        requestId: verification.id,
        documentId: document.id,
      );

      await _verificationRepository.submit(requestId: verification.id);

      final requestsFuture = _verificationRepository.listMine();
      final documentsFuture = _documentRepository.listMyDocuments();

      final requests = await requestsFuture;
      final documents = await documentsFuture;

      state = state.copyWith(
        isLoading: false,
        isSaving: false,
        requests: requests,
        documents: documents,
      );

      return true;
    } on VerificationApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
      return false;
    } on DocumentApiException catch (error) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: error.error.message,
      );
      return false;
    } catch (_) {
      state = state.copyWith(
        isSaving: false,
        errorMessage: 'خطا در ثبت درخواست تأیید',
      );
      return false;
    }
  }
}
