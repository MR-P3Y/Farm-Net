import 'package:flutter/material.dart';

class FarmEmptyView extends StatelessWidget {
  const FarmEmptyView({
    super.key,
    this.message = 'موردی برای نمایش وجود ندارد',
  });

  final String message;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Text(message, textAlign: TextAlign.center),
    );
  }
}