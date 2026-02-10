

# from django.db import models
# from django.contrib.auth.models import AbstractUser
# from django.utils import timezone


# class SignupUser(AbstractUser):
#     created_by = models.CharField(max_length=100, blank=True, null=True)
#     created_date = models.DateTimeField(default=timezone.now)
    
#     class Meta:
#         verbose_name = 'User'
#         verbose_name_plural = 'Users'


# class Client(models.Model):
#     name = models.CharField(max_length=255)
#     address = models.TextField()
#     gst_no = models.CharField(max_length=50)
#     mobile_no = models.CharField(max_length=15)
#     contact_person = models.CharField(max_length=255)
#     created_by = models.CharField(max_length=100)
#     created_date = models.DateTimeField(default=timezone.now)
    
#     def __str__(self):
#         return self.name


# class Process(models.Model):
#     process_name = models.CharField(max_length=255)
#     created_by = models.CharField(max_length=100)
#     created_date = models.DateTimeField(default=timezone.now)
    
#     def __str__(self):
#         return self.process_name


# class Asset(models.Model):
#     output_unit_choices = [
#         ('kg', 'Kilograms'),
#         ('units', 'Units'),
#         ('liters', 'Liters'),
#         ('meters', 'Meters'),
#     ]

#     raw_material_unit_choices = [
#         ('kg', 'Kilograms'),
#         ('tons', 'Tons'),
#         ('liters', 'Liters'),
#         ('pieces', 'Pieces'),
#     ]  
#     name = models.CharField(max_length=255)
#     production_capacity = models.DecimalField(max_digits=10, decimal_places=2)
#     iot_device_id = models.CharField(max_length=100)
#     plc_device_id = models.CharField(max_length=100)
#     output_unit = models.CharField(max_length=50)
#     installation_date = models.DateField()
#     processed_id = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='assets')
#     x_example_id = models.CharField(max_length=100, verbose_name="Example ID")  # x:example ID from image
#     created_by = models.CharField(max_length=100)
#     created_date = models.DateTimeField(default=timezone.now)
    
#     def __str__(self):
#         return self.name


# class ProductionLine(models.Model):
#     name = models.CharField(max_length=255)
#     asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='production_lines')
#     process = models.ForeignKey(Process, on_delete=models.SET_NULL, null=True, blank=True, related_name='production_lines')
#     created_by = models.CharField(max_length=100)
#     created_date = models.DateTimeField(default=timezone.now)
    
#     def __str__(self):
#         return f"{self.name} - {self.asset.name}"

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator



class Asset(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=50, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# Utility function for custom IDs                              getattr(object, attribute_name, default_value)
# Parameters:
# object → the object you want to read from

# attribute_name → attribute name as string

# default_value (optional) → value to return if attribute doesn’t exist
# Why is getattr() useful?

# Because sometimes:

# You don’t know attribute name in advance

# Attribute name comes from user input or variable

# You want generic code (like serializers, filters, sorting)


def generate_unique_id(model_class, field_name, prefix):    # generate_unique_id is a custom "Smart Counter" function designed to automate the creation of IDs like ASN_0001

    last_instance = model_class.objects.order_by('id').last()

    if not last_instance:
        return f"{prefix}_0001"

    last_id = getattr(last_instance, field_name)     #This dynamically grabs the value of the ID (e.g., it gets "ASN_0005").
    try:
        last_num = int(last_id.split('_')[-1])         #It cuts the string at the underscore and takes the last part—the digits ("0005").
        return f"{prefix}_{last_num + 1:04d}"
    except (ValueError, IndexError):
        return f"{prefix}_0001"


gst_validator = RegexValidator(
    regex=r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$',
    message="Enter a valid GST number (15 characters)"
)

mobile_validator = RegexValidator(
    regex=r'^[6-9]\d{9}$',
    message="Enter a valid 10-digit mobile number"
)

#  Custom User Model

class SignupUser(AbstractUser):
    phone = models.CharField(max_length=15, unique=True)
    # role = models.CharField(max_length=50)
    # groups = models.ManyToManyField('auth.Group', related_name='signupuser_groups', blank=True) 
    # user_permissions = models.ManyToManyField('auth.Permission', related_name='signupuser_permissions', blank=True)

    def __str__(self):
        return self.username


# Process Model

class Process(models.Model):
    process_id = models.CharField(max_length=20, unique=True, editable=False, null = True, blank =True)

    process_name = models.CharField(max_length=255, null = True)

    # class Meta:
    #     permissions = [
    #         ("can_view_process", "Can view process"),
    #     ]

    created_by = models.ForeignKey(
        SignupUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.process_id:
            self.process_id = generate_unique_id(Process, 'process_id', 'Pro')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.process_id} - {self.process_name}"

# Client Model

class Client(models.Model):
    client_id = models.CharField(max_length=20, unique=True, editable=False,null=True, blank=True)
    name = models.CharField(max_length=255, unique= True, null=True)
    address = models.TextField(max_length=255, null=True)
    gst_no = models.CharField(max_length=50, unique=True)
    mobile_no = models.CharField(max_length=15)
    contact_person = models.CharField(max_length=255)
    location = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField(protocol='both',unpack_ipv4=False,null=True)
    geo_location = models.JSONField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_by = models.ForeignKey(
        SignupUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.client_id:
            self.client_id = generate_unique_id(Client, 'client_id', 'CL')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.client_id} - {self.name}"

# Asset Model

class Asset(models.Model):
    output_unit_choices = [
        ('kg', 'Kilograms'),
        ('units', 'Units'),
        ('liters', 'Liters'),
        ('meters', 'Meters'),
    ]

    raw_material_choices = [
        ('kg', 'Kilograms'),
        ('tons', 'Tons'),
        ('liters', 'Liters'),
        ('pieces', 'Pieces'),
    ]


    # class Meta:
    #     permissions = [
    #         ("can_manage_asset", "Can manage asset"),
    #     ]

    asset_id = models.CharField(max_length=20, unique=True, editable=False, null = True, blank =True)
    # production_id = models.CharField(max_length=20, unique=True, editable=False, null = True, blank =True)
    name = models.CharField(max_length=255, null = True)
    production_capacity = models.DecimalField(max_digits=10, decimal_places=2)
    iot_device_id = models.CharField(max_length=100, null = True)
    plc_device_id = models.CharField(max_length=100, null = True)
    energy_meter_id = models.CharField(max_length=100, blank=True, null=True)
    ip_address = models.GenericIPAddressField(protocol='both',unpack_ipv4=False,null=True)
    #geo_location = models.JSONField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    output_unit = models.CharField(
        max_length=20,
        choices = output_unit_choices, 
        blank = True,
        null = True )
         
    raw_material_unit = models.CharField(
        max_length=20,
        choices = raw_material_choices,
        blank = True,
        null = True
    )

    installation_date = models.DateField()

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='assets'
    )

    process = models.ForeignKey(
        Process,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        SignupUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.asset_id:
            self.asset_id = generate_unique_id(Asset, 'asset_id', 'ASN')


        # if not self.production_id:
        #     self.production_id = generate_unique_id(Asset, 'production_id', 'Prod')

        super().save(*args, **kwargs)

        def __str__(self):
            return f"{self.asset_id} - {self.name}"

# Production Line Model

class ProductionLine(models.Model):
    name = models.CharField(max_length=255)

    assets = models.ManyToManyField(
        Asset,
        related_name='production_lines',
        blank=True
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='production_lines',
        null = True,
        blank=True,
        default=1
    )

    created_by = models.ForeignKey(
        SignupUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

