from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from .models import Order, OrderLineItem
from services.models import Service

import json
import time
import stripe


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        """
        Send the user a confirmation email
        """
        cust_email = order.email
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order})
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email]
        )

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """

        intent = event.data.object
        pid = intent.id
        basket = intent.metadata.basket

        # Retrieve the charge object to get billing details
        stripe_charge = stripe.Charge.retrieve(
            intent.latest_charge
        )
        billing_details = stripe_charge.billing_details
        grand_total = round(stripe_charge.amount / 100, 2)

        phone = billing_details.phone if billing_details.phone else ''

        # Check if the order was already created by the view
        order_exists = False
        attempt = 1

        # The while loop allows for a delay in case the view is slow to save
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    # full_name__iexact=billing_details.name,
                    # email__iexact=billing_details.email,
                    # phone_number__iexact=phone,
                    # grand_total=grand_total,
                    # original_basket=basket,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)

        if order_exists:
            # If the view has handled and recorded the order, send confirmation email
            # and return success to Stripe
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200)
        else:
            # If the order doesn't exist after 5 attempts, create it here from metadata
            order = None
            try:
                order = Order.objects.create(
                    full_name=billing_details.name,
                    email=billing_details.email,
                    phone_number=phone,
                    grand_total=grand_total,
                    original_basket=basket,
                    stripe_pid=pid,
                )

                # Reconstruct the order items from the JSON metadata
                for item_id, item_data in json.loads(basket).items():
                    # Convert string keys to integers
                    service = Service.objects.get(id=int(item_id))
                    order_line_item = OrderLineItem(
                            order=order,
                            service=service,
                    )
                    order_line_item.save()
                order.update_total()

            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(
                    content=f'Webhook received: {event["type"]} | ERROR: {e}',
                    status=500)
        # If the webhook had to build the order itself, send confirmation email here
        self._send_confirmation_email(order)
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
