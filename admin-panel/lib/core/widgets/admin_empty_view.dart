import 'package:flutter/material.dart';

class AdminEmptyView extends StatelessWidget {
  const AdminEmptyView({
    super.key,
    this.message = 'موردی برای نمایش وجود ندارد',
  });

  final String message;

  @override
  Widget build(BuildContext context) {
    return Center(child: Text(message));
  }
}
