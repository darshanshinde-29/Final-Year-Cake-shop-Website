from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # App
    path('home', views.home, name="home"),
    path('cakebtn/<int:id>', views.cakebtn, name="cakebtn"),
    path('addtocart/<int:cake_id>', views.add_to_cart, name="add_to_cart"),
    path('view_cart', views.view_cart, name="view_cart"),
    path('remove_from_cart/<int:item_id>', views.remove_from_cart, name="remove_from_cart"),
    path('checkout', views.checkout, name="checkout"),
    path('increase_quantity/<int:item_id>', views.increase_quantity, name="increase_quantity"),
    path('decrease_quantity/<int:item_id>', views.decrease_quantity, name="decrease_quantity"),
    path("order-success/<int:order_id>/", views.order_success, name="order_success"),
    path("place_order/", views.place_order, name="place_order"),
    path("order_summary/<int:order_id>", views.order_summary, name="order_summary"),
     path("order/<int:order_id>/invoice/pdf/", views.generate_invoice_pdf, name="generate_invoice_pdf"),
    path("order/track/", views.order_tracker, name="order_tracker"),
     path("order/<int:order_id>/cancel/", views.cancel_order, name="cancel_order"),
 

     # path("your_search_view", views.your_search_view, name="your_search_view"),
     path("search_view_name", views.search_view, name="search_view_name"),
#     path("start-payment/<int:order_id>/", views.start_payment, name="start_payment"),  # if online
    path('about', views.about, name="about" ),
    path('contact', views.contact, name="contact" ),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html",redirect_authenticated_user=True), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),


    path("password-reset/", 
         auth_views.PasswordResetView.as_view(template_name="password_reset.html"), 
         name="password_reset"),

    path("password-reset/done/", 
         auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"), 
         name="password_reset_done"),

    path("reset/<uidb64>/<token>/", 
         auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), 
         name="password_reset_confirm"),

    path("reset/done/", 
         auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"), 
         name="password_reset_complete"),
]

