import 'package:flutter/material.dart';

import '../utils/money.dart';

class FarmPriceText extends StatelessWidget {
  const FarmPriceText({
    super.key,
    required this.amountToman,
  });

  final num amountToman;

  @override
  Widget build(BuildContext context) {
    return Text(
      formatToman(amountToman),
      style: Theme.of(context).textTheme.titleMedium,
    );
  }
}