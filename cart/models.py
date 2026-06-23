from django.db import models
from django.conf import settings
from decimal import Decimal


class Cart(models.Model):
    """
    Supports both guest (session-based) and authenticated carts.
    When a guest logs in, their session cart merges into their user cart.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name='cart',
        on_delete=models.CASCADE
    )

    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        unique=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Discount settings
    DISCOUNT_THRESHOLD = Decimal("500000.00")
    DISCOUNT_RATE = Decimal("0.10")

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        if self.user:
            return f"Cart — {self.user.email}"
        return f"Guest Cart — {self.session_key}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        total = sum(
            (item.total_price for item in self.items.all()),
            Decimal("0.00")
        )
        return total.quantize(Decimal("0.01"))

    @property
    def qualifies_for_discount(self):
        return self.subtotal >= self.DISCOUNT_THRESHOLD

    @property
    def discount_amount(self):
        """
        10% discount if order is above 150,000 DZD
        """
        if self.qualifies_for_discount:
            return (
                self.subtotal * self.DISCOUNT_RATE
            ).quantize(Decimal("0.01"))

        return Decimal("0.00")

    @property
    def total(self):
        return (
            self.subtotal - self.discount_amount
        ).quantize(Decimal("0.01"))

    def merge_with(self, guest_cart):
        """
        Merge guest cart into authenticated cart.
        """
        for guest_item in guest_cart.items.all():
            existing = self.items.filter(
                product=guest_item.product
            ).first()

            if existing:
                existing.quantity += guest_item.quantity
                existing.save()
            else:
                guest_item.cart = self
                guest_item.save()

        guest_cart.delete()

    def clear(self):
        self.items.all().delete()


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        related_name='items',
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def unit_price(self):
        return self.product.price

    @property
    def total_price(self):
        return (
            self.unit_price * self.quantity
        ).quantize(Decimal("0.01"))

    def increase_quantity(self, amount=1):
        self.quantity += amount
        self.save()

    def decrease_quantity(self, amount=1):
        self.quantity = max(1, self.quantity - amount)
        self.save()