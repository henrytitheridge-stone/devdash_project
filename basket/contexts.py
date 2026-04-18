from django.shortcuts import get_object_or_404
from services.models import Service


def basket_contents(request):
    """
    A context processor to make basket data available across the entire site.
    Calculates totals and item counts for the nav bar and success toasts.
    """
    basket_items = []
    total = 0
    service_count = 0
    basket = request.session.get('basket', {})

    for item_id in basket.keys():
        service = get_object_or_404(Service, pk=item_id)
        total += service.price
        service_count += 1
        basket_items.append({
              'item_id': item_id,
              'service': service,
         })

    grand_total = total

    context = {
        'basket_items': basket_items,
        'total': total,
        'grand_total': grand_total,
        'service_count': service_count,
    }

    return context
