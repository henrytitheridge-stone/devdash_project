from django.contrib import admin
from .models import Subscriber, Enquiry


# Register your models here.
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_subscribed',)
    ordering = ('-date_subscribed',)

class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'date_sent',)
    ordering = ('-date_sent',)

admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(Enquiry, EnquiryAdmin)
