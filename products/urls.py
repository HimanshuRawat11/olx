from django.urls import path,include
from .views import addCategoryView,addSubCategoryView,CreateAdView,displayAdViewCategory,displayUsersAdView,displayAdViewSubcategory,DisplayAllAdView


urlpatterns = [
    path("post/add/",CreateAdView.as_view(),name="product_add"),
    path("category/add/",addCategoryView.as_view(),name="add_category"),
    path("category/subcategory/add/",addSubCategoryView.as_view(),name="add_subcategory"),
    path("list/",displayAdViewCategory.as_view(),name="list_products"),
    path("list/subcategory/",displayAdViewSubcategory.as_view(),name="list_products_subcategory"),
    path("user/ads/",displayUsersAdView.as_view(),name="users_products"),
    path("list/ads/",DisplayAllAdView.as_view(),name="diplay_all"),
]

