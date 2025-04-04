from rest_framework.serializers import ModelSerializer
from .models import productStore,productSubcategory,produtcCategory,product_photos,ProductDetails
from django.db import transaction 
from .models import ProductTitles,ProductDetails
class createCategorySerializer(ModelSerializer):
    
    class Meta:
        model=produtcCategory
        fields="__all__"
        
        
class createSubcategorySerializer(ModelSerializer):
    
    class Meta:
        model=productSubcategory
        fields="__all__"

class ProductDetailSerializer(ModelSerializer):
    
    class Meta:
        model=ProductDetails
        fields="__all__"



# class createAdSerializer(ModelSerializer):    
#     product_details=ProductDetailSerializer()
    
#     class Meta:
#         model=productStore
#         fields="__all__"
    
#     def create(self, validated_data):
        
        
class addImageSerializer(ModelSerializer):
    
    class Meta:
        model=product_photos
        fields="__all__"

class displayProductsSerializer(ModelSerializer):
    
    class Meta:
        model=productStore
        fields="__all__"


class displayAdSerializer(ModelSerializer):
    
    class Meta:
        model=productStore
        fields="__all__"