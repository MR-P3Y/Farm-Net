import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/utils/api_urls.dart';
import '../../../core/utils/dates.dart';
import '../../../core/utils/digits.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/social_models.dart';
import '../state/social_controller.dart';

class SocialPostDetailScreen extends ConsumerStatefulWidget {
  const SocialPostDetailScreen({required this.postId, super.key});

  final int postId;

  @override
  ConsumerState<SocialPostDetailScreen> createState() =>
      _SocialPostDetailScreenState();
}

class _SocialPostDetailScreenState
    extends ConsumerState<SocialPostDetailScreen> {
  final _commentController = TextEditingController();

  bool _loaded = false;
  int? _replyToCommentId;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(socialControllerProvider.notifier).loadPost(widget.postId);
    });
  }

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(socialControllerProvider);
    final post = state.selectedPost;

    return Scaffold(
      appBar: FarmAppBar(
        title: 'جزئیات پست',
        actions: [
          IconButton(
            icon: const Icon(Icons.bookmark_border),
            onPressed:
                post == null
                    ? null
                    : () {
                      ref
                          .read(socialControllerProvider.notifier)
                          .bookmarkPost(post.id);
                    },
          ),
          PopupMenuButton<String>(
            onSelected: (value) {
              if (post == null) return;
              if (value == 'report') {
                ref.read(socialControllerProvider.notifier).reportPost(post.id);
              }
            },
            itemBuilder:
                (context) => const [
                  PopupMenuItem(value: 'report', child: Text('گزارش پست')),
                ],
          ),
        ],
      ),
      body: SafeArea(
        child: ResponsiveBuilder(
          builder: (context, constraints, r) {
            if (state.isSaving && post == null) {
              return const FarmLoadingView();
            }

            if (post == null) {
              return const Center(child: Text('پست پیدا نشد.'));
            }

            return Center(
              child: ConstrainedBox(
                constraints: BoxConstraints(maxWidth: r.maxContentWidth()),
                child: Padding(
                  padding: r.pagePadding(),
                  child: Column(
                    children: [
                      Expanded(
                        child: ListView(
                          children: [
                            if (state.errorMessage != null) ...[
                              _ErrorBox(message: state.errorMessage!),
                              SizedBox(height: r.v(12)),
                            ],
                            _PostDetailCard(post: post),
                            SizedBox(height: r.v(12)),
                            _ExpertAnswersSection(answers: post.expertAnswers),
                            SizedBox(height: r.v(12)),
                            Row(
                              children: [
                                FilledButton.icon(
                                  onPressed:
                                      state.isSaving
                                          ? null
                                          : () {
                                            ref
                                                .read(
                                                  socialControllerProvider
                                                      .notifier,
                                                )
                                                .likePost(post.id);
                                          },
                                  icon: const Icon(Icons.thumb_up_alt_outlined),
                                  label: const Text('پسندیدم'),
                                ),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Text(
                                    'واکنش‌ها: ${post.reactionsCount}',
                                  ),
                                ),
                              ],
                            ),
                            SizedBox(height: r.v(16)),
                            Text(
                              'دیدگاه‌ها',
                              style: Theme.of(context).textTheme.titleMedium,
                            ),
                            SizedBox(height: r.v(8)),
                            if (state.comments.isEmpty)
                              const Padding(
                                padding: EdgeInsets.symmetric(vertical: 24),
                                child: Center(
                                  child: Text('هنوز دیدگاهی ثبت نشده است.'),
                                ),
                              )
                            else
                              ...state.comments.map(
                                (comment) => _CommentTile(
                                  comment: comment,
                                  onReply: () {
                                    setState(() {
                                      _replyToCommentId = comment.id;
                                    });
                                  },
                                ),
                              ),
                          ],
                        ),
                      ),
                      _CommentInput(
                        controller: _commentController,
                        replyToCommentId: _replyToCommentId,
                        isSaving: state.isSaving,
                        onCancelReply: () {
                          setState(() => _replyToCommentId = null);
                        },
                        onSend: () async {
                          final text = _commentController.text.trim();
                          if (text.isEmpty) return;

                          await ref
                              .read(socialControllerProvider.notifier)
                              .createComment(
                                postId: post.id,
                                body: text,
                                parentCommentId: _replyToCommentId,
                              );

                          _commentController.clear();
                          if (mounted) {
                            setState(() => _replyToCommentId = null);
                          }
                        },
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }
}

class _PostDetailCard extends StatelessWidget {
  const _PostDetailCard({required this.post});

  final SocialPostModel post;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final imageUrl = absoluteApiUrl(post.mediaPublicUrl);

    return Card(
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (imageUrl != null)
            AspectRatio(
              aspectRatio: 16 / 9,
              child: Image.network(
                imageUrl,
                fit: BoxFit.cover,
                errorBuilder: (_, __, ___) {
                  return const Center(
                    child: Icon(Icons.image_not_supported_outlined),
                  );
                },
              ),
            ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(post.title, style: theme.textTheme.titleLarge),
                const SizedBox(height: 12),
                Text(post.body),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    Chip(label: Text(post.postType)),
                    Chip(label: Text('بازدید: ${post.viewsCount}')),
                    Chip(label: Text('دیدگاه: ${post.commentsCount}')),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ExpertAnswersSection extends StatelessWidget {
  const _ExpertAnswersSection({required this.answers});

  final List<ExpertAnswerModel> answers;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final publishedAnswers =
        answers.where((answer) => answer.status == 'published').toList();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Icon(Icons.verified_outlined, color: theme.colorScheme.primary),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'پاسخ‌های متخصص',
                    style: theme.textTheme.titleMedium,
                  ),
                ),
                Text(
                  toPersianDigits(publishedAnswers.length),
                  style: theme.textTheme.labelLarge,
                ),
              ],
            ),
            const SizedBox(height: 12),
            if (publishedAnswers.isEmpty)
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 14,
                  vertical: 18,
                ),
                decoration: BoxDecoration(
                  color: theme.colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(14),
                ),
                child: const Text(
                  'هنوز پاسخی از متخصص ثبت نشده است.',
                  textAlign: TextAlign.center,
                ),
              )
            else
              ...publishedAnswers.map(
                (answer) => Padding(
                  padding: const EdgeInsets.only(bottom: 10),
                  child: _ExpertAnswerCard(answer: answer),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _ExpertAnswerCard extends StatelessWidget {
  const _ExpertAnswerCard({required this.answer});

  final ExpertAnswerModel answer;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return DecoratedBox(
      decoration: BoxDecoration(
        border: Border.all(color: theme.colorScheme.outlineVariant),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (answer.consultant == null)
              const _MissingConsultantNotice()
            else
              _ExpertConsultantCard(consultant: answer.consultant!),
            const SizedBox(height: 12),
            Text(answer.body, style: theme.textTheme.bodyLarge),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                if (answer.isAccepted)
                  const Chip(
                    avatar: Icon(Icons.check_circle_outline, size: 18),
                    label: Text('پاسخ پذیرفته‌شده'),
                    visualDensity: VisualDensity.compact,
                  ),
                Chip(
                  avatar: const Icon(Icons.thumb_up_alt_outlined, size: 18),
                  label: Text('مفید: ${toPersianDigits(answer.helpfulCount)}'),
                  visualDensity: VisualDensity.compact,
                ),
                Chip(
                  avatar: const Icon(Icons.schedule_outlined, size: 18),
                  label: Text(_formatIsoDate(answer.createdAt)),
                  visualDensity: VisualDensity.compact,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _ExpertConsultantCard extends StatelessWidget {
  const _ExpertConsultantCard({required this.consultant});

  final ExpertAnswerConsultantModel consultant;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final avatarUrl = absoluteApiUrl(consultant.avatarUrl);
    final canOpen = consultant.consultantId > 0;
    final specialties = consultant.specialties.take(3).toList();

    return InkWell(
      borderRadius: BorderRadius.circular(14),
      onTap:
          canOpen
              ? () => context.push('/consultants/${consultant.consultantId}')
              : null,
      child: Ink(
        decoration: BoxDecoration(
          color: theme.colorScheme.primaryContainer.withValues(alpha: .28),
          borderRadius: BorderRadius.circular(14),
        ),
        padding: const EdgeInsets.all(12),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _ConsultantAvatar(url: avatarUrl),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          consultant.resolvedName,
                          style: theme.textTheme.titleSmall,
                        ),
                      ),
                      if (consultant.isVerified)
                        Icon(
                          Icons.verified,
                          size: 18,
                          color: theme.colorScheme.primary,
                        ),
                    ],
                  ),
                  if ((consultant.title ?? '').isNotEmpty) ...[
                    const SizedBox(height: 4),
                    Text(consultant.title!, style: theme.textTheme.bodySmall),
                  ],
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 6,
                    runSpacing: 6,
                    children: [
                      _MiniChip(
                        icon: Icons.star_rounded,
                        label: toPersianDigits(
                          consultant.ratingAverage.toStringAsFixed(1),
                        ),
                      ),
                      _MiniChip(
                        icon: Icons.rate_review_outlined,
                        label:
                            '${toPersianDigits(consultant.reviewsCount)} نظر',
                      ),
                      ...specialties.map(
                        (item) => _MiniChip(
                          icon: Icons.eco_outlined,
                          label: item.title,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            if (canOpen) ...[
              const SizedBox(width: 6),
              const Icon(Icons.chevron_left),
            ],
          ],
        ),
      ),
    );
  }
}

class _ConsultantAvatar extends StatelessWidget {
  const _ConsultantAvatar({required this.url});

  final String? url;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return SizedBox.square(
      dimension: 54,
      child: DecoratedBox(
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: colors.primaryContainer,
        ),
        child: ClipOval(
          child:
              url == null
                  ? Icon(
                    Icons.support_agent_outlined,
                    color: colors.onPrimaryContainer,
                  )
                  : Image.network(
                    url!,
                    fit: BoxFit.cover,
                    errorBuilder: (_, __, ___) {
                      return Icon(
                        Icons.support_agent_outlined,
                        color: colors.onPrimaryContainer,
                      );
                    },
                  ),
        ),
      ),
    );
  }
}

class _MissingConsultantNotice extends StatelessWidget {
  const _MissingConsultantNotice();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(14),
      ),
      child: const Row(
        children: [
          Icon(Icons.info_outline),
          SizedBox(width: 8),
          Expanded(child: Text('اطلاعات مشاور برای این پاسخ در دسترس نیست.')),
        ],
      ),
    );
  }
}

class _MiniChip extends StatelessWidget {
  const _MiniChip({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Chip(
      avatar: Icon(icon, size: 16),
      label: Text(label),
      visualDensity: VisualDensity.compact,
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
    );
  }
}

class _CommentTile extends StatelessWidget {
  const _CommentTile({required this.comment, required this.onReply});

  final SocialCommentModel comment;
  final VoidCallback onReply;

  @override
  Widget build(BuildContext context) {
    final isReply = comment.parentCommentId != null;

    return Padding(
      padding: EdgeInsetsDirectional.only(start: isReply ? 28 : 0),
      child: Card(
        child: ListTile(
          leading: Icon(
            isReply ? Icons.subdirectory_arrow_left : Icons.comment,
          ),
          title: Text(comment.body),
          subtitle: Text('واکنش: ${comment.reactionsCount}'),
          trailing:
              isReply
                  ? null
                  : TextButton(onPressed: onReply, child: const Text('پاسخ')),
        ),
      ),
    );
  }
}

class _CommentInput extends StatelessWidget {
  const _CommentInput({
    required this.controller,
    required this.replyToCommentId,
    required this.isSaving,
    required this.onCancelReply,
    required this.onSend,
  });

  final TextEditingController controller;
  final int? replyToCommentId;
  final bool isSaving;
  final VoidCallback onCancelReply;
  final VoidCallback onSend;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        if (replyToCommentId != null)
          Row(
            children: [
              Expanded(child: Text('در حال پاسخ به کامنت #$replyToCommentId')),
              TextButton(onPressed: onCancelReply, child: const Text('لغو')),
            ],
          ),
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: controller,
                minLines: 1,
                maxLines: 3,
                decoration: const InputDecoration(
                  hintText: 'دیدگاه خود را بنویسید...',
                  border: OutlineInputBorder(),
                ),
              ),
            ),
            const SizedBox(width: 8),
            FilledButton(
              onPressed: isSaving ? null : onSend,
              child: const Text('ارسال'),
            ),
          ],
        ),
      ],
    );
  }
}

String _formatIsoDate(String value) {
  final date = DateTime.tryParse(value);
  if (date == null) return 'تاریخ نامشخص';

  return formatJalaliDate(date.toLocal());
}

class _ErrorBox extends StatelessWidget {
  const _ErrorBox({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;

    return Card(
      color: colors.errorContainer,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Text(message, style: TextStyle(color: colors.onErrorContainer)),
      ),
    );
  }
}
