from django.db import models
from django.conf import settings
from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = (
        ('new', 'Нове'),
        ('paid', 'Оплачене'),
        ('shipped', 'Відправлене'),
        ('delivered', 'Доставлене'),
    )

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='new'
    )

    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f'Order #{self.pk} by {self.buyer.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.product.title} x {self.quantity}'
