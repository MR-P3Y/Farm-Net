import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/utils/digits.dart';
import '../data/service_repository.dart';

final activeServiceRequestCountProvider = FutureProvider<int>((ref) async {
  final requests = await ref.watch(serviceRepositoryProvider).myRequests();
  return requests
      .where(
        (item) =>
            const {'open', 'accepted', 'in_progress'}.contains(item.status),
      )
      .length;
});

class MyServiceRequestsAction extends ConsumerWidget {
  const MyServiceRequestsAction({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final count = ref.watch(activeServiceRequestCountProvider).valueOrNull ?? 0;
    final compactCount = count > 99 ? '99+' : count.toString();
    final countLabel =
        context.l10n.isFa ? toPersianDigits(compactCount) : compactCount;
    return IconButton(
      key: const Key('service-my-requests-action'),
      tooltip: context.l10n.tr(fa: 'درخواست‌های من', en: 'My requests'),
      onPressed: () => context.push('/services/requests'),
      icon:
          count > 0
              ? Badge(
                alignment: Alignment.topCenter,
                offset: const Offset(-4, -6),
                padding: const EdgeInsets.symmetric(horizontal: 4),
                textStyle: const TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w700,
                ),
                label: Text(countLabel, textDirection: TextDirection.ltr),
                child: const Icon(Icons.assignment_outlined),
              )
              : const Icon(Icons.assignment_outlined),
    );
  }
}
