from django.db import models

# Create your models here.
from django.db import models

class PosTable(models.Model):
    number = models.IntegerField(unique=True)
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return f"Table {self.number}"

class PosMenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('Coffee', 'Coffee'),
        ('Bakery', 'Bakery'),
        ('Food', 'Food'),
        ('Beverage', 'Beverage'),
    ]
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name

class PosOrder(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Cancelled', 'Cancelled'),
    ]
    PAYMENT_CHOICES = [
        ('Cash', 'Cash'),
        ('Fonepay', 'Fonepay'),
        ('Due', 'Due'),
    ]
    table = models.ForeignKey(PosTable, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - Table {self.table.number}"

class PosOrderItem(models.Model):
    order = models.ForeignKey(PosOrder, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(PosMenuItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.name}"