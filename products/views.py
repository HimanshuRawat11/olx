from account.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from olx import settings
from django.db import transaction
from rest_framework import generics
from .models import productStore,produtcCategory,productSubcategory,product_photos,ProductDetails,ProductTitles
from .serializer import createCategorySerializer,createSubcategorySerializer,addImageSerializer,displayProductsSerializer,displayAdSerializer

class AddCategoryView(APIView):
    
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminUser]
    http_method_names=["post"]
    user=User.objects
    products=productStore.objects
    category=produtcCategory.objects
    
    def post(self,request):
        data=request.data
        serializer=createCategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"The categry was added"})
        return Response(serializer.errors)
    

class AddSubCategoryView(APIView):
    
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated,IsAdminUser]
    http_method_names=["post"]
    user=User.objects
    products=productStore.objects
    category=produtcCategory.objects
    
    def post(self,request):
        data=request.data
        serializer=createSubcategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"The Subcategry was added"})
        return Response(serializer.errors)



class CreateAdView(generics.CreateAPIView):
    
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    http_method_names=["post"]
    user=User.objects
    products=productStore.objects
    
    def post(self,request):
        data=request.data
        product_data={}
        photos=request.FILES.getlist('photo')
        try:
            category=produtcCategory.objects.get(id=data["category"])
            subcategory=productSubcategory.objects.get(id=data["subcategory"])
            with transaction.atomic():
                product_data = {
                "user_id": request.user,
                "display_photo": photos[0] if photos else None, 
                "category": category,
                "subcategory": subcategory,
                "ad_title": data["ad_title"],
                "price": data["price"],
                "description": data["description"],
                "state": data["state"],
                "city": data["city"],
                "district": data["district"] if data["district"] is not None else None,
            }

            relevant_fields = {key: data[key] for key in data if key not in product_data and key != 'photo'}
            product_created=productStore.objects.create(**product_data)
            try:
                product_details = [ProductDetails(
                            product=product_created,
                            title=ProductTitles.objects.get(category=category, sub_category=subcategory, title=key),
                            value=value) for key, value in relevant_fields.items()
                    ]
                ProductDetails.objects.bulk_create(product_details)
                product_photos_created = [product_photos(product=product_created, photos=photo) for photo in photos]
                product_photos.objects.bulk_create(product_photos_created) 
            except Exception as innerexception:
                 product_created.delete()
                 raise innerexception
            return Response("Data Saved",status=status.HTTP_201_CREATED)        
        except Exception as e:
            return Response({"message":"An error occurred","Error Occured":f"{e}"},status=status.HTTP_400_BAD_REQUEST)


class displayAdViewCategory(generics.ListAPIView):

    def list(self, request):
        try:
            data=request.data
            products=productStore.objects.filter(description__icontains=data["category"]).filter(status="Unsold")
            product_list=displayAdSerializer(products,many=True)
            product_data=product_list.data
            # images=product_photos.objects.get(product=products.id)
            return Response(data=product_data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"Error Occured":f"{e}"},status=status.HTTP_400_BAD_REQUEST)
        
class DisplayAllAdView(generics.ListAPIView):

    def list(self, request):
        try:
            # data=request.data
            products=productStore.objects.filter(status="Unsold")
            product_list=displayAdSerializer(products,many=True)
            product_data=product_list.data
            # images=product_photos.objects.get(product=products.id)
            return Response(data=product_data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"Error Occured":f"{e}"},status=status.HTTP_400_BAD_REQUEST)
        
        
class displayAdViewSubcategory(generics.ListAPIView):
    
    def list(self, request):
        try:
            data=request.data
            products=productStore.objects.filter(subcategory=data["subcategory"]).filter(status="Unsold")
            product_list=displayAdSerializer(products,many=True)
            product_data=product_list.data
            return Response(data=product_data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"Error Occured":f"{e}"},status=status.HTTP_400_BAD_REQUEST)


class displayUsersAdView(generics.ListAPIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    
    def list(self, request):
        try:          
            # data=request.data
            id=request.user.id
            products=productStore.objects.filter(user_id_id=id)
    
            product_list=displayAdSerializer(products,many=True)
            product_data=product_list.data
            # images=product_photos.objects.get(product=products.id)
            return Response(data=product_data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"Error Occured":f"{e}"},status=status.HTTP_400_BAD_REQUEST)


# class UpdateProductView(APIView):
#     authentication_classes=[JWTAuthentication]
#     permission_classes=[IsAuthenticated]
#     http_method_names=['patch']

#     def 