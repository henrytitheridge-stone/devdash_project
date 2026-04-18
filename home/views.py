from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import SubscriberForm, EnquiryForm


# Create your views here.
def index(request):
    """ A view to return the index page """

    return render(request, 'home/index.html')


def newsletter_signup(request):
    """ Handle newsletter subscriptions """
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully subscribed!')
        else:
            messages.error(request, 'Could not subscribe. Please check your email.')

    return redirect(request.META.get('HTTP_REFERER', 'home'))

def contact(request):
    """ View for enquiry form """
    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Enquiry sent! We will be in touch soon.')
            return redirect(reverse('home'))

    form = EnquiryForm()
    return render(request, 'home/contact.html', {'form': form})
