import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/localization/app_localizations.dart';
import '../../../core/widgets/farm_app_bar.dart';
import '../../../core/widgets/farm_glass_card.dart';
import '../data/toolbox_repository.dart';
import '../domain/farm_calculators.dart';
import '../domain/toolbox_number_input.dart';
import 'toolbox_context.dart';
import 'toolbox_localization.dart';

class FarmCalculatorScreen extends ConsumerStatefulWidget {
  const FarmCalculatorScreen({
    required this.type,
    required this.contextSelection,
    this.initialTotalCost,
    super.key,
  });

  final FarmCalculatorType type;
  final ToolboxContextSelection? contextSelection;
  final double? initialTotalCost;

  @override
  ConsumerState<FarmCalculatorScreen> createState() =>
      _FarmCalculatorScreenState();
}

class _FarmCalculatorScreenState extends ConsumerState<FarmCalculatorScreen> {
  final _formKey = GlobalKey<FormState>();
  final Map<String, TextEditingController> _controllers = {};
  FarmCalculationResult? _result;
  UnitConversionOption _conversion = farmUnitConversions.first;
  bool _saving = false;

  CalculatorDefinition get _definition => calculatorDefinition(widget.type);

  @override
  void initState() {
    super.initState();
    for (final field in _definition.fields) {
      final area =
          field.key == 'area_sqm' ? widget.contextSelection?.areaSqm : null;
      final initialCost =
          field.key == 'total_cost_toman' ? widget.initialTotalCost : null;
      _controllers[field.key] = TextEditingController(
        text: formatToolboxNumberInput(
          area ?? initialCost ?? field.initialValue,
        ),
      );
    }
    if (widget.type == FarmCalculatorType.unitConversion) {
      _controllers['factor']?.text = _conversion.factor.toString();
    }
  }

  @override
  void dispose() {
    for (final controller in _controllers.values) {
      controller.dispose();
    }
    super.dispose();
  }

  Map<String, double>? _values() {
    if (!(_formKey.currentState?.validate() ?? false)) return null;
    return {
      for (final entry in _controllers.entries)
        entry.key: parseToolboxNumber(entry.value.text)!,
    };
  }

  void _calculate() {
    final values = _values();
    if (values == null) return;
    try {
      setState(
        () => _result = FarmCalculatorEngine.calculate(widget.type, values),
      );
    } on FormatException {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            context.l10n.tr(
              fa: 'مقادیر واردشده را بررسی کنید.',
              en: 'Check the entered values.',
            ),
          ),
        ),
      );
    }
  }

  Future<void> _save() async {
    final selection = widget.contextSelection;
    final values = _values();
    if (selection == null || values == null || _result == null || _saving) {
      return;
    }
    setState(() => _saving = true);
    try {
      await ref
          .read(toolboxRepositoryProvider)
          .saveCalculation(
            farmId: selection.farmId,
            plotId: selection.plotId,
            cycleId: selection.cycleId,
            type: widget.type,
            title: _definition.title(context),
            inputValues: values,
            inputUnits:
                widget.type == FarmCalculatorType.unitConversion
                    ? {
                      'value': _conversion.fromUnit,
                      'factor': 'ratio',
                      'to_unit': _conversion.toUnit,
                    }
                    : {
                      for (final field in _definition.fields)
                        if (field.unit.isNotEmpty) field.key: field.unit,
                    },
          );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            context.l10n.tr(
              fa: 'محاسبه در دفترچه ذخیره شد',
              en: 'Calculation saved to notebook',
            ),
          ),
        ),
      );
      Navigator.of(context).pop(true);
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(localizeToolboxError(context, error))),
      );
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final definition = _definition;
    return Scaffold(
      appBar: FarmAppBar(title: definition.title(context)),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          FarmGlassCard(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                CircleAvatar(child: Icon(definition.icon)),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        definition.description(context),
                        style: Theme.of(context).textTheme.bodyLarge,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        context.l10n.tr(
                          fa:
                              'فرمول نسخه ${localizeToolboxDigits(context, FarmCalculatorEngine.formulaVersion)} • قابل استفاده آفلاین',
                          en:
                              'Formula ${FarmCalculatorEngine.formulaVersion} • works offline',
                        ),
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Form(
            key: _formKey,
            child: Column(
              children: [
                if (widget.type == FarmCalculatorType.unitConversion) ...[
                  DropdownButtonFormField<UnitConversionOption>(
                    initialValue: _conversion,
                    decoration: InputDecoration(
                      labelText: context.l10n.tr(
                        fa: 'نوع تبدیل',
                        en: 'Conversion',
                      ),
                      prefixIcon: const Icon(Icons.swap_horiz_rounded),
                    ),
                    items:
                        farmUnitConversions
                            .map(
                              (option) => DropdownMenuItem(
                                value: option,
                                child: Text(
                                  '${localizeToolboxUnit(context, option.fromUnit)} → '
                                  '${localizeToolboxUnit(context, option.toUnit)}',
                                ),
                              ),
                            )
                            .toList(),
                    onChanged: (option) {
                      if (option == null) return;
                      setState(() {
                        _conversion = option;
                        _controllers['factor']!.text = option.factor.toString();
                        _result = null;
                      });
                    },
                  ),
                  const SizedBox(height: 12),
                ],
                for (final field in definition.fields)
                  if (field.key != 'factor') ...[
                    TextFormField(
                      controller: _controllers[field.key],
                      keyboardType: const TextInputType.numberWithOptions(
                        decimal: true,
                      ),
                      inputFormatters: [
                        FilteringTextInputFormatter.allow(
                          RegExp(r'[0-9۰-۹٠-٩.,٬٫]'),
                        ),
                      ],
                      decoration: InputDecoration(
                        labelText: field.label(context),
                        suffixText:
                            widget.type == FarmCalculatorType.unitConversion &&
                                    field.key == 'value'
                                ? localizeToolboxUnit(
                                  context,
                                  _conversion.fromUnit,
                                )
                                : localizeToolboxUnit(context, field.unit),
                      ),
                      validator: (value) {
                        final parsed = parseToolboxNumber(value ?? '');
                        if (parsed == null || parsed < 0) {
                          return context.l10n.tr(
                            fa: 'یک عدد معتبر وارد کنید',
                            en: 'Enter a valid number',
                          );
                        }
                        if (field.positive && parsed <= 0) {
                          return context.l10n.tr(
                            fa: 'مقدار باید بیشتر از صفر باشد',
                            en: 'Value must be greater than zero',
                          );
                        }
                        if (field.percent && parsed > 100) {
                          return context.l10n.tr(
                            fa: 'درصد باید حداکثر ۱۰۰ باشد',
                            en: 'Percentage cannot exceed 100',
                          );
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 12),
                  ],
              ],
            ),
          ),
          FilledButton.icon(
            onPressed: _calculate,
            icon: const Icon(Icons.calculate_rounded),
            label: Text(context.l10n.tr(fa: 'محاسبه کن', en: 'Calculate')),
          ),
          if (_result != null) ...[
            const SizedBox(height: 20),
            _ResultCard(
              definition: definition,
              result: _result!,
              conversion: _conversion,
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed:
                  widget.contextSelection == null || _saving ? null : _save,
              icon:
                  _saving
                      ? const SizedBox.square(
                        dimension: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                      : const Icon(Icons.bookmark_add_outlined),
              label: Text(
                widget.contextSelection == null
                    ? context.l10n.tr(
                      fa: 'برای ذخیره، ابتدا مزرعه را انتخاب کنید',
                      en: 'Select a farm to save',
                    )
                    : context.l10n.tr(
                      fa: 'ذخیره در دفترچه محاسبات',
                      en: 'Save to calculation notebook',
                    ),
              ),
            ),
          ],
          if (widget.type == FarmCalculatorType.fertilizer ||
              widget.type == FarmCalculatorType.spraying) ...[
            const SizedBox(height: 16),
            Text(
              context.l10n.tr(
                fa:
                    'این ابزار فقط مقدار درج‌شده توسط شما یا روی برچسب محصول را محاسبه می‌کند و توصیه مصرف نیست.',
                en:
                    'This tool only calculates the rate you or the label provide; it is not an application recommendation.',
              ),
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ],
      ),
    );
  }
}

class _ResultCard extends StatelessWidget {
  const _ResultCard({
    required this.definition,
    required this.result,
    required this.conversion,
  });

  final CalculatorDefinition definition;
  final FarmCalculationResult result;
  final UnitConversionOption conversion;

  @override
  Widget build(BuildContext context) => FarmGlassCard(
    padding: const EdgeInsets.all(16),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          context.l10n.tr(fa: 'نتیجه', en: 'Result'),
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 12),
        for (final entry in result.values.entries)
          ListTile(
            contentPadding: EdgeInsets.zero,
            title: Text(definition.resultLabel(context, entry.key)),
            trailing: Text(
              formatToolboxValue(
                context,
                entry.value,
                entry.key == 'converted_value'
                    ? conversion.toUnit
                    : result.units[entry.key] ?? '',
              ),
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800),
            ),
          ),
      ],
    ),
  );
}

class CalculatorFieldDefinition {
  const CalculatorFieldDefinition({
    required this.key,
    required this.fa,
    required this.en,
    required this.unit,
    this.initialValue,
    this.positive = true,
    this.percent = false,
  });

  final String key;
  final String fa;
  final String en;
  final String unit;
  final double? initialValue;
  final bool positive;
  final bool percent;

  String label(BuildContext context) => context.l10n.tr(fa: fa, en: en);
}

class CalculatorDefinition {
  const CalculatorDefinition({
    required this.type,
    required this.fa,
    required this.en,
    required this.descriptionFa,
    required this.descriptionEn,
    required this.icon,
    required this.fields,
    required this.results,
  });

  final FarmCalculatorType type;
  final String fa;
  final String en;
  final String descriptionFa;
  final String descriptionEn;
  final IconData icon;
  final List<CalculatorFieldDefinition> fields;
  final Map<String, ({String fa, String en})> results;

  String title(BuildContext context) => context.l10n.tr(fa: fa, en: en);
  String description(BuildContext context) =>
      context.l10n.tr(fa: descriptionFa, en: descriptionEn);
  String resultLabel(BuildContext context, String key) {
    final label = results[key];
    return label == null ? key : context.l10n.tr(fa: label.fa, en: label.en);
  }
}

CalculatorDefinition calculatorDefinition(FarmCalculatorType type) =>
    _calculatorDefinitions.firstWhere((item) => item.type == type);

final _calculatorDefinitions = <CalculatorDefinition>[
  CalculatorDefinition(
    type: FarmCalculatorType.seed,
    fa: 'محاسبه بذر و بوته',
    en: 'Seed & plant calculator',
    descriptionFa: 'تعداد بوته و بذر موردنیاز بر اساس فاصله کشت',
    descriptionEn: 'Plants and seeds based on planting spacing',
    icon: Icons.grass_rounded,
    fields: const [
      CalculatorFieldDefinition(
        key: 'area_sqm',
        fa: 'مساحت',
        en: 'Area',
        unit: 'm²',
      ),
      CalculatorFieldDefinition(
        key: 'row_spacing_m',
        fa: 'فاصله ردیف',
        en: 'Row spacing',
        unit: 'm',
        initialValue: 0.5,
      ),
      CalculatorFieldDefinition(
        key: 'plant_spacing_m',
        fa: 'فاصله بوته',
        en: 'Plant spacing',
        unit: 'm',
        initialValue: 0.2,
      ),
      CalculatorFieldDefinition(
        key: 'germination_percent',
        fa: 'درصد جوانه‌زنی',
        en: 'Germination',
        unit: '%',
        initialValue: 90,
        percent: true,
      ),
      CalculatorFieldDefinition(
        key: 'reserve_percent',
        fa: 'ذخیره اضافه',
        en: 'Extra reserve',
        unit: '%',
        initialValue: 5,
        positive: false,
        percent: true,
      ),
    ],
    results: const {
      'plant_count': (fa: 'تعداد بوته', en: 'Plant count'),
      'seed_count': (fa: 'تعداد بذر', en: 'Seed count'),
    },
  ),
  CalculatorDefinition(
    type: FarmCalculatorType.irrigation,
    fa: 'محاسبه آبیاری',
    en: 'Irrigation calculator',
    descriptionFa: 'حجم آب و مدت کارکرد پمپ',
    descriptionEn: 'Water volume and pump duration',
    icon: Icons.water_drop_rounded,
    fields: const [
      CalculatorFieldDefinition(
        key: 'area_sqm',
        fa: 'مساحت',
        en: 'Area',
        unit: 'm²',
      ),
      CalculatorFieldDefinition(
        key: 'depth_mm',
        fa: 'عمق آبیاری',
        en: 'Irrigation depth',
        unit: 'mm',
        initialValue: 20,
      ),
      CalculatorFieldDefinition(
        key: 'efficiency_percent',
        fa: 'راندمان سیستم',
        en: 'Efficiency',
        unit: '%',
        initialValue: 80,
        percent: true,
      ),
      CalculatorFieldDefinition(
        key: 'flow_lpm',
        fa: 'دبی آب',
        en: 'Flow',
        unit: 'L/min',
        initialValue: 100,
      ),
    ],
    results: const {
      'volume_l': (fa: 'حجم آب', en: 'Water volume'),
      'duration_minutes': (fa: 'مدت آبیاری', en: 'Irrigation duration'),
    },
  ),
  CalculatorDefinition(
    type: FarmCalculatorType.fertilizer,
    fa: 'محاسبه کود',
    en: 'Fertilizer calculator',
    descriptionFa: 'مقدار کل و تعداد کیسه بر اساس نرخ ثبت‌شده',
    descriptionEn: 'Total amount and bags using the entered rate',
    icon: Icons.compost_rounded,
    fields: const [
      CalculatorFieldDefinition(
        key: 'area_sqm',
        fa: 'مساحت',
        en: 'Area',
        unit: 'm²',
      ),
      CalculatorFieldDefinition(
        key: 'rate_kg_per_hectare',
        fa: 'نرخ درج‌شده',
        en: 'Entered rate',
        unit: 'kg/ha',
      ),
      CalculatorFieldDefinition(
        key: 'bag_size_kg',
        fa: 'وزن هر کیسه',
        en: 'Bag size',
        unit: 'kg',
        initialValue: 50,
      ),
    ],
    results: const {
      'total_kg': (fa: 'مقدار کل', en: 'Total amount'),
      'bag_count': (fa: 'تعداد کیسه', en: 'Bag count'),
    },
  ),
  CalculatorDefinition(
    type: FarmCalculatorType.spraying,
    fa: 'محاسبه محلول‌پاشی',
    en: 'Spraying calculator',
    descriptionFa: 'آب، محصول و تعداد مخزن بر اساس برچسب',
    descriptionEn: 'Water, product and tanks based on the label',
    icon: Icons.sanitizer_rounded,
    fields: const [
      CalculatorFieldDefinition(
        key: 'area_sqm',
        fa: 'مساحت',
        en: 'Area',
        unit: 'm²',
      ),
      CalculatorFieldDefinition(
        key: 'water_rate_l_per_hectare',
        fa: 'حجم آب در هکتار',
        en: 'Water rate',
        unit: 'L/ha',
      ),
      CalculatorFieldDefinition(
        key: 'product_rate_ml_per_l',
        fa: 'نرخ محصول روی برچسب',
        en: 'Label product rate',
        unit: 'mL/L',
      ),
      CalculatorFieldDefinition(
        key: 'tank_capacity_l',
        fa: 'ظرفیت مخزن',
        en: 'Tank capacity',
        unit: 'L',
      ),
    ],
    results: const {
      'water_l': (fa: 'آب موردنیاز', en: 'Required water'),
      'product_ml': (fa: 'محصول موردنیاز', en: 'Required product'),
      'tank_count': (fa: 'تعداد مخزن', en: 'Tank count'),
    },
  ),
  CalculatorDefinition(
    type: FarmCalculatorType.costProfit,
    fa: 'سود، زیان و نقطه سربه‌سر',
    en: 'Profit & break-even',
    descriptionFa: 'برآورد درآمد، سود و قیمت سربه‌سر',
    descriptionEn: 'Estimate revenue, profit and break-even price',
    icon: Icons.query_stats_rounded,
    fields: const [
      CalculatorFieldDefinition(
        key: 'total_cost_toman',
        fa: 'کل هزینه',
        en: 'Total cost',
        unit: 'Toman',
        positive: false,
      ),
      CalculatorFieldDefinition(
        key: 'expected_yield_kg',
        fa: 'برداشت پیش‌بینی‌شده',
        en: 'Expected yield',
        unit: 'kg',
      ),
      CalculatorFieldDefinition(
        key: 'price_per_kg_toman',
        fa: 'قیمت هر کیلو',
        en: 'Price per kg',
        unit: 'Toman',
        positive: false,
      ),
      CalculatorFieldDefinition(
        key: 'area_sqm',
        fa: 'مساحت',
        en: 'Area',
        unit: 'm²',
      ),
    ],
    results: const {
      'expected_revenue_toman': (
        fa: 'درآمد پیش‌بینی‌شده',
        en: 'Expected revenue',
      ),
      'profit_toman': (fa: 'سود/زیان', en: 'Profit/loss'),
      'break_even_price_per_kg_toman': (
        fa: 'قیمت سربه‌سر هر کیلو',
        en: 'Break-even price/kg',
      ),
      'cost_per_sqm_toman': (fa: 'هزینه هر مترمربع', en: 'Cost per m²'),
    },
  ),
  CalculatorDefinition(
    type: FarmCalculatorType.unitConversion,
    fa: 'تبدیل واحد',
    en: 'Unit converter',
    descriptionFa: 'تبدیل سریع واحدهای پرکاربرد مزرعه',
    descriptionEn: 'Quick conversion of common farm units',
    icon: Icons.swap_horiz_rounded,
    fields: const [
      CalculatorFieldDefinition(
        key: 'value',
        fa: 'مقدار',
        en: 'Value',
        unit: '',
        positive: false,
      ),
      CalculatorFieldDefinition(
        key: 'factor',
        fa: 'ضریب',
        en: 'Factor',
        unit: '',
        initialValue: 0.0001,
      ),
    ],
    results: const {
      'converted_value': (fa: 'مقدار تبدیل‌شده', en: 'Converted value'),
    },
  ),
  CalculatorDefinition(
    type: FarmCalculatorType.pumpFuel,
    fa: 'پمپ و سوخت',
    en: 'Pump & fuel',
    descriptionFa: 'مدت کار، مصرف و هزینه سوخت',
    descriptionEn: 'Runtime, fuel use and fuel cost',
    icon: Icons.local_gas_station_rounded,
    fields: const [
      CalculatorFieldDefinition(
        key: 'flow_lpm',
        fa: 'دبی پمپ',
        en: 'Pump flow',
        unit: 'L/min',
      ),
      CalculatorFieldDefinition(
        key: 'target_volume_l',
        fa: 'حجم هدف',
        en: 'Target volume',
        unit: 'L',
      ),
      CalculatorFieldDefinition(
        key: 'fuel_l_per_hour',
        fa: 'مصرف ساعتی سوخت',
        en: 'Fuel per hour',
        unit: 'L/h',
        positive: false,
      ),
      CalculatorFieldDefinition(
        key: 'fuel_price_toman',
        fa: 'قیمت هر لیتر سوخت',
        en: 'Fuel price per litre',
        unit: 'Toman',
        positive: false,
      ),
    ],
    results: const {
      'duration_minutes': (fa: 'مدت کار پمپ', en: 'Pump runtime'),
      'fuel_l': (fa: 'مصرف سوخت', en: 'Fuel usage'),
      'fuel_cost_toman': (fa: 'هزینه سوخت', en: 'Fuel cost'),
    },
  ),
];
