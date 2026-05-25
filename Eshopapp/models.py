from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db.models.signals import pre_save
from django.dispatch import receiver
import sys
from django.utils import timezone

# Create your models here.

class tbl_admin(models.Model):
    email=models.EmailField(max_length=100,default="")
    pswd=models.CharField(max_length=100,default="")


class tbl_register(models.Model):
    email=models.EmailField(max_length=100,default="")
    phn=models.CharField(max_length=100,default="")
    name=models.CharField(max_length=100,default="")
    uname=models.CharField(max_length=100,default="")
    pswd=models.CharField(max_length=100,default="")
    adrs=models.CharField(max_length=100,default="")
    plc=models.CharField(max_length=100,default="")
    licence_num=models.CharField(max_length=100,default="")
    utype=models.CharField(max_length=100,default="")
    status=models.CharField(max_length=100,default="")
    is_online = models.BooleanField(default=False)

    
class tbl_category(models.Model):
    category = models.CharField(max_length=100, default="")
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    start_price = models.CharField(max_length=100, default="")
    offer = models.CharField(max_length=100, default="")
    category_url = models.CharField(max_length=100, default="")
    qr_image_path = models.ImageField(upload_to='image',default='image/null.png')
    floor = models.CharField(max_length=100, default="")
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img = Image.open(self.image.path)

            # Resize the image to a fixed size (300x300) without antialiasing
            img = img.resize((300, 300), Image.BOX)

            # Save the resized image back to the same path
            img.save(self.image.path)
    
class tbl_products(models.Model):
    image = models.ImageField(upload_to='product_images/')
    category=models.ForeignKey(tbl_category, on_delete=models.CASCADE, blank=True, null=True)
    brand=models.CharField(max_length=100,default="")
    model=models.CharField(max_length=100,default="")
    actual_price=models.CharField(max_length=100,default="")
    our_price = models.CharField(max_length=100,default="")
    discount= models.CharField(max_length=100,default="")
    other_offers=models.CharField(max_length=100,default="")
    size=models.CharField(max_length=100,default="")
    color=models.CharField(max_length=100,default="")
    warranty=models.CharField(max_length=100,default="")
    desc=models.CharField(max_length=1000,default="")
    instock= models.CharField(max_length=100,default="")
    section=models.CharField(max_length=1000,default="")
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img = Image.open(self.image.path)

            # Resize the image to a fixed size (300x300) without antialiasing
            img = img.resize((300, 300), Image.BOX)

            # Save the resized image back to the same path
            img.save(self.image.path)
    # qr_image_path = models.ImageField(upload_to='image',default='null.jpeg')
    


class tbl_wishlist(models.Model):
    products = models.ForeignKey( tbl_products, on_delete=models.CASCADE, blank=True, null=True)
    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE, blank=True, null=True)


class tbl_feedback_rating(models.Model):
    feedback = models.CharField(max_length=100, default='')
    ratings = models.IntegerField(default=0, blank=True, null=True)
    date = models.CharField(max_length=100, default='')
    # status = models.CharField(max_length=100, default='')
    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE, related_name='user_feedback_ratings', blank=True, null=True)
    salesman = models.ForeignKey(tbl_register, on_delete=models.CASCADE, related_name='salesman_feedback_ratings', blank=True, null=True)

class tbl_products_rating(models.Model):
    ratings = models.IntegerField(default=0, blank=True, null=True)
    feedback = models.CharField(max_length=100, default='')
    date = models.CharField(max_length=100, default='')
    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(tbl_products, on_delete=models.CASCADE, blank=True, null=True)
    
class tbl_request_salesman(models.Model):
    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE, related_name='user_requests', blank=True, null=True)
    salesman = models.ForeignKey(tbl_register, on_delete=models.CASCADE, related_name='allocated_requests', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    categories=models.CharField(max_length=100, default='')
    status=models.CharField(max_length=100, default='pending')
    
class user_notification(models.Model):
    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE, related_name='user')
    salesman =models.ForeignKey(tbl_register, on_delete=models.CASCADE,related_name='salesman', null=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
class salesman_notification(models.Model):
    user = models.ForeignKey(tbl_register, on_delete=models.CASCADE, related_name='users')
    salesman = models.ForeignKey(tbl_register, on_delete=models.CASCADE, related_name='salesmans')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    

class Contact(models.Model):
    name = models.CharField(max_length=100, default="")
    email = models.EmailField(max_length=100, default="")
    subject = models.CharField(max_length=100, default="")
    phone_number = models.CharField(max_length=100, default="")
    message = models.TextField(default="")