import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/utils/api_urls.dart';
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
