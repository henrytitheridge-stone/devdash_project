from django.shortcuts import render, redirect, reverse
from .forms import OrderForm


# Create your views here.
def checkout(request):

    basket = request.session.get('basket', {})

    if not basket:
        return redirect(reverse('services'))

    order_form = OrderForm()
    template = 'checkout/checkout.html'
    context = {
            'order_form': order_form,
            }

    return render(request, template, context)
