from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Cake)
class CakeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "veg_nonveg", "price")
    search_fields = ("name", "category")
    list_filter = ("category", "veg_nonveg")

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "cake", "quantity", "added_at")
    search_fields = ("user__username", "cake__name")
    list_filter = ("added_at",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_amount", "status", "created_at")
    search_fields = ("user__username", "address")
    list_filter = ("status", "created_at")

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "cake", "quantity", "price")
