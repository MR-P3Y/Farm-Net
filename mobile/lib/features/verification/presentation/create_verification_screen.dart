import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_button.dart';
import '../../../core/widgets/farm_text_field.dart';
import '../../documents/data/document_models.dart';
import '../../media/presentation/media_upload_button.dart';
import '../data/verification_models.dart';
import '../state/verification_controller.dart';

class CreateVerificationScreen extends ConsumerStatefulWidget {
  const CreateVerificationScreen({super.key});

  @override
  ConsumerState<CreateVerificationScreen> createState() =>
      _CreateVerificationScreenState();
}

class _CreateVerificationScreenState
    extends ConsumerState<CreateVerificationScreen> {
  String _targetRole = 'consultant';
  String _documentType = 'national_card';
  String? _documentMediaFileKey;

  final _requestNoteController = TextEditingController(
    text: 'درخواست تأیید نقش در فارم نت',
  );
  final _filePathController = TextEditingController(
    text: 'storage/documents/users/me/national-card.jpg',
  );
  final _fileNameController = TextEditingController(text: 'national-card.jpg');
  final _mimeTypeController = TextEditingController(text: 'image/jpeg');
  final _sizeBytesController = TextEditingController(text: '345000');

  @override
  void dispose() {
    _requestNoteController.dispose();
    _filePathController.dispose();
    _fileNameController.dispose();
    _mimeTypeController.dispose();
    _sizeBytesController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final size = int.tryParse(_sizeBytesController.text.trim());

    final ok = await ref
        .read(verificationControllerProvider.notifier)
        .createDocumentAndSubmitVerification(
          documentInput: DocumentCreateInput(
            documentType: _documentType,
            filePath: _filePathController.text.trim(),
            fileName: _fileNameController.text.trim(),
            mimeType: _mimeTypeController.text.trim(),
            sizeBytes: size,
            mediaFileKey: _documentMediaFileKey,
          ),
          verificationInput: VerificationCreateInput(
            targetRole: _targetRole,
            requestNote: _requestNoteController.text.trim(),
          ),
        );

    if (!ok || !mounted) return;

    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(verificationControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('درخواست تأیید جدید'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: ResponsiveBuilder(
        builder: (context, constraints, r) {
          return SingleChildScrollView(
            padding: r.pagePadding(),
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 720),
                child: Card(
                  child: Padding(
                    padding: EdgeInsets.all(r.s(20)),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Text(
                          'اطلاعات درخواست',
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                        SizedBox(height: r.v(16)),
                        DropdownButtonFormField<String>(
                          value: _targetRole,
                          decoration: const InputDecoration(
                            labelText: 'نقش درخواستی',
                            border: OutlineInputBorder(),
                          ),
                          items: const [
                            DropdownMenuItem(
                              value: 'shop_owner',
                              child: Text('فروشگاه‌دار'),
                            ),
                            DropdownMenuItem(
                              value: 'lessor',
                              child: Text('موجر ادوات'),
                            ),
                            DropdownMenuItem(
                              value: 'consultant',
                              child: Text('مشاور'),
                            ),
                            DropdownMenuItem(
                              value: 'service_provider',
                              child: Text('ارائه‌دهنده خدمات'),
                            ),
                            DropdownMenuItem(
                              value: 'data_client',
                              child: Text('مشتری داده'),
                            ),
                          ],
                          onChanged: (value) {
                            if (value == null) return;
                            setState(() => _targetRole = value);
                          },
                        ),
                        SizedBox(height: r.v(12)),
                        FarmTextField(
                          controller: _requestNoteController,
                          label: 'توضیح درخواست',
                          maxLines: 3,
                        ),
                        SizedBox(height: r.v(24)),
                        Text(
                          'metadata سند موقت',
                          style: Theme.of(context).textTheme.titleMedium,
                        ),
                        SizedBox(height: r.v(12)),
                        DropdownButtonFormField<String>(
                          value: _documentType,
                          decoration: const InputDecoration(
                            labelText: 'نوع سند',
                            border: OutlineInputBorder(),
                          ),
                          items: const [
                            DropdownMenuItem(
                              value: 'national_card',
                              child: Text('کارت ملی'),
                            ),
                            DropdownMenuItem(
                              value: 'business_license',
                              child: Text('مجوز کسب‌وکار'),
                            ),
                            DropdownMenuItem(
                              value: 'agriculture_certificate',
                              child: Text('گواهی کشاورزی'),
                            ),
                            DropdownMenuItem(
                              value: 'consultant_certificate',
                              child: Text('گواهی مشاوره'),
                            ),
                            DropdownMenuItem(
                              value: 'equipment_ownership',
                              child: Text('مالکیت ادوات'),
                            ),
                            DropdownMenuItem(
                              value: 'driver_license',
                              child: Text('گواهینامه راننده'),
                            ),
                            DropdownMenuItem(
                              value: 'contract_signed_pdf',
                              child: Text('قرارداد امضا شده'),
                            ),
                            DropdownMenuItem(
                              value: 'other',
                              child: Text('سایر'),
                            ),
                          ],
                          onChanged: (value) {
                            if (value == null) return;
                            setState(() => _documentType = value);
                          },
                        ),
                        SizedBox(height: r.v(12)),
                        MediaUploadButton(
                          label: 'آپلود مدرک',
                          purpose: 'verification_document',
                          visibility: 'private',
                          allowedExtensions: const [
                            'pdf',
                            'jpg',
                            'jpeg',
                            'png',
                            'webp',
                          ],
                          onUploaded: (media) {
                            setState(() {
                              _documentMediaFileKey = media.fileKey;
                              _fileNameController.text = media.originalFilename;
                              _mimeTypeController.text = media.mimeType;
                              _sizeBytesController.text =
                                  media.sizeBytes.toString();
                              _filePathController.text =
                                  media.privateUrl ?? media.relativePath;
                            });
                          },
                        ),
                        if (_documentMediaFileKey != null) ...[
                          SizedBox(height: r.v(8)),
                          const Text('مدرک آپلود شد.'),
                        ],
                        SizedBox(height: r.v(12)),
                        FarmTextField(
                          controller: _filePathController,
                          label: 'مسیر فایل',
                        ),
                        SizedBox(height: r.v(12)),
                        FarmTextField(
                          controller: _fileNameController,
                          label: 'نام فایل',
                        ),
                        SizedBox(height: r.v(12)),
                        FarmTextField(
                          controller: _mimeTypeController,
                          label: 'MIME Type',
                        ),
                        SizedBox(height: r.v(12)),
                        FarmTextField(
                          controller: _sizeBytesController,
                          label: 'حجم فایل به بایت',
                          keyboardType: TextInputType.number,
                        ),
                        if (state.errorMessage != null) ...[
                          SizedBox(height: r.v(12)),
                          Text(
                            state.errorMessage!,
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: Theme.of(context).colorScheme.error,
                            ),
                          ),
                        ],
                        SizedBox(height: r.v(20)),
                        FarmButton(
                          label: 'ثبت و ارسال درخواست',
                          isLoading: state.isSaving,
                          onPressed: state.isSaving ? null : _submit,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
