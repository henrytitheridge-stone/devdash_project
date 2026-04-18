from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from checkout.webhook_handler import StripeWH_Handler

import stripe


@require_POST
@csrf_exempt
def webhook(request):
    """
    Listen for webhooks from Stripe and dispatch them to the correct handler.
    Exempt from CSRF as the request comes from Stripe, not a user.
    """
    # Setup Stripe keys and variables from environment variables
    wh_secret = settings.STRIPE_WH_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get the webhook data and verify its signature
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        # Verify that the request came from Stripe
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WH_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)

    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    except Exception as e:
        # FOr any other errors during construction
        return HttpResponse(content=e, status=400)

    # Initialise the webhook handler class
    handler = StripeWH_Handler(request)

    # Dictionary to map Stripe event types to correct handler methods
    event_map = {
        'payment_intent.succeeded': handler.handle_payment_intent_succeeded,
        'payment_intent.payment_failed': handler.handle_payment_intent_payment_failed,
    }

    # Identify event type, get mapped handler or default
    event_type = event['type']
    event_handler = event_map.get(event_type, handler.handle_event)

    # Call the handler and return the response
    response = event_handler(event)
    print('Success!')
    return response
