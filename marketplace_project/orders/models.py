from django.db import models
from django.conf import settings
from products.models import Product


from django.db import models
from django.conf import settings


class Order(models.Model):
    STATUS_CHOICES = (
        ('new', 'Нове'),
        ('paid', 'Оплачене'),
        ('shipped', 'Відправлене'),
        ('delivered', 'Доставлене'),
    )

    DELIVERY_CHOICES = (
        ('nova_poshta', 'Нова Пошта'),
        ('ukr_poshta', 'Укрпошта'),
        ('courier', 'Кур’єр'),
    )

    PAYMENT_CHOICES = (
        ('card', 'Оплата карткою'),
        ('cod', 'Накладений платіж'),
        ('bank', 'Банківський переказ'),
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

    # 🔹 Дані отримувача / доставки
    full_name = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    delivery_method = models.CharField(
        max_length=20,
        choices=DELIVERY_CHOICES,
        default='nova_poshta',
        blank=True,
        null=True,
    )
    delivery_department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Відділення Нової Пошти / Укрпошти"
    )

    comment = models.TextField(blank=True)

    # 🔹 Оплата
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default='card',
        blank=True,
        null=True,
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return f'Order #{self.pk} by {self.buyer.username}'


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
