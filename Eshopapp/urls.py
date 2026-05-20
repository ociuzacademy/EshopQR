from django.contrib import admin
from django.urls import path,include
from.import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.index),
    path('user_register/',views.user_register),
    # path('shop_register/',views.shop_register),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('about/',views.about),
    path('contact/',views.contact),
    path('category/',views.category),
    path('user_home/',views.user_home,name='user_home'),
    path('all_view_category/',views.all_view_category),
    path('all_view_qr/',views.all_view_qr,name='all_view_qr'),
    path('all_view_products/<int:id>/',views.all_view_products,name="all_view_products"),
    path('all_view_productdetails/<int:id>/',views.all_view_productdetails,name="all_view_productdetails"),
    path('qr_code_scanner/', views.qr_code_scanner, name='qr_code_scanner'),
    path('contact/', views.contact, name='contact'),
    # path('shop_home/',views.shop_home),
    
    
    path('user_view_category/',views.user_view_category),
    path('user_view_products/<int:id>/',views.user_view_products,name="user_view_products"),
    path('user_view_product/<int:id>/',views.user_view_products,name="user_view_products"),
    path('user_view_productdetails/<int:id>/',views.user_view_productdetails,name="user_view_productdetails"),
    path('user_view_salesman/',views.user_view_salesman),
    path('user_request_salesman/',views.user_request_salesman),
    path('user_add_salesman_rating/<int:id>/',views.user_add_salesman_rating),
    path('user_add_product_rating/<int:product_id>/', views.user_add_product_rating, name='user_add_product_rating'),
    path('view_wishlist/', views.view_wishlist, name='view_wishlist'),
    path('add_to_wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('user_view_notification/',views.user_view_notification),
    
    
    path('admin_home/',views.admin_home,name='admin_home'),
    path('admin_add_category/',views.admin_add_category),
    path('admin_view_category/',views.admin_view_category),
    path('admin_edit_category/<int:id>/',views.admin_edit_category),
    path('admin_delete_category/<int:id>/',views.admin_delete_category),
    path('admin_view_products/<int:id>/',views.admin_view_products,name='admin_view_products'),
    path('admin_add_products/<int:id>/',views.admin_add_products),
    path('admin_edit_product/<int:id>/',views.admin_edit_product),
    path('admin_delete_product/<int:id>/',views.admin_delete_product),
    path('admin_view_salesman/',views.admin_view_salesman),
    path('admin_view_salesman_ratings/',views.admin_view_salesman_ratings),
    path('admin_view_salesman_feedbacks/<int:salesman_id>/',views.admin_view_salesman_feedbacks),
    path('admin_add_salesman/',views.admin_add_salesman),
    path('admin_edit_salesman/<int:salesman_id>/',views.admin_edit_salesman),
    path('admin_delete_salesman/<int:salesman_id>/',views.admin_delete_salesman),
    path('admin_view_customers/',views.admin_view_customers),
    path('admin_view_user_requests/', views.admin_view_user_requests, name='admin_view_user_requests'),
    path('admin_allocate_user_requests/', views.admin_allocate_user_requests, name='admin_allocate_user_requests'),
    path('admin_view_allocation/',views.admin_view_allocation),
    
    
    
    path('admin_view_online_salesman/',views.admin_view_online_salesman),
    path('salesman_home/',views.salesman_home),
    path('salesman_view_profile/',views.salesman_view_profile),
    path('salesman_view_feedback_ratings/',views.salesman_view_feedback_ratings),
    path('salesman_update_status/',views.salesman_update_status,name='salesman_update_status'),
    path('toggle_status/',views.toggle_status),
    path('salesman_view_notification/',views.salesman_view_notification),
    # path('salesman_view_wishlist/<int:user_id>/',views.salesman_view_wishlist),
    path('salesman_view_wishlist/<int:user_id>/', views.salesman_view_wishlist, name='salesman_view_wishlist'),

    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)