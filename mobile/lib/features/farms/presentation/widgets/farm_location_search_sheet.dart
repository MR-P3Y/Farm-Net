import 'package:flutter/material.dart';

import '../../../../core/localization/app_localizations.dart';
import '../../data/farm_models.dart';

typedef FarmLocationSearch =
    Future<List<FarmLocationResult>> Function(String query);

Future<FarmLocationResult?> showFarmLocationSearchSheet(
  BuildContext context, {
  required FarmLocationSearch onSearch,
}) => showModalBottomSheet<FarmLocationResult>(
  context: context,
  isScrollControlled: true,
  useSafeArea: true,
  builder:
      (_) => FractionallySizedBox(
        heightFactor: 0.82,
        child: _FarmLocationSearchSheet(onSearch: onSearch),
      ),
);

class _FarmLocationSearchSheet extends StatefulWidget {
  const _FarmLocationSearchSheet({required this.onSearch});

  final FarmLocationSearch onSearch;

  @override
  State<_FarmLocationSearchSheet> createState() =>
      _FarmLocationSearchSheetState();
}

class _FarmLocationSearchSheetState extends State<_FarmLocationSearchSheet> {
  final _controller = TextEditingController();
  List<FarmLocationResult>? _results;
  String? _error;
  var _searching = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _search() async {
    final l10n = context.l10n;
    final query = _controller.text.trim();
    if (query.length < 2) {
      setState(() {
        _error = l10n.tr(
          fa: 'حداقل دو حرف برای جست‌وجو وارد کنید.',
          en: 'Enter at least two characters.',
        );
      });
      return;
    }
    FocusScope.of(context).unfocus();
    setState(() {
      _searching = true;
      _error = null;
    });
    try {
      final results = await widget.onSearch(query);
      if (!mounted) return;
      setState(() => _results = results);
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _error = l10n.tr(
          fa: 'جست‌وجوی مکان انجام نشد؛ دوباره تلاش کنید.',
          en: 'Location search failed. Please try again.',
        );
      });
    } finally {
      if (mounted) setState(() => _searching = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = context.l10n;
    return Padding(
      padding: EdgeInsets.fromLTRB(
        18,
        12,
        18,
        14 + MediaQuery.viewInsetsOf(context).bottom,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Center(
            child: Container(
              width: 42,
              height: 4,
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.outlineVariant,
                borderRadius: BorderRadius.circular(99),
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            l10n.tr(fa: 'جست‌وجوی موقعیت مزرعه', en: 'Find farm location'),
            style: Theme.of(
              context,
            ).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 4),
          Text(
            l10n.tr(
              fa: 'نام استان، شهر، روستا یا مکان را بنویسید و جست‌وجو را بزنید.',
              en: 'Enter a province, city, village, or place and tap Search.',
            ),
            style: Theme.of(context).textTheme.bodySmall,
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              Expanded(
                child: TextField(
                  key: const ValueKey('farm-location-search-field'),
                  controller: _controller,
                  autofocus: true,
                  textInputAction: TextInputAction.search,
                  onSubmitted: (_) => _search(),
                  decoration: InputDecoration(
                    hintText: l10n.tr(
                      fa: 'مثلاً قلات، شیراز',
                      en: 'For example, Qalat, Shiraz',
                    ),
                    prefixIcon: const Icon(Icons.travel_explore_rounded),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              FilledButton(
                key: const ValueKey('farm-location-search-submit'),
                onPressed: _searching ? null : _search,
                child:
                    _searching
                        ? const SizedBox.square(
                          dimension: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                        : Text(l10n.tr(fa: 'جست‌وجو', en: 'Search')),
              ),
            ],
          ),
          if (_error != null) ...[
            const SizedBox(height: 10),
            Text(
              _error!,
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
          ],
          const SizedBox(height: 12),
          Expanded(child: _buildResults(l10n)),
          if (_results != null) ...[
            const Divider(height: 16),
            const Text(
              '© OpenStreetMap contributors',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 10),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildResults(AppLocalizations l10n) {
    final results = _results;
    if (results == null) {
      return Center(
        child: Icon(
          Icons.map_outlined,
          size: 54,
          color: Theme.of(context).colorScheme.outline,
        ),
      );
    }
    if (results.isEmpty) {
      return Center(
        child: Text(
          l10n.tr(
            fa: 'مکانی با این نام پیدا نشد؛ عبارت دقیق‌تری وارد کنید.',
            en: 'No place was found. Try a more specific query.',
          ),
          textAlign: TextAlign.center,
        ),
      );
    }
    return ListView.separated(
      keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
      itemCount: results.length,
      separatorBuilder: (_, __) => const Divider(height: 1),
      itemBuilder: (context, index) {
        final result = results[index];
        return ListTile(
          key: ValueKey('farm-location-result-${result.reference}'),
          leading: const CircleAvatar(child: Icon(Icons.location_on_outlined)),
          title: Text(
            result.shortName,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          subtitle: Text(
            result.displayName,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          trailing: const Icon(Icons.chevron_right_rounded),
          onTap: () => Navigator.pop(context, result),
        );
      },
    );
  }
}
