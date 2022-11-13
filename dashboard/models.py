from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
CATEGORY = (
    ('Stationary', 'Stationary'),
    ('Electronics', 'Electronics'),
    ('Food', 'Food'),
    ('cosmetics', 'cosmetics')
)


class Product(models.Model):
    name = models.CharField(max_length=100, null=True)
    quantity = models.PositiveIntegerField(null=True)
    category = models.CharField(max_length=50, choices=CATEGORY, null=True)
    mrp = models.FloatField(default=1000.0)

    def __str__(self):
        return f'{self.name}'


class Order(models.Model):
    name = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    order_quantity = models.PositiveIntegerField(null=True)
    delivered_quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def amount(self):
        return self.order_quantity * self.name.mrp

    def __str__(self):
        return f'{self.customer}-{self.name}'


class DeliveryLog(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

