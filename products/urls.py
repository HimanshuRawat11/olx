from django.urls import path,include
from .views import AddCategoryView,AddSubCategoryView,CreateAdView,displayAdViewCategory,displayUsersAdView,displayAdViewSubcategory,DisplayAllAdView


urlpatterns = [
    path("post/add/",CreateAdView.as_view(),name="product_add"),
    path("category/add/",AddCategoryView.as_view(),name="add_category"),
    path("category/subcategory/add/",AddSubCategoryView.as_view(),name="add_subcategory"),
    path("list/",displayAdViewCategory.as_view(),name="list_products"),
    path("list/subcategory/",displayAdViewSubcategory.as_view(),name="list_products_subcategory"),
    path("user/ads/",displayUsersAdView.as_view(),name="users_products"),
    path("list/ads/",DisplayAllAdView.as_view(),name="diplay_all"),
]

