from django.shortcuts import get_object_or_404
from services.models import Service


def basket_contents(request):

    basket_items = []
    total = 0
    basket = request.session.get('basket', {})

    for item_id in basket.keys():
        service = get_object_or_404(Service, pk=item_id)
        total += service.price
        basket_items.append({
              'item_id': item_id,
              'service': service,
         })

    grand_total = total

    context = {
        'basket_items': basket_items,
        'total': total,
        'grand_total': grand_total,
    }

    return context
