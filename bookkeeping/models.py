from django.db import models

# Create your models here.
from django.db import models
from pos.models import PosOrder

class BkLedger(models.Model):
    order = models.ForeignKey(PosOrder, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f"Ledger entry {self.id} - Rs. {self.amount}"