
# Create your models here.
# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now, timedelta

class EmailOTP2(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return now() < self.created_at + timedelta(minutes=5)  # 5 min expiry

class Cake(models.Model):
    name = models.CharField(max_length=1000)
    description = models.TextField(max_length=2000, blank=True)
    category = models.CharField(max_length=1000)
    veg_nonveg = models.CharField(max_length=10, choices=[
        ('veg', 'Vegetarian'),
        ('nonveg', 'Non-Vegetarian'),
    ])
    price = models.DecimalField(max_digits=8, decimal_places=2)
    cake_image = models.ImageField(upload_to='cakes/', blank=True, null=True)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def item_total(self):
        """Calculates the total price for this cart line item."""
        # This handles the multiplication: price * quantity
        return self.cake.price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = (
        ('Unpaid', 'Unpaid (COD)'),
        ('Paid', 'Paid (COD/Online)'),
        ('Failed', 'Payment Failed'),
        ('Refunded', 'Refunded'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200, default="")
    address = models.TextField()
    city = models.CharField(max_length=100, default="")
    zipcode = models.CharField(max_length=20, default="")
    phone = models.CharField(max_length=20, default="")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    # cake = models.ForeignKey(Cake, on_delete=models.CASCADE, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='Unpaid'
    )
    def __str__(self):
        return f"Order {self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items' # <--- ADD/UPDATE THIS LINE
    ) 
    cake = models.ForeignKey(Cake, on_delete=models.CASCADE)  # your cake model
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_item_total(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.cake.name} x {self.quantity}"
