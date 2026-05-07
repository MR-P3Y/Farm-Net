import 'package:flutter/material.dart';

class FarmStatusChip extends StatelessWidget {
  const FarmStatusChip({
    super.key,
    required this.label,
  });

  final String label;

  @override
  Widget build(BuildContext context) {
    return Chip(
      label: Text(label),
      visualDensity: VisualDensity.compact,
    );
  }
}