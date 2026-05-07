import 'package:flutter/material.dart';

class FarmLoadingView extends StatelessWidget {
  const FarmLoadingView({super.key});

  @override
  Widget build(BuildContext context) {
    return const Center(
      child: CircularProgressIndicator(),
    );
  }
}