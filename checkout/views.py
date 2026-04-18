from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from services.models import Service
from profiles.models import UserProfile
from basket.contexts import basket_contents

import stripe
import json


# Create your views here.
@require_POST
def cache_checkout_data(request):
    """
    Temporary storage of checkout data in the Stripe PaymentIntent.
    Allows for recovery of orders if the user's connection drops.
    """
    try:
        # Extract payment intent ID from client secret
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Add metadata to Stripe intent to make data save in webhooks
        stripe.PaymentIntent.modify(pid, metadata={
            'basket': json.dumps(request.session.get('basket', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user,
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be \
            processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)


def checkout(request):
    """
    Core view for processing payments.
    Handles form validation, Stripe intent creation, and order saving.
    """
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

            # Prevent multiple saves while adding data manually
            order = order_form.save(commit=False)
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_basket = json.dumps(basket)
            order.save()

            # Iterate through basket to create line items
            for item_id in basket.keys():
                service = Service.objects.get(id=item_id)
                order_line_item = OrderLineItem(
                    order=order,
                    service=service,
                )
                order_line_item.save()

            # Trigger calculation of the total in the model
            order.update_total()

            # Store the 'save info' preference to be handled in success view
            request.session['save_info'] = 'save-info' in request.POST

            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
            messages.error(request, 'There was an error with your form. \
                Please double check your information.')
    else:
        # Handle GET request
        basket = request.session.get('basket', {})
        if not basket:
            messages.error(request, "There's nothing in your basket at the moment")
            return redirect(reverse('services'))

        # Prep totals for Stripe in cents 
        current_basket = basket_contents(request)
        total = current_basket['grand_total']
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key

        # Create payment intent for JS
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

        # Pre-fill form with profile data for logged in users
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(initial={
                    'full_name': profile.user.get_full_name(),
                    'email': profile.user.email,
                    'phone_number': profile.default_phone_number,
                })
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
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
    Finalises the transaction.
    Links the order to the user's profile and clears the session basket.
    """
    order = get_object_or_404(Order, order_number=order_number)

    # Attach profile to order if user was logged in
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        order.user_profile = profile
        order.save()

    # Empty session basket once payment is confirmed
    if 'basket' in request.session:
        del request.session['basket']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }
    return render(request, template, context)
