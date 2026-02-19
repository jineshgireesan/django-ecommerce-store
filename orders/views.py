from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from cart.models import Cart
import uuid

def order_history(request):
    return HttpResponse("Order history page works!")

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    if not cart_items.exists():
        messages.error(request, 'Your cart is empty.')
        return redirect('cart_view')

    if request.method == 'POST':
        # Get form data
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        country = request.POST.get('country')
        postal_code = request.POST.get('postal_code')

        # Create order
        order = Order.objects.create(
            user=request.user,
            order_number=f"ORD{uuid.uuid4().hex[:8].upper()}",
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            country=country,
            postal_code=postal_code,
            total_amount=cart.get_total(),
            status='pending'
        )

        # Create order items from cart
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_price=cart_item.product.price,
                quantity=cart_item.quantity
            )
            # Reduce stock
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()

        # Clear cart
        cart.items.all().delete()

        messages.success(request, f'Order placed successfully! Order number: {order.order_number}')
        return redirect('order_detail', order_id=order.id)

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
    })


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})