from rest_framework import serializers
from product.models import Category, Brand, Product, ProductFeature, Discount, DiscountCode, Image, FeatureValue, \
    Feature, ProductColor, ProductStock


# === Image Serializer ===
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'file', 'title', 'description']


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ['id', 'name']


class FeatureValueSerializer(serializers.ModelSerializer):
    feature = FeatureSerializer(read_only=True)

    class Meta:
        model = FeatureValue
        fields = ['id', 'value', 'feature', 'color_swatch', 'hex_code']


class ProductFeatureSerializer(serializers.ModelSerializer):
    feature_value = FeatureValueSerializer()

    class Meta:
        model = ProductFeature
        fields = ['feature_value']


# === Discount Serializer (for single product) ===
class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = ['value', 'discount_type', 'start_date', 'end_date', 'active']

# === Product Color Serializer ===
class ProductColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = ['name', 'hex_code']

# === Product Serializer (Main) ===
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    brand = serializers.StringRelatedField()
    discount = DiscountSerializer(read_only=True)
    features = ProductFeatureSerializer(many=True, read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    final_price = serializers.SerializerMethodField()
    colors = ProductColorSerializer(many=True, read_only=True)


    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'category', 'brand',
                  'price', 'weight', 'image', 'created', 'updated',
                  'is_active', 'final_price', 'features', 'images', 'discount', 'colors']

    def get_final_price(self, obj):
        return obj.get_final_price()


# === Nested Category Serializer ===
class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)
    is_main_branch = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'subcategories', 'is_main_branch']

    def get_is_main_branch(self, obj):
        return obj.is_main_branch()



# === Brand Serializer ===
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'description']


# === ProductStock Serializer ===
class ProductStockSerializer(serializers.ModelSerializer):
    color = ProductColorSerializer()
    feature_value = FeatureValueSerializer()

    class Meta:
        model = ProductStock
        fields = ['id', 'color', 'feature_value', 'price', 'quantity']
