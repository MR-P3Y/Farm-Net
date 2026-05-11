import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'document_api.dart';
import 'document_models.dart';

final documentRepositoryProvider = Provider<DocumentRepository>((ref) {
  return DocumentRepository(api: DocumentApi());
});

class DocumentRepository {
  DocumentRepository({required DocumentApi api}) : _api = api;

  final DocumentApi _api;

  Future<List<UserDocument>> listMyDocuments() {
    return _api.listMyDocuments();
  }

  Future<UserDocument> createDocument(DocumentCreateInput input) {
    return _api.createDocument(input);
  }
}
