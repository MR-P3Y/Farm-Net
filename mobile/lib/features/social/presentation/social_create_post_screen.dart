import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../state/social_controller.dart';

class SocialCreatePostScreen extends ConsumerStatefulWidget {
  const SocialCreatePostScreen({super.key});

  @override
  ConsumerState<SocialCreatePostScreen> createState() =>
      _SocialCreatePostScreenState();
}

class _SocialCreatePostScreenState
    extends ConsumerState<SocialCreatePostScreen> {
  final _titleController = TextEditingController();
  final _bodyController = TextEditingController();

  int? _categoryId;
  String _postType = 'question';

  @override
  void initState() {
    super.initState();

    Future.microtask(() {
      final state = ref.read(socialControllerProvider);
      if (state.categories.isEmpty) {
        ref.read(socialControllerProvider.notifier).load();
      }
    });
  }

  @override
  void dispose() {
    _titleController.dispose();
    _bodyController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(socialControllerProvider);

    return Scaffold(
      appBar: const FarmAppBar(title: 'ساخت پست'),
      body: SafeArea(
        child: ResponsiveBuilder(
          builder: (context, constraints, r) {
            return Center(
              child: ConstrainedBox(
                constraints: BoxConstraints(maxWidth: r.maxContentWidth()),
                child: ListView(
                  padding: r.pagePadding(),
                  children: [
                    DropdownButtonFormField<int>(
                      initialValue: _categoryId,
                      decoration: const InputDecoration(
                        labelText: 'دسته‌بندی',
                        border: OutlineInputBorder(),
                      ),
                      items:
                          state.categories
                              .map(
                                (category) => DropdownMenuItem(
                                  value: category.id,
                                  child: Text(category.title),
                                ),
                              )
                              .toList(),
                      onChanged: (value) {
                        setState(() => _categoryId = value);
                      },
                    ),
                    SizedBox(height: r.v(12)),
                    DropdownButtonFormField<String>(
                      initialValue: _postType,
                      decoration: const InputDecoration(
                        labelText: 'نوع پست',
                        border: OutlineInputBorder(),
                      ),
                      items: const [
                        DropdownMenuItem(
                          value: 'question',
                          child: Text('پرسش'),
                        ),
                        DropdownMenuItem(
                          value: 'experience',
                          child: Text('تجربه'),
                        ),
                        DropdownMenuItem(value: 'problem', child: Text('مشکل')),
                        DropdownMenuItem(value: 'guide', child: Text('راهنما')),
                        DropdownMenuItem(
                          value: 'general',
                          child: Text('عمومی'),
                        ),
                      ],
                      onChanged: (value) {
                        if (value == null) return;
                        setState(() => _postType = value);
                      },
                    ),
                    SizedBox(height: r.v(12)),
                    TextField(
                      controller: _titleController,
                      decoration: const InputDecoration(
                        labelText: 'عنوان',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    SizedBox(height: r.v(12)),
                    TextField(
                      controller: _bodyController,
                      minLines: 5,
                      maxLines: 10,
                      decoration: const InputDecoration(
                        labelText: 'متن پست',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    SizedBox(height: r.v(16)),
                    FilledButton.icon(
                      onPressed: state.isSaving ? null : () => _submit(context),
                      icon: const Icon(Icons.send_outlined),
                      label: const Text('انتشار پست'),
                    ),
                    if (state.errorMessage != null) ...[
                      SizedBox(height: r.v(12)),
                      Text(
                        state.errorMessage!,
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.error,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Future<void> _submit(BuildContext context) async {
    final title = _titleController.text.trim();
    final body = _bodyController.text.trim();

    if (title.length < 3 || body.length < 3) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('عنوان و متن باید کامل باشند.')),
      );
      return;
    }

    await ref
        .read(socialControllerProvider.notifier)
        .createPost(
          categoryId: _categoryId,
          title: title,
          body: body,
          postType: _postType,
        );

    final error = ref.read(socialControllerProvider).errorMessage;
    if (context.mounted && error == null) {
      context.pop();
    }
  }
}
