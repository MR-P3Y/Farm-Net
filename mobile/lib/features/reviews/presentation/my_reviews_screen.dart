import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/review_models.dart';
import '../data/review_repository.dart';

final myReviewsProvider = FutureProvider<List<MyReview>>(
  (ref) => ref.watch(reviewRepositoryProvider).myReviews(),
);

class MyReviewsScreen extends ConsumerWidget {
  const MyReviewsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(myReviewsProvider);
    return Scaffold(
      appBar: AppBar(title: const Text('نظرات من')),
      body: state.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(error.toString()),
              TextButton(
                onPressed: () => ref.invalidate(myReviewsProvider),
                child: const Text('تلاش دوباره'),
              ),
            ],
          ),
        ),
        data: (items) => RefreshIndicator(
          onRefresh: () => ref.refresh(myReviewsProvider.future),
          child: items.isEmpty
              ? ListView(
                  children: const [
                    SizedBox(height: 120),
                    Center(child: Text('هنوز نظری ثبت نکرده‌اید.')),
                  ],
                )
              : ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: items.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (context, index) =>
                      _ReviewCard(review: items[index]),
                ),
        ),
      ),
    );
  }
}

class _ReviewCard extends ConsumerWidget {
  const _ReviewCard({required this.review});
  final MyReview review;
  @override
  Widget build(BuildContext context, WidgetRef ref) => Card(
    child: ListTile(
      title: Text(reviewSubjectLabel(review.subjectType)),
      subtitle: Text(
        [
          if ((review.body ?? '').isNotEmpty) review.body!,
          'وضعیت: ${review.status}',
        ].join('\n'),
      ),
      leading: CircleAvatar(child: Text('${review.score}')),
      trailing: review.canEdit || review.canDelete
          ? PopupMenuButton<String>(
              onSelected: (action) async {
                if (action == 'edit') {
                  await _edit(context, ref);
                } else {
                  await ref.read(reviewRepositoryProvider).delete(review.id);
                  ref.invalidate(myReviewsProvider);
                }
              },
              itemBuilder: (_) => [
                if (review.canEdit)
                  const PopupMenuItem(value: 'edit', child: Text('ویرایش')),
                if (review.canDelete)
                  const PopupMenuItem(value: 'delete', child: Text('حذف')),
              ],
            )
          : null,
    ),
  );

  Future<void> _edit(BuildContext context, WidgetRef ref) async {
    var score = review.score;
    final body = TextEditingController(text: review.body);
    final save = await showDialog<bool>(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('ویرایش نظر'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                children: List.generate(
                  5,
                  (index) => IconButton(
                    onPressed: () => setDialogState(() => score = index + 1),
                    icon: Icon(
                      index < score ? Icons.star : Icons.star_border,
                      color: Colors.amber,
                    ),
                  ),
                ),
              ),
              TextField(controller: body, maxLength: 2000, maxLines: 4),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('انصراف'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('ذخیره'),
            ),
          ],
        ),
      ),
    );
    if (save == true) {
      await ref.read(reviewRepositoryProvider).update(
        review.id,
        score,
        body.text.trim().isEmpty ? null : body.text.trim(),
      );
      ref.invalidate(myReviewsProvider);
    }
    body.dispose();
  }
}
