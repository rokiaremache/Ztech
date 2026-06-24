from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """
    Custom manager so email is the unique identifier
    instead of username.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    ZTech custom user model.
    Uses email as login instead of username.
    Supports gender theming preference.
    """
    THEME_CHOICES = [
        ('men', 'Dark Neon'),
        ('women', 'Pastel Neon'),
    ]

    # Core fields
    email           = models.EmailField(unique=True)
    first_name      = models.CharField(max_length=100)
    last_name       = models.CharField(max_length=100)
    phone           = models.CharField(max_length=20, blank=True)
    avatar          = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # Theme preference
    theme           = models.CharField(max_length=10, choices=THEME_CHOICES, default='men')

    # Newsletter
    subscribed_to_newsletter = models.BooleanField(default=False)

    # Django required fields
    is_active       = models.BooleanField(default=True)
    is_staff        = models.BooleanField(default=False)
    date_joined     = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name        = 'User'
        verbose_name_plural = 'Users'
        ordering            = ['-date_joined']

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_default_address(self):
        return self.addresses.filter(is_default=True).first()
    
    def get_short_name(self):
        return self.first_name


class Address(models.Model):
    """
    A user can have multiple saved addresses.
    One is marked as default.
    """
    WILAYA_CHOICES = [
        ('01', 'Adrar'), ('02', 'Chlef'), ('03', 'Laghouat'), ('04', 'Oum El Bouaghi'),
        ('05', 'Batna'), ('06', 'Béjaïa'), ('07', 'Biskra'), ('08', 'Béchar'),
        ('09', 'Blida'), ('10', 'Bouira'), ('11', 'Tamanrasset'), ('12', 'Tébessa'),
        ('13', 'Tlemcen'), ('14', 'Tiaret'), ('15', 'Tizi Ouzou'), ('16', 'Alger'),
        ('17', 'Djelfa'), ('18', 'Jijel'), ('19', 'Sétif'), ('20', 'Saïda'),
        ('21', 'Skikda'), ('22', 'Sidi Bel Abbès'), ('23', 'Annaba'), ('24', 'Guelma'),
        ('25', 'Constantine'), ('26', 'Médéa'), ('27', 'Mostaganem'), ('28', "M'Sila"),
        ('29', 'Mascara'), ('30', 'Ouargla'), ('31', 'Oran'), ('32', 'El Bayadh'),
        ('33', 'Illizi'), ('34', 'Bordj Bou Arréridj'), ('35', 'Boumerdès'),
        ('36', 'El Tarf'), ('37', 'Tindouf'), ('38', 'Tissemsilt'), ('39', 'El Oued'),
        ('40', 'Khenchela'), ('41', 'Souk Ahras'), ('42', 'Tipaza'), ('43', 'Mila'),
        ('44', 'Aïn Defla'), ('45', 'Naâma'), ('46', 'Aïn Témouchent'),
        ('47', 'Ghardaïa'), ('48', 'Relizane'), ('49', 'El M\'Ghair'), ('50', 'El Menia'),
        ('51', 'Ouled Djellal'), ('52', 'Bordj Badji Mokhtar'), ('53', 'Béni Abbès'),
        ('54', 'Timimoun'), ('55', 'Touggourt'), ('56', 'Djanet'),
        ('57', 'In Salah'), ('58', 'In Guezzam'),
    ]

    user        = models.ForeignKey(CustomUser, related_name='addresses', on_delete=models.CASCADE)
    full_name   = models.CharField(max_length=200)
    phone       = models.CharField(max_length=20)
    street      = models.CharField(max_length=300)
    city        = models.CharField(max_length=100)
    wilaya      = models.CharField(max_length=2, choices=WILAYA_CHOICES)
    postal_code = models.CharField(max_length=10, blank=True)
    is_default  = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Address'
        verbose_name_plural = 'Addresses'
        ordering            = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} — {self.city}, {self.get_wilaya_display()}"

    def save(self, *args, **kwargs):
        # If this is set as default, remove default from all others
        if self.is_default:
            self.user.addresses.exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

