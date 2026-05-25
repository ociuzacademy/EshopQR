from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse_lazy
from.models import*
from django.http import HttpResponse,HttpResponseRedirect, QueryDict,JsonResponse
from django.contrib import messages
from django.urls import reverse
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.db import IntegrityError
from django.db.models import Avg
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Avg, Count
from django.core.exceptions import MultipleObjectsReturned
from .models import Contact
def generate_star_icons(rating):
    full_stars = int(rating)
    half_star = 1 if rating % 1 >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star

    return {
        'full_stars': range(full_stars),
        'half_star': half_star,
        'empty_stars': range(empty_stars),
    }
# Create your views here.

def index(request):
    return render(request,'index.html')
def about(request):
    return render(request,'about.html')
def contact(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        message = request.POST.get('message')
        # Save to the database
        Contact.objects.create(name=name, email=email, phone_number=phone_number, message=message)
        # Redirect after successful submission (you can customize the URL)
        return render(request, 'contact.html')
    return render(request, 'contact.html')

def all_view_category(request):
    # Get all categories from the database
    all_categories = tbl_category.objects.all()

    # Set the number of items per page
    items_per_page = 4  # You can adjust this value as needed

    # Create a Paginator instance
    paginator = Paginator(all_categories, items_per_page)

    # Get the current page number from the request's GET parameters
    page = request.GET.get('page')

    try:
        # Get the requested page
        categories = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, set it to the first page
        categories = paginator.page(1)
    except EmptyPage:
        # If the page is out of range, deliver the last page of results
        categories = paginator.page(paginator.num_pages)

    return render(request, 'all_view_category.html', {'categories': categories})



def all_view_qr(request):
    # Get all categories from the database
    all_categories = tbl_category.objects.all()

    # Set the number of items per page
    items_per_page = 4

    # Create a Paginator instance
    paginator = Paginator(all_categories, items_per_page)

    # Get the current page number from the request's GET parameters
    page = request.GET.get('page')

    try:
        # Get the requested page
        categories = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, set it to the first page
        categories = paginator.page(1)
    except EmptyPage:
        # If the page is out of range, deliver the last page of results
        categories = paginator.page(paginator.num_pages)

    return render(request, 'all_view_qr.html', {'categories': categories})

def all_view_products(request, id):
    products = tbl_products.objects.filter(category_id=id)
    # Generate the URL for all_view_products
    category_url1 = reverse('all_view_products', args=[id])
    category_url = f'417sptdw-8000.inc1.devtunnels.ms/{category_url1}'
    # Update the category object with the transformed URL
    category = tbl_category.objects.get(pk=id)
    category.category_url = category_url
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(category_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # Delete previous QR code image
    previous_qr_image_path = category.qr_image_path.path
    if os.path.exists(previous_qr_image_path):
        os.remove(previous_qr_image_path)

    # Save the new QR code image to BytesIO
    image_stream = BytesIO()
    qr_img.save(image_stream, format='PNG')
    image_stream.seek(0)

    # Save QR code image to qr_image_path field
    category.qr_image_path.save(f"{category.category}_qr.png", ContentFile(image_stream.read()), save=True)
    category.save(update_fields=['category_url', 'qr_image_path'])
    
     # Calculate the average rating and count of ratings for each product
    product_data = []

    for product in products:
        # Retrieve all product ratings for the current product
        product_ratings = tbl_products_rating.objects.filter(product=product)

        # Calculate the average rating using Django's Avg aggregation function
        avg_rating = product_ratings.aggregate(Avg('ratings'))['ratings__avg']

        # Calculate the count of ratings using Django's Count aggregation function
        ratings_count = product_ratings.aggregate(Count('ratings'))['ratings__count']

        product_data.append({
            'product': product,
            'avg_rating': avg_rating if avg_rating else 0,  # Set to 0 if there are no ratings
            'ratings_count': ratings_count,
        })
    
    
    # Search query
    search_query = request.GET.get('search', '')
    if search_query:
        products = tbl_products.objects.filter(category_id=id,brand__icontains=search_query)| products.filter(category_id=id,model__icontains=search_query)| products.filter(category_id=id, color__icontains=search_query)
    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(products, 4)  # Show 6 products per page
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'all_view_products.html', {'products': products,'category':category,'search_query':search_query,'product_data':product_data})


def all_view_productdetails(request, id):
    product = tbl_products.objects.get(id=id)
    category_floor = tbl_category.objects.get(id=product.category_id).floor
    context = {
        'category_floor':category_floor,
        'product': product}
    return render(request, 'all_view_productdetails.html', context)

def user_register(request):
    error_message = None
    registration_success = False

    if request.method == 'POST':
        name = request.POST.get('name')
        uname = request.POST.get('uname')
        email = request.POST.get('email')
        pswd = request.POST.get('pswd')
        cpswd = request.POST.get('cpswd')
        adrs = request.POST.get('adrs')
        phn = request.POST.get('phn')
        plc = request.POST.get('plc')

        # Check if the email already exists
        if tbl_register.objects.filter(email=email).exists():
            error_message = "Email already exists. Please use a different email."
        elif pswd != cpswd:
            error_message = "Passwords do not match."
        else:
            # If the email and passwords match, save the new user
            tbl_register.objects.create(name=name, uname=uname, email=email, pswd=pswd, adrs=adrs, phn=phn, plc=plc, utype='user')
            registration_success = True

    return render(request, 'user_register.html', {'error_message': error_message, 'registration_success': registration_success})
     

     



def login(request):
    if request.method == "POST":
        pswd = request.POST['pswd']
        email = request.POST['email']
        var = tbl_register.objects.all().filter(pswd=pswd, email=email, utype='user')
        var2 = tbl_register.objects.all().filter(pswd=pswd, email=email, utype='salesman')
        var4= tbl_admin.objects.all().filter(pswd=pswd, email=email)

        if var:
            for x in var:
                request.session['id'] = x.id
            return render(request, 'user/user_home.html')
        if var2:
            for x in var2:
                request.session['id'] = x.id
            return render(request, 'salesman/salesman_home.html')
        elif var4:
            for x in var4:
                request.session['id'] = x.id
                # next_url = request.GET.get('next', reverse_lazy('/'))
                # return redirect(next_url)
            return render(request, 'admin/admin_home.html',{'login_success': True})

        else:
            txt = """<script>alert("Invalid user Credentials....");window.location='/';</script>"""
            return HttpResponse(txt) 
    else:
        return render(request, "login.html")
    


def user_home(request):
    return render(request, 'user/user_home.html')

def user_view_category(request):
    data=tbl_category.objects.all()
    return render(request,'user/all_view_category.html',{'categories':data})

def user_view_products(request, id):
    category = tbl_category.objects.get(pk=id)
    products = tbl_products.objects.filter(category_id=id)

    # Calculate the average rating and count of ratings for each product
    product_data = []

    for product in products:
        # Retrieve all product ratings for the current product
        product_ratings = tbl_products_rating.objects.filter(product=product)

        # Calculate the average rating using Django's Avg aggregation function
        avg_rating = product_ratings.aggregate(Avg('ratings'))['ratings__avg']

        # Calculate the count of ratings using Django's Count aggregation function
        ratings_count = product_ratings.aggregate(Count('ratings'))['ratings__count']

        product_data.append({
            'product': product,
            'avg_rating': avg_rating if avg_rating else 0,  # Set to 0 if there are no ratings
            'ratings_count': ratings_count,
        })

    # Search query
    search_query = request.GET.get('search', '')
    if search_query:
        products = tbl_products.objects.filter(category_id=id, brand__icontains=search_query) | \
                   products.filter(category_id=id, model__icontains=search_query) | \
                   products.filter(category_id=id, color__icontains=search_query)

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(products, 4)  # Show 4 products per page

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'user/all_view_products.html', {'products': products, 'category': category, 'search_query': search_query, 'product_data': product_data})

def user_view_productdetails(request, id):
    product = tbl_products.objects.get(id=id)
    category_floor = tbl_category.objects.get(id=product.category_id).floor
    context = {
        'category_floor':category_floor,
        'product': product}
    return render(request, 'user/all_view_productdetails.html', context)

def user_view_salesman(request):
    salesman = tbl_register.objects.filter(utype='salesman')
    return render(request, 'user/user_view_salesmen.html', {'salesman': salesman})

def user_request_salesman(request):
    if request.method == 'POST':
        user_id = request.session.get('id')
        categories = request.POST.get('categories')
        
        # Fetch the user instance using get_object_or_404
        user = get_object_or_404(tbl_register, id=user_id)
        
        # Check if there is any pending request for the same user
        pending_request = tbl_request_salesman.objects.filter(user=user, status="pending").first()
        
        if pending_request:
            # Update the existing pending request
            pending_request.categories = categories
            pending_request.save()
            message = 'Salesman request updated successfully'
        else:
            # Create a new request
            tbl_request_salesman.objects.create(user=user, categories=categories, status="pending")
            message = 'Salesman request submitted successfully'

        return render(request, 'user/user_request_salesman.html', {'message': message})
    
    return render(request, 'user/user_request_salesman.html')
       
from django.shortcuts import render
def user_add_salesman_rating(request, id):
    salesman = get_object_or_404(tbl_register, id=id)
    user_id = request.session.get('id')

    if user_id is not None:
        user_notifications = user_notification.objects.filter(user_id=user_id).order_by('-timestamp')

    if request.method == 'POST':
        user = get_object_or_404(tbl_register, id=user_id)
        feedback = request.POST.get('feedback')
        ratings = request.POST.get('ratings')

        # Check if the user has already rated the salesman using filter()
        existing_feedbacks = tbl_feedback_rating.objects.filter(user=user, salesman=salesman)

        if existing_feedbacks.exists():
            # If feedback exists, update the existing instance
            feedback_instance = existing_feedbacks.first()
        else:
            # If feedback doesn't exist, create a new instance
            feedback_instance = tbl_feedback_rating(user=user, salesman=salesman)

        # Update the instance fields
        feedback_instance.feedback = feedback
        feedback_instance.ratings = ratings
        feedback_instance.date = timezone.now()  # Set the current date
        feedback_instance.save()

        # Redirect to the notification page after successful submission
        return redirect('/user_view_notification/')

    return render(request, 'user/user_add_salesman_rating.html', {'salesman': salesman, 'user_notifications': user_notifications})


# views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import tbl_products, tbl_products_rating
from django.contrib import messages
from django.utils import timezone  # Import timezone module

def user_add_product_rating(request, product_id):
    product = get_object_or_404(tbl_products, id=product_id)
    user_id = request.session.get('id')
    
    # Retrieve the user instance using the session ID
    user = get_object_or_404(tbl_register, id=user_id)

    if request.method == 'POST':
        # Assuming you have a form with 'rating' and 'feedback' fields
        rating_value = request.POST.get('ratings')
        feedback = request.POST.get('feedback')

        # Check if the user has already rated the product
        existing_rating = tbl_products_rating.objects.filter(product=product, user=user).first()

        if existing_rating:
            # If a rating exists, update it
            existing_rating.ratings = rating_value
            existing_rating.feedback = feedback
            existing_rating.date = timezone.now()  # Update the date to the current date and time
            existing_rating.save()
            messages.success(request, 'Rating updated successfully!')
        else:
            # If no rating exists, create a new one
            new_rating = tbl_products_rating.objects.create(
                product=product,
                user=user,
                ratings=rating_value,
                feedback=feedback,
                date=timezone.now()  # Set to the current date and time
            )
            messages.success(request, 'Rating added successfully!')

        return redirect('/user_view_category/')  # Redirect to the product view page or any other page

    return render(request, 'user/user_add_product_rating.html', {'product': product})




def add_to_wishlist(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')

        # Check if the product is already in the wishlist for the current session
        user_id = request.session.get('id')
        is_in_wishlist = tbl_wishlist.objects.filter(user_id=user_id, products_id=product_id).exists()

        if is_in_wishlist:
            return JsonResponse({'success': False, 'message': 'This product is already in your wishlist.'})
        else:
            # Add the product to the wishlist
            tbl_wishlist.objects.create(user_id=user_id, products_id=product_id)
            return JsonResponse({'success': True, 'message': 'Product added to wishlist successfully.'})

    # Handle other cases, like GET requests
    return JsonResponse({'success': False, 'message': 'Invalid request.'})


def view_wishlist(request):
    user_id = request.session.get('id')
    # Retrieve wishlist items
    wishlist_items = tbl_wishlist.objects.filter(user_id=user_id)
    # Create a list to store wishlist details
    wishlist_details = []

    # Loop through each wishlist item and fetch associated product details
    for wishlist_item in wishlist_items:
        if wishlist_item.products:  # Check if products is not None
            product_detail = {
                'product': wishlist_item.products,
                'brand': wishlist_item.products.brand,
                'model': wishlist_item.products.model,
                'image_url': wishlist_item.products.image.url,
            }
            wishlist_details.append(product_detail)

    num_items = len(wishlist_details)
    context = {
        'wishlist_details': wishlist_details,
        'num_items': num_items,
    }
    return render(request, 'user/view_wishlist.html', context)





# Your existing views...
def remove_from_wishlist(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        user_id = request.session.get('id')

        # Print statements for debugging
        print(f"Product ID: {product_id}")
        print(f"User ID: {user_id}")

        # Find the wishlist item to remove
        wishlist_item = get_object_or_404(tbl_wishlist, user_id=user_id, products_id=product_id)

        # Remove the item from the wishlist
        wishlist_item.delete()

        return redirect('view_wishlist')  # Redirect to the wishlist page

    return render(request, 'error.html', {'message': 'Invalid request.'})

def user_view_notification(request):
    user_id = request.session.get('id')
    if user_id is not None:
        user_notifications = user_notification.objects.filter(user_id=user_id).order_by('-timestamp')
        user_requests = tbl_request_salesman.objects.filter(user_id=user_id)
        # Initialize salesman_id before the for loop
        salesman_id = None
        for user_request in user_requests:
            # Accessing the salesman_id for each user_request
            salesman_id = user_request.salesman_id
            print(salesman_id)
        return render(request, 'user/user_view_notification.html', {'user_notifications': user_notifications, 'salesman_id': salesman_id})
    else:
        # Handle the case when user ID is not in the session
        return HttpResponse("User ID not found in the session.")

def shop_home(request):
    return render(request,'shop/shop_home.html')


def admin_home(request):
    return render(request,'admin/admin_home.html')

def admin_add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category')
        category_image = request.FILES.get('image')
        start_price = request.POST.get('start_price')
        offer = request.POST.get('offer')
        floor = request.POST.get('floor')

        # Check if the category already exists
        if not tbl_category.objects.filter(category=category_name).exists():
            # If the category doesn't exist, create it.
            category = tbl_category.objects.create(
                category=category_name,
                start_price=start_price,
                offer=offer,
                floor=floor,
                # Save the image to the media directory
                image=category_image
            )

            # You may want to save the image with a unique name to prevent overwrites
            image_path = os.path.join(settings.MEDIA_ROOT, 'category_images', f"{category.id}_{category_image.name}")
            with open(image_path, 'wb') as destination:
                for chunk in category_image.chunks():
                    destination.write(chunk)

            # Update the category image field with the new path
            category.image = f"category_images/{category.id}_{category_image.name}"
            category.save()

            return render(request, 'admin/admin_add_category.html')

    return render(request, 'admin/admin_add_category.html')

def admin_view_category(request):
    categories = tbl_category.objects.all()
    items_per_page = 5
    paginator = Paginator(categories, items_per_page)
    page = request.GET.get('page', 1)
    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        categories = paginator.page(1)
    except EmptyPage:
        categories = paginator.page(paginator.num_pages)
    return render(request, 'admin/admin_view_category.html', {'categories': categories})

from django.shortcuts import render, get_object_or_404, redirect

def admin_edit_category(request, id):
    category = get_object_or_404(tbl_category, id=id)

    if request.method == 'POST':
        # Process the form submission
        category.category = request.POST.get('category')
        category.start_price = request.POST.get('start_price')
        category.offer = request.POST.get('offer')
        category.floor = request.POST.get('floor')

        # Handle image field
        if 'image' in request.FILES:
            category.image = request.FILES['image']

        category.save()
        messages.success(request, 'Category updated successfully.')

        return redirect('/admin_view_category')  # Use the correct URL pattern name
    else:
        # Display the form
        return render(request, 'admin/admin_edit_category.html', {'category': category})

def admin_delete_category(request, id):
    category = tbl_category.objects.get(id=id)
    category.delete()

    # Redirect to the student list page or any other desired page
    return redirect('/admin_view_category')

def category(request):
    categories = tbl_category.objects.all()
    items_per_page = 4
    paginator = Paginator(categories, items_per_page)
    page = request.GET.get('page', 1)
    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        categories = paginator.page(1)
    except EmptyPage:
        categories = paginator.page(paginator.num_pages)
    return render(request, 'admin/category.html', {'categories': categories})


def admin_view_products(request, id):
    products = tbl_products.objects.filter(category_id=id)
    category = tbl_category.objects.get(pk=id)
    items_per_page = 5
    paginator = Paginator(products, items_per_page)
    page = request.GET.get('page', 1)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'admin/admin_view_products.html', {'products': products, 'category': category})
    # # Generate the URL for admin_view_products
    # category_url = reverse('admin_view_products', args=[id])

    # # Update the category object with the transformed URL
    # category = tbl_category.objects.get(pk=id)
    # category.category_url = category_url

    # # Generate QR code
    # qr = qrcode.QRCode(
    #     version=1,
    #     error_correction=qrcode.constants.ERROR_CORRECT_L,
    #     box_size=10,
    #     border=4,
    # )
    # qr.add_data(category_url)
    # qr.make(fit=True)
    # qr_img = qr.make_image(fill_color="black", back_color="white")

    # # Delete previous QR code image
    # previous_qr_image_path = category.qr_image_path.path
    # if os.path.exists(previous_qr_image_path):
    #     os.remove(previous_qr_image_path)

    # # Save the new QR code image to BytesIO
    # image_stream = BytesIO()
    # qr_img.save(image_stream, format='PNG')
    # image_stream.seek(0)

    # # Save QR code image to qr_image_path field
    # category.qr_image_path.save(f"{category.category}_qr.png", ContentFile(image_stream.read()), save=True)
    # category.save(update_fields=['category_url', 'qr_image_path'])

    # return render(request, 'admin/admin_view_products.html', {'products': products,'category':category})

import os


def admin_add_products(request, id):
    if request.method == 'POST':
        # Extract form data from the request
        image = request.FILES.get('image')  # Use 'image' instead of 'product_image'
        category_id = id
        brand = request.POST.get('brand')
        model = request.POST.get('model')
        actual_price = request.POST.get('actual_price')
        discount = request.POST.get('discount')
        our_price = int(actual_price)-(int(actual_price)*(int(discount)/100))
        size = request.POST.get('size')
        color = request.POST.get('color')
        warranty = request.POST.get('warranty')
        desc = request.POST.get('desc')
        instock=request.POST.get('instock')
        section=request.POST.get('section')

        # Create a new product instance
        product = tbl_products.objects.create(image=image,  # Use 'image' instead of 'product_image'
            category_id=category_id,
            brand=brand,
            model=model,
            actual_price=actual_price,
            our_price=our_price,
            discount=discount,
            size=size,
            color=color,
            warranty=warranty,
            desc=desc,
            instock=instock,
            section=section
        )

        # Save the uploaded image with a unique name
        image_path = os.path.join(settings.MEDIA_ROOT, 'product_images', f"{product.id}_{image.name}")
        with open(image_path, 'wb') as destination:
            for chunk in image.chunks():
                destination.write(chunk)

        # Update the product image field with the new path
        product.image = f"product_images/{product.id}_{image.name}"
        product.save()

        return render(request, 'admin/admin_add_products.html', {'category_id': id})

    return render(request, 'admin/admin_add_products.html', {'category_id': id})



def admin_edit_product(request, id):
    product = tbl_products.objects.get(id=id)
    if request.method == 'POST':
        brand = request.POST.get('brand')
        model = request.POST.get('model')
        actual_price = request.POST.get('actual_price')
        discount = request.POST.get('discount')
        our_price = int(actual_price)-(int(actual_price)*(int(discount)/100))
        size = request.POST.get('size')
        color = request.POST.get('color')
        warranty = request.POST.get('warranty')
        desc = request.POST.get('desc')
        other_offers=request.POST.get('other_offers')
        instock=request.POST.get('instock')
        section=request.POST.get('section')
        if 'image' in request.FILES:
            image = request.FILES.get('image')
            product.image = image
        

        # Update product data in the database
        product.brand = brand
        product.model = model
        product.actual_price = actual_price
        product.our_price=our_price
        product.discount = discount
        product.size = size
        product.color = color
        product.warranty = warranty
        product.desc = desc
        product.instock = instock
        product.section=section
        product.other_offers = other_offers

        # Save the changes
        product.save()
        # Redirect or render as needed
        return render(request, 'admin/admin_edit_product.html', {'product': product})
    else:
        # Pass the existing product data to the HTML template for pre-filling the form
        return render(request, 'admin/admin_edit_product.html', {'product': product})
    
def admin_delete_product(request, id):
    product = tbl_products.objects.filter(id=id)
    product.delete()
    # Redirect to the student list page or any other desired page
    return redirect('/admin_view_products')

def admin_add_salesman(request):
    error_message = None
    success_message = None

    if request.method == 'POST':
        name = request.POST.get('name')
        uname = request.POST.get('uname')
        email = request.POST.get('email')
        adrs = request.POST.get('adrs')
        phn = request.POST.get('phn')
        plc = request.POST.get('plc')
        licence_num = request.POST.get('licence_num')

        try:
            # Generate a random password
            pswd = generate_random_password(name, phn)

            # Create a new salesman
            new_salesman = tbl_register(
                name=name,
                uname=uname,
                email=email,
                pswd=pswd,
                adrs=adrs,
                phn=phn,
                plc=plc,
                licence_num=licence_num,
                utype='salesman',
                status='busy',
                is_online=False
            )

            new_salesman.save()

            # Set the success message
            success_message = f"Salesman {name} added successfully. Email: {email}, Password: {pswd}"

        except IntegrityError:
            # Handle the case when a duplicate email is detected
            error_message = "Email already exists. Please use a different email."

    return render(request, 'admin/admin_add_salesman.html', {'success_message': success_message, 'error_message': error_message})

import secrets
import string

def generate_random_password(username, phone_number, length=8):
    if length <= 7:
        length = 8

    username_prefix = username[:4]
    last_four_digits = phone_number[4:]

    # characters = string.ascii_letters + string.digits + string.punctuation
    # random_part = ''.join(secrets.choice(characters) for _ in range(length - 7))

    password = f"{username_prefix}{last_four_digits}"
    return password

   
def admin_add_salesman(request):
    success_message = None
    if request.method=='POST':
        name=request.POST.get('name')
        uname=request.POST.get('uname')
        email=request.POST.get('email')
        
        adrs=request.POST.get('adrs')
        phn=request.POST.get('phn')
        plc=request.POST.get('plc')
        licence_num=request.POST.get('licence_num')
        pswd = generate_random_password(name, phn)
        # licence=request.POST.get('licence')
        tbl_register(name=name,uname=uname,email=email,pswd=pswd,adrs=adrs,phn=phn,plc=plc,licence_num=licence_num,utype='salesman',status='offline').save()
        # Set the success message
        success_message = f"Salesman {name} added successfully. Email: {email}, Password: {pswd}"
        return render(request, 'admin/admin_add_salesman.html', {'success_message': success_message})
    else:
        return render(request, 'admin/admin_add_salesman.html', {'success_message': success_message})
    
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from .models import tbl_register  # Import your actual model

def admin_view_salesman(request):
    salesman_list = tbl_register.objects.filter(utype='salesman')

    # Set the number of items per page
    items_per_page = 10  # Adjust this value as needed

    # Create a Paginator instance
    paginator = Paginator(salesman_list, items_per_page)

    # Get the current page number from the request's GET parameters
    page = request.GET.get('page')

    try:
        # Get the requested page
        salesmen = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, set it to the first page
        salesmen = paginator.page(1)
    except EmptyPage:
        # If the page is out of range, deliver the last page of results
        salesmen = paginator.page(paginator.num_pages)

    return render(request, 'admin/admin_view_salesmen.html', {'salesmen': salesmen})



def admin_view_salesman_ratings(request):
    # Retrieve all salesmen
    salesmen = tbl_register.objects.filter(utype='salesman')

    # Create a list to store salesman data with their overall rating
    salesman_data = []

    for salesman in salesmen:
        # Retrieve all feedback instances for the current salesman
        feedback_instances = tbl_feedback_rating.objects.filter(salesman=salesman)

        # Calculate the average rating using Django's Avg aggregation function
        avg_rating = feedback_instances.aggregate(Avg('ratings'))['ratings__avg']

        # Append the salesman data with the calculated average rating
        salesman_data.append({
            'salesman': salesman,
            'avg_rating': avg_rating if avg_rating else 0  # Set to 0 if there are no ratings
        })

    # Set the number of items per page
    items_per_page = 10  # Adjust this value as needed

    # Create a Paginator instance
    paginator = Paginator(salesman_data, items_per_page)

    # Get the current page number from the request's GET parameters
    page = request.GET.get('page')

    try:
        # Get the requested page
        salesman_data_page = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, set it to the first page
        salesman_data_page = paginator.page(1)
    except EmptyPage:
        # If the page is out of range, deliver the last page of results
        salesman_data_page = paginator.page(paginator.num_pages)

    return render(request, 'admin/admin_view_salesman_ratings.html', {'salesman_data': salesman_data_page})


def admin_view_salesman_feedbacks(request, salesman_id):
    # Get the salesman object or return a 404 response if not found
    salesman = get_object_or_404(tbl_register, id=salesman_id)
    
    # Retrieve all feedback instances for the current salesman and order them by datetime
    feedback_instances = tbl_feedback_rating.objects.filter(salesman=salesman).order_by('-date')

    return render(request, 'admin/admin_view_salesman_feedbacks.html', {'salesman': salesman, 'feedback_instances': feedback_instances})

def admin_delete_salesman(request, salesman_id):
    salesman = tbl_register.objects.filter(utype='salesman')
    s_man = get_object_or_404(tbl_register, id=salesman_id)
    s_man.delete()
    messages.success(request, 'Salesman deleted successfully.')
    return render(request, 'admin/admin_view_salesmen.html', {'salesman': salesman})

def admin_edit_salesman(request, salesman_id):
    salesman = tbl_register.objects.get(id=salesman_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        uname = request.POST.get('uname')
        email = request.POST.get('email')
        pswd = request.POST.get('pswd')
        adrs = request.POST.get('adrs')
        phn = request.POST.get('phn')
        plc = request.POST.get('plc')
        licence_num = request.POST.get('licence_num')

        tbl_register.objects.all().filter(id=salesman_id).update(name=name, uname=uname, email=email, pswd=pswd, adrs=adrs, phn=phn, plc=plc) 
        success_message = f"Salesman {name} updated successfully. Email: {email}, Password: {pswd}"
        return render(request, 'admin/admin_edit_salesman.html', {'success_message': success_message,'salesman': salesman})
    else:
        # Pass the existing product data to the HTML template for pre-filling the form
        return render(request, 'admin/admin_edit_salesman.html', {'salesman': salesman})

def admin_view_customers(request):
    customers = tbl_register.objects.all().filter(utype="user")
    # Number of customers to display per page
    items_per_page = 10
    # Get the current page number from the request's GET parameters
    page = request.GET.get('page', 1)
    # Create a Paginator instance
    paginator = Paginator(customers, items_per_page)
    try:
        # Get the customers for the current page
        users = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, display the first page
        users = paginator.page(1)
    except EmptyPage:
        # If the page is out of range, deliver the last page of results
        users = paginator.page(paginator.num_pages)
    return render(request, 'admin/admin_view_customers.html', {'users': users})

def admin_view_online_salesman(request):
    salesmen_list = tbl_register.objects.filter(utype='salesman', status='online')

    # Set the number of items per page
    items_per_page = 10  # Adjust this value as needed

    # Create a Paginator instance
    paginator = Paginator(salesmen_list, items_per_page)

    # Get the current page number from the request's GET parameters
    page = request.GET.get('page')

    try:
        # Get the requested page
        salesmen = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, set it to the first page
        salesmen = paginator.page(1)
    except EmptyPage:
        # If the page is out of range, deliver the last page of results
        salesmen = paginator.page(paginator.num_pages)

    return render(request, 'admin/admin_view_online_salesman.html', {'salesmen': salesmen})

def admin_view_user_requests(request):
    # Retrieve all user requests ordered by the timestamp in descending order
    all_user_requests = tbl_request_salesman.objects.filter(status="pending").order_by('-timestamp')
    # Pass the user requests to the template
    context = {
        'all_user_requests': all_user_requests,
    }
    # Render the admin template with all user requests
    return render(request, 'admin/admin_view_user_request.html', context)

from django.core.exceptions import MultipleObjectsReturned
from django.shortcuts import render
from django.contrib import messages
from django.core.mail import send_mail
from .models import tbl_register, tbl_request_salesman, user_notification, salesman_notification

def admin_allocate_user_requests(request):
    all_user_requests = tbl_request_salesman.objects.filter(status="pending").order_by('-timestamp')
    all_online_salesmen = tbl_register.objects.filter(utype="salesman", status="online")
    context = {'all_user_requests': all_user_requests}
    allocated_salesmen_dict = {}

    if all_user_requests and all_online_salesmen:
        for user_request in all_user_requests:
            available_salesmen = [s for s in all_online_salesmen if s.id not in allocated_salesmen_dict.values()]

            if not available_salesmen:
                # Notify user about unavailability
                notify_no_salesman(user_request.user_id)
                messages.warning(request, 'No salesman available at the moment. Please wait for a few minutes.')
                continue

            # Allocate first available salesman
            allocated_salesman = available_salesmen[0]
            user_request.salesman = allocated_salesman
            user_request.status = "allocated"
            user_request.save()

            allocated_salesman.status = "busy"
            allocated_salesman.save()

            # Track allocation
            allocated_salesmen_dict[user_request.user_id] = allocated_salesman.id

            # ✅ Notification to user
            user_msg = f'Your request has been allocated to Salesman {allocated_salesman.name}. Contact: {allocated_salesman.phn}. Email: {allocated_salesman.email}'
            user_notification.objects.update_or_create(
                user_id=user_request.user.id,
                defaults={
                    'salesman_id': allocated_salesman.id,
                    'message': user_msg
                }
            )

            # ✅ Notification to salesman
            salesman_msg = f'You have been allocated a new request from user {user_request.user.name}. Contact: {user_request.user.phn}'
            salesman_notification.objects.create(
                user_id=user_request.user.id,
                salesman_id=allocated_salesman.id,
                message=salesman_msg
            )

            # ✅ Email to salesman
            send_mail(
                subject=f'New Allocated Request - User: {user_request.user.name}',
                message=f'{salesman_msg}\nDate & Time: {user_request.timestamp}',
                from_email='projecteshop99@gmail.com',
                recipient_list=[allocated_salesman.email]
            )

            # ✅ Email to user
            send_mail(
                subject=f'Your Request Has Been Allocated - Salesman: {allocated_salesman.name}',
                message=user_msg,
                from_email='projecteshop99@gmail.com',
                recipient_list=[user_request.user.email]
            )

            messages.success(request, f'Salesman {allocated_salesman.name} allocated to user {user_request.user.name}')

        return render(request, 'admin/admin_view_user_request.html', context)

    # If no requests or salesmen
    messages.warning(request, 'No user requests found or no online salesmen available.')
    for user_request in all_user_requests:
        notify_no_salesman(user_request.user_id)

    return render(request, 'admin/admin_view_user_request.html', context)

# Helper function to handle no salesman available notifications
def notify_no_salesman(user_id):
    try:
        user_notification.objects.update_or_create(
            user_id=user_id,
            defaults={'message': 'No salesman available at the moment. Please wait for a few minutes.'}
        )
    except MultipleObjectsReturned:
        existing = user_notification.objects.filter(user_id=user_id).first()
        existing.message = 'No salesman available at the moment. Please wait for a few minutes.'
        existing.save()

def admin_view_allocation(request):
    # Retrieve all allocated user requests
    allocated_requests = tbl_request_salesman.objects.filter(status="allocated").order_by('-timestamp')

    # Paginate the allocated requests
    paginator = Paginator(allocated_requests, 5)  # Show 5 allocated requests per page

    # Get the current page number from the request's GET parameters
    page = request.GET.get('page')

    try:
        # Get the allocated requests for the current page
        allocated_requests_page = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, show the first page
        allocated_requests_page = paginator.page(1)
    except EmptyPage:
        # If the page is out of range (e.g., 9999), deliver the last page of results
        allocated_requests_page = paginator.page(paginator.num_pages)

    # Pass the allocated requests to the template
    context = {'allocated_requests': allocated_requests_page}

    # Render the admin template with allocated requests
    return render(request, 'admin/admin_view_allocation.html', context)










# <--------------------------------salesman--------------------------->
def salesman_home(request):
    return render(request,'salesman/salesman_home.html')

def salesman_view_profile(request):
    id=request.session['id']
    salesman_profile = tbl_register.objects.get(id=id)
    context = {'salesman_profile': salesman_profile}
    return render(request, 'salesman/salesman_view_profile.html', context)

def salesman_view_feedback_ratings(request):
    salesman_id = request.session['id']
    # Get the salesman object or return a 404 response if not found
    salesman = get_object_or_404(tbl_register, id=salesman_id)
    # Retrieve all feedback instances for the current salesman and order them by datetime
    feedback_instances = tbl_feedback_rating.objects.filter(salesman=salesman).order_by('-date')
    return render(request, 'salesman/salesman_view_feedback_ratings.html', {'salesman': salesman, 'feedback_instances': feedback_instances})

def salesman_view_notification(request):
    salesman_id = request.session.get('id')
    
    if salesman_id is not None:
        salesman_notifications = salesman_notification.objects.filter(salesman_id=salesman_id).order_by('-timestamp')
        salesman_requests = tbl_request_salesman.objects.filter(salesman_id=salesman_id)

        return render(request, 'salesman/salesman_view_notification.html', {'salesman_notifications': salesman_notifications, 'salesman_requests': salesman_requests})
    else:
        # Handle the case when salesman ID is not in the session
        return HttpResponse("Salesman ID not found in the session.")
from django.http import JsonResponse

def toggle_status(request):
    if request.method == 'POST':
        user_profile = request.user.userprofile  # Assuming you have a one-to-one relationship with User
        user_profile.is_online = not user_profile.is_online
        user_profile.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

def salesman_update_status(request):
    salesman_id = request.session.get('id')

    if not salesman_id:
        return redirect('/')  # Redirect to login or home if not logged in

    salesman = tbl_register.objects.get(id=salesman_id)

    if request.method == 'POST':
        # Toggle between 'online' and 'busy'
        if salesman.status == 'online':
            salesman.status = 'busy'
        else:
            salesman.status = 'online'
        salesman.save()

    return render(request, 'salesman/salesman_update_status.html', {'user': salesman})

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import tbl_register, tbl_wishlist

def salesman_view_wishlist(request, user_id):
    salesman_id = request.session.get('id')

    if salesman_id:
        salesman = get_object_or_404(tbl_register, id=salesman_id)
        user = get_object_or_404(tbl_register, id=user_id)
        wishlist_items = tbl_wishlist.objects.filter(user=user).select_related('products')
        print(f"Wishlist items for user {user_id}: {wishlist_items}")

        return render(request, 'salesman/salesman_view_wishlist.html', {
            'salesman': salesman,
            'user': user,
            'wishlist_items': wishlist_items
        })
    else:
        return HttpResponse("Salesman ID not found in the session.")



















def qr_code_scanner(request):
    return render(request, 'qr_code_scanner.html')


















def logout(request):
    if 'id' in request.session:
        del request.session['id']
        logout(request)
    return render(request,'index.html')

