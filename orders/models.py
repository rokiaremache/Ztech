from django.db import models
from django.conf import settings
import uuid


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',     'Pending'),
        ('paid',        'Paid'),
        ('processing',  'Processing'),
        ('shipped',     'Shipped'),
        ('delivered',   'Delivered'),
        ('cancelled',   'Cancelled'),
        ('refunded',    'Refunded'),
        ('failed',      'Failed'),
    ]

    reference            = models.CharField(max_length=20, unique=True, editable=False)
    user                 = models.ForeignKey(
                             settings.AUTH_USER_MODEL,
                             null=True, blank=True,
                             related_name='orders',
                             on_delete=models.SET_NULL
                           )
    full_name            = models.CharField(max_length=200)
    email                = models.EmailField()
    phone                = models.CharField(max_length=20)
    street               = models.CharField(max_length=300)
    city                 = models.CharField(max_length=100)
    wilaya               = models.CharField(max_length=100)
    postal_code          = models.CharField(max_length=10, blank=True)

    subtotal             = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount      = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total                = models.DecimalField(max_digits=12, decimal_places=2)

    status               = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    customer_notes       = models.TextField(blank=True)
    admin_notes          = models.TextField(blank=True)
    # Cancellation reason — required when admin cancels
    cancellation_reason  = models.TextField(blank=True)

    created_at           = models.DateTimeField(auto_now_add=True)
    updated_at           = models.DateTimeField(auto_now=True)
    paid_at              = models.DateTimeField(null=True, blank=True)
    shipped_at           = models.DateTimeField(null=True, blank=True)
    delivered_at         = models.DateTimeField(null=True, blank=True)
    cancelled_at         = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering            = ['-created_at']
        verbose_name        = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order #{self.reference}"

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = f"ZT-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    @property
    def is_paid(self):
        return self.status in ('paid', 'shipped', 'delivered', 'processing')

    @property
    def can_be_cancelled(self):
        return self.status in ('pending', 'paid', 'processing')

    @property
    def status_color(self):
        return {
            'pending':     'warning',
            'paid':        'success',
            'processing':  'info',
            'shipped':     'primary',
            'delivered':   'success',
            'cancelled':   'secondary',
            'refunded':    'secondary',
            'failed':      'danger',
        }.get(self.status, 'secondary')

    @property
    def tracking_steps(self):
        steps = [
            ('pending',    'Order Placed',      'cart-check'),
            ('paid',       'Payment Confirmed', 'credit-card'),
            ('processing', 'Being Prepared',    'box-seam'),
            ('shipped',    'Shipped',           'truck'),
            ('delivered',  'Delivered',         'house-check'),
        ]
        order_of = {s[0]: i for i, s in enumerate(steps)}
        current  = order_of.get(self.status, 0)
        return [
            {
                'key':    s[0],
                'label':  s[1],
                'icon':   s[2],
                'done':   order_of.get(s[0], 0) <= current,
                'active': s[0] == self.status,
            }
            for s in steps
        ]


class OrderItem(models.Model):
    order         = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product       = models.ForeignKey('products.Product', null=True, on_delete=models.SET_NULL)
    product_name  = models.CharField(max_length=300)
    product_image = models.CharField(max_length=500, blank=True)
    unit_price    = models.DecimalField(max_digits=12, decimal_places=2)
    quantity      = models.PositiveIntegerField()

    class Meta:
        verbose_name        = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"

    @property
    def total_price(self):
        return self.unit_price * self.quantity
