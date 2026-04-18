from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import SubscriberForm, EnquiryForm
from .models import Subscriber


# Create your views here.
def index(request):
    """ A view to return the index page """

    return render(request, 'home/index.html')


def newsletter_signup(request):
    """ 
    Processes newsletter subscription requests. 
    Checks for existing subscribers to prevent duplicate entries.
    """
    if request.method == 'POST':
        email = request.POST.get('email')

        if Subscriber.objects.filter(email=email).exists():
            messages.info(request, 'You are already subscribed!')
            return redirect(request.META.get('HTTP_REFERER', 'home'))

        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully subscribed!')
        else:
            messages.error(request, 'Could not subscribe. Please check your email.')

    return redirect(request.META.get('HTTP_REFERER', 'home'))


def contact(request):
    """
    Handles user inquiries via the EnquiryForm.
    Saves data to the Enquiry model for admin review.
    """
    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Enquiry sent! We will be in touch soon.')
            return redirect(reverse('home'))

    form = EnquiryForm()
    return render(request, 'home/contact.html', {'form': form})
