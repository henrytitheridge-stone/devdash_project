from django.db import models


# Create your models here.
class Subscriber(models.Model):
    """
    A model to store email addresses for the site's newsletter.
    """
    email = models.EmailField(max_length=254, unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class Enquiry(models.Model):
    """
    A model to capture and store user messages from the Contact Us form.
    """
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Enquiries"

    def __str__(self):
        return f"Enquiry from {self.name}: {self.subject}"
