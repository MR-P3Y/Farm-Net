import '../data/store_models.dart';

class StoreState {
  const StoreState({
    required this.isLoading,
    this.isSaving = false,
    this.publicStores = const [],
    this.selectedPublicStore,
    this.myStore,
    this.errorMessage,
  });

  final bool isLoading;
  final bool isSaving;
  final List<Store> publicStores;
  final Store? selectedPublicStore;
  final Store? myStore;
  final String? errorMessage;

  factory StoreState.initial() {
    return const StoreState(isLoading: false);
  }

  StoreState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<Store>? publicStores,
    Store? selectedPublicStore,
    Store? myStore,
    String? errorMessage,
    bool clearSelected = false,
    bool clearMyStore = false,
    bool clearError = false,
  }) {
    return StoreState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      publicStores: publicStores ?? this.publicStores,
      selectedPublicStore:
          clearSelected
              ? null
              : selectedPublicStore ?? this.selectedPublicStore,
      myStore: clearMyStore ? null : myStore ?? this.myStore,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}
