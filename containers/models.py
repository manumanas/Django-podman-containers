from django.db import models

# Create your models here.

# class Container(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     wireguard_ip = models.GenericIPAddressField(unique=True)
#     public_key = models.CharField(max_length=255, unique=True)

#     def __str__(self):
#         return f"{self.name} ({self.wireguard_ip})"

class Container(models.Model):
    name = models.CharField(max_length=100, unique=True)
    tailscale_ip = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.tailscale_ip})"