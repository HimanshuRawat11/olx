from django.db import models
from account.models import User
# Create your models here.

class produtcCategory(models.Model):
    category_name=models.CharField(max_length=250,blank=False)
    def __str__(self):
        return self.category_name
    class Meta:
        db_table="produtCategory"

class productSubcategory(models.Model):
    cat_id=models.ForeignKey(produtcCategory,on_delete=models.CASCADE,related_name="cat_id")
    subcategory_name=models.CharField(max_length=250,blank=False)
    
    def __str__(self):
        return self.subcategory_name
    
    class Meta:
        db_table="productSubcategory"

class productStore(models.Model):
    class current_status(models.TextChoices):
        Sold="Sold"
        Unsold="Unsold"
        deleted="Deleted"
    
    category=models.ForeignKey(produtcCategory,on_delete=models.CASCADE)
    subcategory=models.ForeignKey(productSubcategory,on_delete=models.CASCADE)
    user_id=models.ForeignKey(User,on_delete=models.CASCADE)
    ad_title=models.CharField(max_length=200,null=False,blank=False)
    price=models.DecimalField(max_digits=10,decimal_places=2,null=False,blank=False)
    description=models.TextField()
    status=models.CharField(max_length=10,choices=current_status.choices,default=current_status.Unsold)    
    date_added=models.DateField(auto_now_add=True)
    state=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    district=models.CharField(max_length=100,null=True,blank=True)
    display_photo=models.ImageField(default=None)
    
    class Meta:
        db_table="products"
        
    def __str__(self):
        return self.ad_title

    
class ProductTitles(models.Model):
    category=models.ForeignKey(produtcCategory,on_delete=models.CASCADE)
    sub_category=models.ForeignKey(productSubcategory,on_delete=models.CASCADE)
    title=models.CharField(max_length=200)
    
    def __str__(self):
        return self.title
    
    class Meta:
        db_table="product_details_title"

class ProductDetails(models.Model):
    product=models.ForeignKey(productStore,on_delete=models.CASCADE)
    title=models.ForeignKey(ProductTitles,on_delete=models.CASCADE)
    value=models.CharField(max_length=200)
    
    class Meta:
        db_table="product_details"        
    def __str__(self):
        return self.value

class product_photos(models.Model):
    product=models.ForeignKey(productStore,on_delete=models.Case)
    photos=models.ImageField()
    
    class Meta:
        db_table="products_photos"
