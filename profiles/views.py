from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import UserProfile
from .forms import UserProfileForm

from checkout.models import Order


# Create your views here.
@login_required
def profile(request):
    """
    Display the user's profile.
    Allows CRUD for contact info and lists past orders.
    """
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        # Update form
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Update failed. Please ensure the form is valid.')
    else:
        # Initialise form with existing profile data
        form = UserProfileForm(instance=profile)
    
    # Collect all orders linked to this profile
    orders = profile.orders.all()

    template = 'profiles/profile.html'
    context = {
        'form': form,
        'orders': orders,
        'profile': profile,
        # Hide mini-basket success toast on profile page
        'on_profile_page': True
    }

    return render(request, template, context)


def order_history(request, order_number):
    """
    Displays a past order confirmation to the user.
    Re-uses the checkout_success template to 
    verify the transaction details for the user.
    """
    order = get_object_or_404(Order, order_number=order_number)

    # Tell user they're seeing historical data, not a new purchase
    messages.info(request, (
        f'This is a past confirmation for order number {order_number}. '
        'A confirmation email was sent on the order date.'
    ))

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        # Came from profile order history
        'from_profile': True,
    }

    return render(request, template, context)
