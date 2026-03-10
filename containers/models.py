from django.db import models
from django.contrib.auth.models import User


class Container(models.Model):
    name = models.CharField(max_length=100)
    tailscale_ip = models.GenericIPAddressField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "name")

    def __str__(self):
        return f"{self.name} ({self.tailscale_ip})"