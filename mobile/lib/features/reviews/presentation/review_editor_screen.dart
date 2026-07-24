import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/review_models.dart';
import '../data/review_repository.dart';

class ReviewEditorScreen extends ConsumerStatefulWidget {
  const ReviewEditorScreen({required this.target, super.key});
  final ReviewCreateTarget target;
  @override
  ConsumerState<ReviewEditorScreen> createState() => _State();
}

class _State extends ConsumerState<ReviewEditorScreen> {
  final _body = TextEditingController();
  int _score = 5;
  bool _saving = false;
  String? _error;

  @override
  void dispose() {
    _body.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('ثبت نظر')),
    body: ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text(widget.target.title, style: Theme.of(context).textTheme.titleLarge),
        const SizedBox(height: 20),
        const Text('امتیاز شما'),
        Semantics(
          label: 'امتیاز از یک تا پنج',
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: List.generate(
              5,
              (index) => IconButton(
                onPressed: _saving ? null : () => setState(() => _score = index + 1),
                icon: Icon(
                  index < _score ? Icons.star_rounded : Icons.star_border_rounded,
                  color: Colors.amber,
                  size: 38,
                ),
              ),
            ),
          ),
        ),
        TextField(
          controller: _body,
          maxLength: 2000,
          maxLines: 6,
          decoration: const InputDecoration(
            labelText: 'متن نظر — اختیاری',
            border: OutlineInputBorder(),
          ),
        ),
        if (_error != null)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Text(
              _error!,
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
          ),
        FilledButton.icon(
          onPressed: _saving ? null : _submit,
          icon: _saving
              ? const SizedBox.square(
                  dimension: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Icon(Icons.send_outlined),
          label: const Text('ثبت نظر'),
        ),
      ],
    ),
  );

  Future<void> _submit() async {
    setState(() {
      _saving = true;
      _error = null;
    });
    try {
      await ref.read(reviewRepositoryProvider).create(
        widget.target,
        _score,
        _body.text.trim().isEmpty ? null : _body.text.trim(),
      );
      if (mounted) Navigator.pop(context, true);
    } on Exception catch (error) {
      if (mounted) {
        setState(() {
          _saving = false;
          _error = error.toString().replaceFirst('Exception: ', '');
        });
      }
    }
  }
}
