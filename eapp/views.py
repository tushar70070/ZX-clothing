import json
from math import ceil
from django.shortcuts import render
from eapp.models import Product
from eapp import keys
from django.http import JsonResponse
# Create your views here.
def home (request):
    current_user = request.user
    allProds = []
    catproduct = Product.objects.values('category','id')
    cats = {item['category'] for item in catproduct}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n=len(prod)
        nslides = n // 4 + ceil((n/4))-(n//4)
        allProds.append([prod,range(1,nslides),nslides])


    params = {'allProds':allProds}
    return render(request,'index.html',params)


def some_view(request):
    # Get the cart count, e.g., from a session or database
    cart_count = 0
    if request.user.is_authenticated:
        cart_count = request.session.get('cart_count', 0)
    return render(request, 'base.html', {'cart_count': cart_count})

def add_to_cart(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            data = json.loads(request.body)  # Parse JSON request body
            item_id = data.get('itemId')    # Get the item ID from the request

            if not item_id:
                return JsonResponse({'success': False, 'message': 'Invalid item ID'})

            # Get the cart from session or initialize it
            cart = request.session.get('cart', [])
            if item_id not in cart:
                cart.append(item_id)  # Add the item to the cart
                request.session['cart'] = cart  # Save back to session
                request.session['cart_count'] = len(cart)  # Update cart count
            return JsonResponse({'success': True, 'cart_count': len(cart)})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Unauthorized or invalid request'})
    
def mycart(request):
    if request.user.is_authenticated:
        cart = request.session.get('cart', [])  # Retrieve cart from session
        # Retrieve actual cart items from the database based on IDs (if necessary)
        return render(request, 'mycart.html', {'cart': cart})
    return render(request, 'mycart.html', {'cart': []})    