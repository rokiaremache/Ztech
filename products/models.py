from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Category(models.Model):
    GENDER_CHOICES = [('all','All'),('men','Men'),('women','Women')]
    name        = models.CharField(max_length=200)
    slug        = models.SlugField(max_length=200, unique=True, blank=True)
    parent      = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.SET_NULL)
    gender      = models.CharField(max_length=10, choices=GENDER_CHOICES, default='all')
    description = models.TextField(blank=True)
    image       = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Category'
        verbose_name_plural = 'Categories'
        ordering            = ['name']

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'slug': self.slug})

    def get_all_children(self):
        children = list(self.children.filter(is_active=True))
        for child in self.children.filter(is_active=True):
            children += child.get_all_children()
        return children


class Brand(models.Model):
    name      = models.CharField(max_length=100)
    slug      = models.SlugField(unique=True, blank=True)
    logo      = models.ImageField(upload_to='brands/', blank=True, null=True)
    website   = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    GENDER_CHOICES = [('all','All'),('men','Men'),('women','Women')]
    COMPONENT_TYPE_CHOICES = [
        ('', 'Not a build component'),
        ('cpu',         'CPU'),
        ('gpu',         'GPU'),
        ('ram',         'RAM'),
        ('storage',     'Storage'),
        ('motherboard', 'Motherboard'),
        ('psu',         'PSU'),
        ('case',        'Case'),
        ('cooler',      'CPU Cooler'),
        ('other',       'Other'),
    ]

    name             = models.CharField(max_length=300)
    slug             = models.SlugField(max_length=300, unique=True, blank=True)
    category         = models.ForeignKey(Category, related_name='products', on_delete=models.PROTECT)
    brand            = models.ForeignKey(Brand, related_name='products', on_delete=models.SET_NULL, null=True, blank=True)
    gender           = models.CharField(max_length=10, choices=GENDER_CHOICES, default='all')
    component_type   = models.CharField(max_length=20, choices=COMPONENT_TYPE_CHOICES, blank=True, default='', help_text="Used by the AI Builder / Calculator")
    socket           = models.CharField(max_length=50, blank=True, help_text="CPU socket (e.g. AM5, LGA1700) — fill for CPUs and Motherboards")
    ram_type         = models.CharField(max_length=20, blank=True, help_text="RAM type (DDR4, DDR5) — fill for RAM and Motherboards")
    price            = models.DecimalField(max_digits=12, decimal_places=2)
    old_price        = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    discount_percent = models.PositiveIntegerField(default=0)
    short_description = models.CharField(max_length=500, blank=True)
    description      = models.TextField(blank=True)
    main_image       = models.ImageField(upload_to='products/main/', blank=True, null=True)
    stock            = models.PositiveIntegerField(default=0)
    sku              = models.CharField(max_length=100, unique=True, blank=True)
    is_active        = models.BooleanField(default=True)
    is_featured      = models.BooleanField(default=False)
    is_new           = models.BooleanField(default=True)
    wattage          = models.PositiveIntegerField(null=True, blank=True, help_text="Power draw in watts")
    compatible_with  = models.ManyToManyField('self', blank=True, symmetrical=False)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering            = ['-created_at']
        verbose_name        = 'Product'
        verbose_name_plural = 'Products'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['is_featured','is_active']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if self.old_price and self.old_price > self.price:
            self.discount_percent = int(((self.old_price - self.price) / self.old_price) * 100)
        else:
            self.discount_percent = 0
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def is_low_stock(self):
        return 0 < self.stock <= 3

    @property
    def savings(self):
        return (self.old_price - self.price) if self.old_price else 0


class ProductImage(models.Model):
    product  = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image    = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    order    = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} — image {self.order}"


class ProductSpec(models.Model):
    product = models.ForeignKey(Product, related_name='specs', on_delete=models.CASCADE)
    key     = models.CharField(max_length=100)
    value   = models.CharField(max_length=300)
    order   = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} | {self.key}: {self.value}"


class ProductReview(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    product     = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user        = models.ForeignKey('accounts.CustomUser', related_name='reviews', on_delete=models.CASCADE)
    rating      = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    title       = models.CharField(max_length=200)
    body        = models.TextField()
    image       = models.ImageField(upload_to='reviews/', blank=True, null=True, help_text="Optional photo of received product")
    created_at  = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)   # auto-approve — admin can toggle off

    class Meta:
        ordering        = ['-created_at']
        unique_together = ('product', 'user')

    def __str__(self):
        return f"{self.user.email} → {self.product.name} ({self.rating}★)"
