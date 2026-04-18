from django.db import models


# Create your models here.
class Service(models.Model):
    """
    Represents individual audit services available to purchase
    """
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name
