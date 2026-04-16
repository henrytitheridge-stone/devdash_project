from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from services.models import Service
from basket.contexts import basket_contents

import stripe


# Create your views here.
def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        basket = request.session.get('basket', {})

        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
        }

        order_form = OrderForm(form_data)

        if order_form.is_valid():
            order = order_form.save()

            for item_id in basket.keys():
                service = Service.objects.get(id=item_id)
                order_line_item = OrderLineItem(
                    order=order,
                    service=service,
                )
                order_line_item.save()

            order.update_total()

            if 'basket' in request.session:
                del request.session['basket']

            return redirect(reverse('checkout_success', args=[order.order_number]))

    else:
        basket = request.session.get('basket', {})
        if not basket:
            return redirect(reverse('services'))

    current_basket = basket_contents(request)
    total = current_basket['grand_total']
    stripe_total = round(total * 100)
    stripe.api_key = stripe_secret_key

    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )

    order_form = OrderForm()

    template = 'checkout/checkout.html'
    context = {
            'order_form': order_form,
            'stripe_public_key': stripe_public_key,
            'client_secret': intent.client_secret,
            }

    return render(request, template, context)


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    order = get_object_or_404(Order, order_number=order_number)

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }
    return render(request, template, context)
