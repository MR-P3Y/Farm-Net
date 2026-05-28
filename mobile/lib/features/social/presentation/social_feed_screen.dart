import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/responsive/responsive.dart';
import '../../../core/utils/api_urls.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_empty_view.dart';
import '../../../core/widgets/farm_loading_view.dart';
import '../data/social_models.dart';
import '../state/social_controller.dart';

class SocialFeedScreen extends ConsumerStatefulWidget {
  const SocialFeedScreen({super.key});

  @override
  ConsumerState<SocialFeedScreen> createState() => _SocialFeedScreenState();
}

class _SocialFeedScreenState extends ConsumerState<SocialFeedScreen> {
  bool _loaded = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (_loaded) return;
    _loaded = true;

    Future.microtask(() {
      ref.read(socialControllerProvider.notifier).load();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(socialControllerProvider);

    return Scaffold(
      appBar: FarmAppBar(
        title: 'جامعه کشاورزی',
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => context.push('/social/create'),
          ),
        ],
      ),
      body: SafeArea(
        child: ResponsiveBuilder(
          builder: (context, constraints, r) {
            return Center(
              child: ConstrainedBox(
                constraints: BoxConstraints(maxWidth: r.maxContentWidth()),
                child: Padding(
                  padding: r.pagePadding(),
                  child:
                      state.isLoading
                          ? const FarmLoadingView()
                          : Column(
                            children: [
                              if (state.errorMessage != null) ...[
                                _ErrorBox(message: state.errorMessage!),
                                SizedBox(height: r.v(12)),
                              ],
                              _CategoryChips(
                                categories: state.categories,
                                selectedCategoryId: state.selectedCategoryId,
                                onSelected: (categoryId) {
                                  ref
                                      .read(socialControllerProvider.notifier)
                                      .filterByCategory(categoryId);
                                },
                              ),
                              if (state.isSaving) ...[
                                SizedBox(height: r.v(8)),
                                const LinearProgressIndicator(),
                              ],
                              SizedBox(height: r.v(12)),
                              Expanded(
                                child: RefreshIndicator(
                                  onRefresh:
                                      () =>
                                          ref
                                              .read(
                                                socialControllerProvider
                                                    .notifier,
                                              )
                                              .load(),
                                  child:
                                      state.posts.isEmpty
                                          ? ListView(
                                            physics:
                                                const AlwaysScrollableScrollPhysics(),
                                            children: const [
                                              SizedBox(height: 96),
                                              FarmEmptyView(
                                                message:
                                                    'اولین پست جامعه کشاورزی را شما ثبت کنید.',
                                              ),
                                            ],
                                          )
                                          : ListView.separated(
                                            physics:
                                                const AlwaysScrollableScrollPhysics(),
                                            itemCount: state.posts.length,
                                            separatorBuilder:
                                                (_, __) =>
                                                    SizedBox(height: r.v(10)),
                                            itemBuilder: (context, index) {
                                              final post = state.posts[index];
                                              return _SocialPostCard(
                                                post: post,
                                              );
                                            },
                                          ),
                                ),
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

class _CategoryChips extends StatelessWidget {
  const _CategoryChips({
    required this.categories,
    required this.selectedCategoryId,
    required this.onSelected,
  });

  final List<SocialCategoryModel> categories;
  final int? selectedCategoryId;
  final ValueChanged<int?> onSelected;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 44,
      child: ListView(
        scrollDirection: Axis.horizontal,
        children: [
          Padding(
            padding: const EdgeInsetsDirectional.only(end: 8),
            child: ChoiceChip(
              label: const Text('همه'),
              selected: selectedCategoryId == null,
              onSelected: (_) => onSelected(null),
            ),
          ),
          ...categories.map(
            (category) => Padding(
              padding: const EdgeInsetsDirectional.only(end: 8),
              child: ChoiceChip(
                label: Text(category.title),
                selected: selectedCategoryId == category.id,
                onSelected: (_) => onSelected(category.id),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _SocialPostCard extends StatelessWidget {
  const _SocialPostCard({required this.post});

  final SocialPostModel post;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final imageUrl = absoluteApiUrl(post.mediaPublicUrl);

    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () => context.push('/social/detail/${post.id}'),
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
              padding: const EdgeInsets.all(14),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(post.title, style: theme.textTheme.titleMedium),
                  const SizedBox(height: 8),
                  Text(post.body, maxLines: 3, overflow: TextOverflow.ellipsis),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      Chip(label: Text(_postTypeLabel(post.postType))),
                      Chip(label: Text('دیدگاه: ${post.commentsCount}')),
                      Chip(label: Text('واکنش: ${post.reactionsCount}')),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _postTypeLabel(String value) {
    return switch (value) {
      'question' => 'پرسش',
      'experience' => 'تجربه',
      'problem' => 'مشکل',
      'guide' => 'راهنما',
      'general' => 'عمومی',
      _ => value,
    };
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
