import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../data/review_models.dart';
import '../data/review_repository.dart';

final publicReviewsProvider =
    FutureProvider.family<PublicReviewPage, ({String type, int id})>(
      (ref, target) =>
          ref.watch(reviewRepositoryProvider).publicReviews(target.type, target.id),
    );

class PublicReviewsSection extends ConsumerWidget {
  const PublicReviewsSection({
    required this.subjectType,
    required this.subjectId,
    super.key,
  });
  final String subjectType;
  final int subjectId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final key = (type: subjectType, id: subjectId);
    final state = ref.watch(publicReviewsProvider(key));
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: state.when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (_, __) => Row(
            children: [
              const Expanded(child: Text('دریافت نظرها ناموفق بود.')),
              TextButton(
                onPressed: () => ref.invalidate(publicReviewsProvider(key)),
                child: const Text('تلاش دوباره'),
              ),
            ],
          ),
          data: (page) => Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Text('نظر کاربران', style: Theme.of(context).textTheme.titleLarge),
                  const Spacer(),
                  const Icon(Icons.star_rounded, color: Colors.amber),
                  Text(page.rating.ratingAverage.toStringAsFixed(1)),
                  Text(' (${page.rating.reviewsCount})'),
                ],
              ),
              const SizedBox(height: 10),
              if (page.items.isEmpty)
                const Text('هنوز نظری ثبت نشده است.')
              else
                ...page.items.map(
                  (review) => ListTile(
                    contentPadding: EdgeInsets.zero,
                    leading: CircleAvatar(child: Text('${review.score}')),
                    title: Text(review.authorName),
                    subtitle: review.body == null ? null : Text(review.body!),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: List.generate(
                        5,
                        (index) => Icon(
                          index < review.score ? Icons.star : Icons.star_border,
                          size: 15,
                          color: Colors.amber,
                        ),
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
