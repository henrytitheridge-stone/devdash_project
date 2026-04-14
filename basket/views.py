from django.shortcuts import render, redirect


# Create your views here.
def add_to_basket(request, item_id):

    redirect_url = request.POST.get('redirect_url')
    basket = request.session.get('basket', {})

    basket[item_id] = 1

    request.session['basket'] = basket
    return redirect(redirect_url)
