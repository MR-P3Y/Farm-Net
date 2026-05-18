import '../data/product_models.dart';

class ProductState {
  const ProductState({
    required this.isLoading,
    this.isSaving = false,
    this.publicProducts = const [],
    this.storeProducts = const [],
    this.myProducts = const [],
    this.selectedProduct,
    this.errorMessage,
  });

  final bool isLoading;
  final bool isSaving;
  final List<Product> publicProducts;
  final List<Product> storeProducts;
  final List<Product> myProducts;
  final Product? selectedProduct;
  final String? errorMessage;

  factory ProductState.initial() {
    return const ProductState(isLoading: false);
  }

  ProductState copyWith({
    bool? isLoading,
    bool? isSaving,
    List<Product>? publicProducts,
    List<Product>? storeProducts,
    List<Product>? myProducts,
    Product? selectedProduct,
    String? errorMessage,
    bool clearSelected = false,
    bool clearError = false,
  }) {
    return ProductState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      publicProducts: publicProducts ?? this.publicProducts,
      storeProducts: storeProducts ?? this.storeProducts,
      myProducts: myProducts ?? this.myProducts,
      selectedProduct:
          clearSelected ? null : selectedProduct ?? this.selectedProduct,
      errorMessage: clearError ? null : errorMessage ?? this.errorMessage,
    );
  }
}
