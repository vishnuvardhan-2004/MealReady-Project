from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Cart, CartItem, User, Restaurant, Item
import razorpay
import json
from django.conf import settings
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def index(request):
    return render(request, 'index.html')

# Open Signup Page
def open_signup(request):
    return render(request, "signup.html")

# Open Signin Page
def open_signin(request):
    return render(request, "signin.html")

# Signup
def signup(request):
    
    if request.method == 'POST':
        name = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')

        # Duplicate emails Checking
        if User.objects.filter(email = email).exists():
            return HttpResponse("This email is already registered. Please try with another email.")
        
        # Duplicate usernames Checking
        if User.objects.filter(username = username).exists():
            return HttpResponse("This username is already registered. Please try with another username.")

        user = User(name = name, username = username, email = email, password = password, mobile = mobile, address = address)
        user.save()
        return render(request, 'signin.html')
    
    else:
        return render(request, 'signup.html')

# Signin
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            User.objects.get(username=username, password=password)

            if username == 'admin':
                return render(request, 'admin_home.html')
            else:
                return redirect('customer_home', username=username)

        except User.DoesNotExist:
            return render(request, 'fail.html')

    return render(request, 'signin.html')

# Customers's Home Page
def customer_home(request, username):
    query = request.GET.get('q')

    if query:
        restaurantList = Restaurant.objects.filter(
            name__icontains=query
        )
    else:
        restaurantList = Restaurant.objects.all()

    return render(request, 'customer_home.html', {
        'restaurantList': restaurantList,
        'username': username
    })

# Open Add Restaurant Page
def open_add_restaurant(request):
    return render(request, 'add_restaurant.html')


def add_restaurant(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')
        location = request.POST.get('location')
        mobile = request.POST.get('mobile')

        if not name or not picture or not cuisine or not rating or not location or not mobile:
            return render(request, 'add_restaurant.html', {
                'error': 'Please fill all details.'
            })

        if Restaurant.objects.filter(name=name).exists():
            return render(request, 'add_restaurant.html', {
                'error': 'Restaurant name already exists.'
            })

        if Restaurant.objects.filter(mobile=mobile).exists():
            return render(request, 'add_restaurant.html', {
                'error': 'Mobile number already exists.'
            })

        if len(str(mobile)) != 10:
            return render(request, 'add_restaurant.html', {
                'error': 'Mobile number must contain 10 digits.'
            })

        Restaurant.objects.create(
            name=name,
            picture=picture,
            cuisine=cuisine,
            rating=rating,
            location=location,
            mobile=mobile,
        )
        return render(request, 'add_restaurant.html', {
            'success': True
        })
    return render(request, 'add_restaurant.html')

# Open Show Restaurant Page
def open_show_restaurant(request):
    query = request.GET.get('q', '')

    if query:
        restaurantList = Restaurant.objects.filter(
            name__icontains=query
        )
    else:
        restaurantList = Restaurant.objects.all()

    return render(request, 'show_restaurant.html', {
        "restaurantList": restaurantList,
        "query": query
    })

# Open Update Restaurant Page
def open_update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    
    return render(request, 'update_restaurant.html', {"restaurant": restaurant})

# Update Restaurant Info
def update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')
        location = request.POST.get('location')
        mobile = request.POST.get('mobile')
        
        restaurant.name = name
        restaurant.picture = picture
        restaurant.cuisine = cuisine
        restaurant.rating = rating
        restaurant.location = location
        restaurant.mobile = mobile
        restaurant.save()
        
    restaurantList = Restaurant.objects.all()
    return render(request, 'show_restaurant.html', {"restaurantList": restaurantList})

# Delete Restaurant Info
def delete_restaurant(request, restaurant_id):
    if request.method == "POST":
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        restaurant.delete()
    return redirect('open_show_restaurant')

# Open Update Menu Page
def open_update_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    query = request.GET.get('q', '')

    if query:
        itemList = restaurant.items.filter(
            name__icontains=query
        )
    else:
        itemList = restaurant.items.all()

    return render(request, 'update_menu.html', {
        "restaurant": restaurant,
        "itemList": itemList,
        "query": query
    })

# Update Menu
def update_menu(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price')
        picture = request.POST.get('picture')

        vegetarian = 'vegetarian' in request.POST
        non_vegetarian = 'non_vegetarian' in request.POST
        soup = 'soup' in request.POST
        other = 'other' in request.POST

        # Basic validation
        if not name or not price:
            messages.error(request, "Item name and price are required.")
            return redirect('open_update_menu', restaurant_id=restaurant.id)

        # Duplicate check (restaurant-wise)
        if Item.objects.filter(
            name__iexact=name,
            restaurant=restaurant
        ).exists():
            messages.error(request, "This item already exists in the menu.")
            return redirect('open_update_menu', restaurant_id=restaurant.id)

        Item.objects.create(
            restaurant=restaurant,
            name=name,
            description=description,
            price=float(price),
            vegetarian=vegetarian,
            non_vegetarian=non_vegetarian,
            soup=soup,
            other=other,
            picture=picture,
        )

        messages.success(request, "Menu item added successfully.")

    return redirect('open_update_menu', restaurant_id=restaurant.id)

# Removing item from menu list
def delete_menu_item(request, item_id, restaurant_id):
    item = get_object_or_404(Item, id=item_id, restaurant_id=restaurant_id)
    item.delete()
    return redirect('open_update_menu', restaurant_id=restaurant_id)

# View Menu Page
def view_menu(request, restaurant_id, username):
    restaurant = get_object_or_404(Restaurant, id = restaurant_id)
    query = request.GET.get('q')
    if query:
        itemList = restaurant.items.filter(
            name__icontains=query
        )
    else:
        itemList = restaurant.items.all()

    return render(request, 'customer_menu.html', {
        'itemList': itemList,
        'restaurant': restaurant,
        'username': username
    })

# Add to cart
@require_POST
def add_to_cart(request, item_id, username):
    customer = get_object_or_404(User, username=username)
    item = get_object_or_404(Item, id=item_id)

    quantity = int(request.POST.get('quantity', 1))

    cart, _ = Cart.objects.get_or_create(customer=customer)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        item=item
    )

    if created:
        cart_item.quantity = quantity
    else:
        cart_item.quantity += quantity

    cart_item.save()

    return redirect(
        'view_menu',
        restaurant_id=item.restaurant.id,
        username=username
    )

# Show Cart
def show_cart(request, username):
    customer = get_object_or_404(User, username=username)
    cart = Cart.objects.filter(customer=customer).first()

    cart_items = cart.cart_items.all() if cart else []
    total_price = cart.total_price() if cart else 0

    return render(
        request,
        'cart.html',
        {
            "cart_items": cart_items,
            "total_price": total_price,
            "username": username
        }
    )

# Removing cart Items
def remove_from_cart(request, item_id, username):
    customer = get_object_or_404(User, username=username)
    cart = get_object_or_404(Cart, customer=customer)

    CartItem.objects.filter(
        cart=cart,
        item_id=item_id
    ).delete()

    return redirect('show_cart', username=username)

# Checkout page
def checkout(request, username):
    customer = get_object_or_404(User, username=username)
    cart = Cart.objects.filter(customer=customer).first()

    cart_items = cart.cart_items.all() if cart else []
    total_price = cart.total_price() if cart else 0

    if total_price == 0:
        return render(request, 'checkout.html', {
            'username': username,
            'error': 'Your cart is empty!',
        })

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    order_data = {
        'amount': int(total_price * 100),  # paisa
        'currency': 'INR',
        'payment_capture': '1',
    }

    order = client.order.create(data=order_data)

    return render(request, 'checkout.html', {
        'username': username,
        'cart_items': cart_items,
        'total_price': total_price,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order_id': order['id'],
        'amount': total_price,
    })

# Address Saving
@csrf_exempt
def save_address(request):
    if request.method == "POST":
        data = json.loads(request.body)
        request.session['delivery_address'] = data.get('address')
        return HttpResponse("OK")

# Orders Page
def orders(request, username):
    customer = get_object_or_404(User, username=username)
    cart = Cart.objects.filter(customer=customer).first()

    cart_items = cart.cart_items.all() if cart else []
    total_price = cart.total_price() if cart else 0

    delivery_address = request.session.get('delivery_address')

    if cart:
        cart.cart_items.all().delete()

    return render(request, 'orders.html', {
        'username': username,
        'customer': customer,
        'cart_items': cart_items,
        'total_price': total_price,
        'delivery_address': delivery_address,
    })