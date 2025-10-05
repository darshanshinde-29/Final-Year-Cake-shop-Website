from django.shortcuts import render , redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .utils import send_otp_email
from .models import *
from django.db.models import Q
from .forms import *  # import custom form
from django.contrib import messages
from django.template.loader import render_to_string
from django.http import HttpResponse
# from weasyprint import HTML
from django.conf import settings
from django.contrib.auth.decorators import login_required # Add this if not present
import os
# --- Explicitly register MSYS2/GTK directories for DLL loading ---
# NOTE: Use 'r' prefix for raw string to handle backslashes correctly
try:
    # Add the primary GTK/UCRT directory
    os.add_dll_directory(r'C:\msys64\ucrt64\bin')
    # Add the core MSYS2 runtime directory (often needed for transitive dependencies)
    os.add_dll_directory(r'C:\msys64\usr\bin') 
except AttributeError:
    # Fallback for older Python versions (not needed for 3.13, but good practice)
    pass
    


from io import BytesIO
from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
# from reportlab.lib import colors

# from io import BytesIO
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
# from reportlab.lib import colors
# from reportlab.lib.units import inch

# Import the PDF generation tool
from weasyprint import HTML, CSS

# Create your views here.

def home(req):
    if req.user.is_authenticated:


        categories = Cake.objects.values_list("category", flat=True).distinct()
        cakes_by_category = {}
        for category in categories:
            cakes_by_category[category] = Cake.objects.filter(category=category)
    
        return render(req, "landing_user.html", {"cakes_by_category": cakes_by_category})
        # return render(req, "landing_user.html")  # template for logged-in users
    else:
        return redirect('/')  # template for visitors

def cakebtn(req, id):
    
    cake = get_object_or_404(Cake, id=id)
    return render(req, "cakebtn.html", {'cake':cake})

def about(req):
    return render(req, "About.html")


def contact(req):
    return render(req, "Contact.html")


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect('login')  # redirect after register
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def add_to_cart(request, cake_id):
    cake = get_object_or_404(Cake, id=cake_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, cake=cake)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('view_cart')

def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.cake.price * item.quantity for item in cart_items)

    
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

def remove_from_cart(request, item_id):
    Cart.objects.filter(id=item_id, user=request.user).delete()
    return redirect('view_cart')


@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    cart_total = sum(item.quantity * item.cake.price for item in cart_items)

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Save order
            order = Order.objects.create(
                user=request.user,
                full_name=form.cleaned_data['full_name'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                zipcode=form.cleaned_data['zipcode'],
                phone=form.cleaned_data['phone'],
                total_amount=cart_total,
            )

            # Save items
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.cake,
                    quantity=item.quantity,
                    price=item.cake.price
                )

            # Clear cart
            cart_items.delete()

            # Payment method check
            if form.cleaned_data['payment_method'] == 'cod':
                messages.success(request, "Order placed successfully! Cash on Delivery selected.")
                return redirect("order_success", order_id=order.id)
            else:
                return redirect("start_payment", order_id=order.id)

    else:
        form = CheckoutForm()

    return render(request, "checkout.html", {
        "form": form,
        "cart_items": cart_items,
        "cart_total": cart_total
    })

def increase_quantity(request, item_id):
    item = Cart.objects.get(id=item_id, user=request.user)
    item.quantity += 1
    item.save()
    return redirect('view_cart')

def decrease_quantity(request, item_id):
    item = Cart.objects.get(id=item_id, user=request.user)
    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()
    return redirect('view_cart')


@login_required
def order_success(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return render(request, "order_success.html", {"order": order})


@login_required
def place_order(request):
    if request.method == "POST":
        # 1. Collect Shipping Details from the POST request
        name = request.POST.get("name")
        address = request.POST.get("address")
        city = request.POST.get("city")
        zipcode = request.POST.get("zipcode")
        phone = request.POST.get("phone")
        payment_method = request.POST.get("payment_method") # Not strictly needed for COD, but good practice

        # 2. Cart Validation and Total Calculation
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            messages.error(request, "Your cart is empty! Please add items before checking out.")
            return redirect("checkout")

        total = sum(item.cake.price * item.quantity for item in cart_items)

        # 3. Create the Main Order Object
        # Use separate fields to store shipping data for better structure
        order = Order.objects.create(
            user=request.user,
            full_name=name,              # <-- Saving to specific field
            address=address,             # <-- Saving to specific field
            city=city,                   # <-- Saving to specific field
            zipcode=zipcode,             # <-- Saving to specific field
            phone=phone,                 # <-- Saving to specific field
            total_amount=total,
            status="Pending",
            payment_status='Unpaid',     # <-- Set initial status for COD
        )

        # 4. Create OrderItem Objects (Line Items)
        for item in cart_items:
            # Create a separate OrderItem record for each cake in the cart
            OrderItem.objects.create(
                order=order,
                cake=item.cake,
                quantity=item.quantity,
                # Store the price at the time of order
                price=item.cake.price 
            )

        # 5. Clear the Cart
        # Only clear the cart after the order and all items have been successfully saved
        cart_items.delete()

        messages.success(request, f"Order #{order.id} placed successfully! 🎉 Payment is due upon delivery.")
        return redirect("order_summary", order_id=order.id)
        
    # If not a POST request, redirect back to checkout
    return redirect("checkout")
@login_required
def order_summary(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    return render(request, "order_summary.html", {"order": order})

@login_required
def generate_invoice_pdf(request, order_id):
    # 1. Fetch the Order and related items (using 'items' related_name)
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # 2. Render the HTML template with the order context
    html_content = render_to_string('invoice_template.html', {'order': order})

    # 3. Create the PDF object from the rendered HTML
    # WeasyPrint needs the base URL to find linked images/fonts, 
    # but since we embedded CSS, we can often skip or use a simple base.
    pdf_file = HTML(string=html_content).write_pdf()

    # 4. Prepare the HTTP response
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
    
    return response

@login_required
def order_tracker(request):
    # Fetch all orders for the logged-in user, newest first
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, "order_tracker.html", {"orders": orders})


@login_required
def cancel_order(request, order_id):
    # 1. Get the order or return 404 if not found or not owned by the user
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # 2. Check if the order can be cancelled (e.g., if status is 'Pending')
    # You might want to define a list of cancellable statuses in your settings/models.
    CANCELLABLE_STATUSES = ['Pending', 'Confirmed'] 

    if order.status in CANCELLABLE_STATUSES:
        # Change the order status to 'Cancelled'
        order.status = 'Cancelled'
        
        # If you add a payment_status field (see below), update it here:
        # order.payment_status = 'Refunded' or similar if payment was made, 
        # but for COD it's simply 'Cancelled'/'Not Applicable'.
        
        order.save()
        messages.success(request, f"Order #{order.id} has been successfully cancelled.")
    else:
        messages.error(request, f"Order #{order.id} cannot be cancelled as its status is '{order.status}'.")
    
    # 3. Redirect to the order summary or tracker page
    return redirect("order_summary", order_id=order.id)
    # Alternatively, redirect to the list view: return redirect("order_tracker")



# def your_search_view(req):
#     query = req.GET.get('q')

#     results = []

#     if query:
#         # Case-insensitive search across multiple fields
#         results = Cake.objects.filter(
#             Q(name__icontains=query) | Q(category__icontains=query)
#         )
#     return render(req, 'search_results.html', {'results': results, 'query': query})

def search_view(request):
    # Get the search query from the URL parameter 'q'
    query = request.GET.get('q')
    results = Cake.objects.none() # Start with an empty queryset
    
    if query:
        # Use Q objects to combine search lookups (case-insensitive contains: __icontains)
        results = Cake.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__icontains=query) # Search within the category's name field
        ).distinct()
        
    context = {
        'query': query,    # The search term itself, to display on the results page
        'results': results # The queryset of matching Cake objects
    }
    
    # Renders the search_results.html template
    return render(request, 'search_results.html', context)