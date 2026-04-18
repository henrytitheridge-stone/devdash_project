from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from services.models import Service


# Create your views here.
def add_to_basket(request, item_id):
    """
    Add a specific service to the shopping basket.
    Updates the session with the service ID.
    """
    service = Service.objects.get(pk=item_id)
    redirect_url = request.POST.get('redirect_url')

    # Retrieve basket if one exists in the session, otherwise create empty dictionary
    basket = request.session.get('basket', {})

    if item_id in list(basket.keys()):
        messages.info(request, f'{service.name} is already in your basket.')
    else:
        # Each audit quantity set to 1 as only 1 ever needed at a time
        basket[item_id] = 1
        messages.success(request, f'Added {service.name} to your basket.')

    request.session['basket'] = basket
    return redirect(redirect_url)


def view_basket(request):
    """
    A view that renders the basket contents page. 
    Allows users to see the services they intend to purchase before checkout.
    """
    return render(request, 'basket/basket.html')


def remove_from_basket(request, item_id):
    """
    Remove a service from the shopping basket.
    Updates the session to reflect the removal of the service ID.
    """
    try:
        basket = request.session.get('basket', {})

        # Remove item from dictionary using id
        basket.pop(item_id)

        # Overwrite session with updated basket
        request.session['basket'] = basket

        return HttpResponse(status=200)

    except Exception as e:
        # Return a server error if item cannot be found or removed 
        return HttpResponse(status=500)
