from django.shortcuts import render, redirect, HttpResponse


# Create your views here.
def add_to_basket(request, item_id):

    redirect_url = request.POST.get('redirect_url')
    basket = request.session.get('basket', {})

    basket[item_id] = 1

    request.session['basket'] = basket
    return redirect(redirect_url)


def view_basket(request):

    return render(request, 'basket/basket.html')


def remove_from_basket(request, item_id):

    try:

        basket = request.session.get('basket', {})
        basket.pop(item_id)
        request.session['basket'] = basket

        return HttpResponse(status=200)

    except Exception as e:
        return HttpResponse(status=500)
