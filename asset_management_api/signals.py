from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Asset, AssetHistory


@receiver(post_save, sender=Asset)
def create_asset_history(sender, instance, created, **kwargs):

    if created:
        AssetHistory.objects.create(
            asset=instance,
            action="CREATED",
            performed_by=instance.created_by
        )