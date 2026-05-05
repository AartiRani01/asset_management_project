from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Client, Process, Asset
from .models import generate_unique_id
import logging

logger = logging.getLogger(__name__)


# Helper function to send email notification
def send_asset_change_email(asset, changed_by, changes_dict, is_created=False):
    """Send email notification for asset changes"""
    try:
        subject = f"Asset {'Created' if is_created else 'Updated'}: {asset.name} ({asset.asset_id})"
        
        # Build email body
        body = f"""
Asset Change Notification
{'=' * 40}

Asset Name: {asset.name}
Asset ID: {asset.asset_id or 'Not assigned yet'}
Client: {asset.client.name if asset.client else 'N/A'}
Process: {asset.process.process_name if asset.process else 'N/A'}

Action: {'CREATED' if is_created else 'UPDATED'}
Changed By: {changed_by.username if changed_by else 'System'}
Timestamp: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        if is_created:
            body += f"""
Asset Details:
{'-' * 40}
Description: {asset.description or 'N/A'}
Status: {asset.status}
Status of Asset: {asset.status_of_asset}
Production Capacity: {asset.production_capacity}
Installation Date: {asset.installation_date}
IoT Device ID: {asset.iot_device_id or 'N/A'}
PLC Device ID: {asset.plc_device_id or 'N/A'}
Location: {asset.city or 'N/A'}, {asset.region or 'N/A'}, {asset.country or 'N/A'}
"""
        else:
            body += f"""
Changes Made:
{'-' * 40}
"""
            if changes_dict:
                for field, values in changes_dict.items():
                    body += f"  • {field}: '{values[0]}' → '{values[1]}'\n"
            else:
                body += "  • Multiple fields were updated (detailed changes not tracked)\n"
        
        body += f"""
{'=' * 40}
Please log into the system to review the asset details.
"""
        
        recipient_list = getattr(settings, 'ASSET_NOTIFICATION_RECIPIENTS', [settings.DEFAULT_FROM_EMAIL])
        
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        
        logger.info(f"Asset change email sent for {asset.asset_id}")
        
    except Exception as e:
        logger.error(f"Failed to send asset change email: {str(e)}")


def get_changed_fields(old_instance, new_instance, exclude_fields=['created_date', 'updated_date', 'created_at']):
    """Compare two model instances and return dictionary of changed fields"""
    changes = {}
    
    if not old_instance:
        return changes
    
    for field in old_instance._meta.fields:
        field_name = field.name
        
        if field_name in exclude_fields:
            continue
            
        old_value = getattr(old_instance, field_name)
        new_value = getattr(new_instance, field_name)
        
        if old_value != new_value:
            if hasattr(old_value, 'strftime'):
                old_value = old_value.strftime('%Y-%m-%d %H:%M:%S')
            if hasattr(new_value, 'strftime'):
                new_value = new_value.strftime('%Y-%m-%d %H:%M:%S')
            
            changes[field_name] = (str(old_value), str(new_value))
    
    return changes


# PRE SAVE signals for generating IDs
@receiver(pre_save, sender=Client)
def set_client_id(sender, instance, **kwargs):
    if not instance.client_id:
        instance.client_id = generate_unique_id(Client, 'client_id', 'CL')


@receiver(pre_save, sender=Process)
def set_process_id(sender, instance, **kwargs):
    if not instance.process_id:
        instance.process_id = generate_unique_id(Process, 'process_id', 'Pro')


@receiver(pre_save, sender=Asset)
def set_asset_id(sender, instance, **kwargs):
    if not instance.asset_id:
        instance.asset_id = generate_unique_id(Asset, 'asset_id', 'AST')


# POST SAVE signal for Asset with email notification
@receiver(post_save, sender=Asset)
def asset_created_or_updated(sender, instance, created, **kwargs):
    """Send email notification when asset is created or updated"""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Get first admin user as changed_by (or implement your own user tracking)
        changed_by = User.objects.filter(is_superuser=True).first()
        
        if created:
            # Asset was created
            print(f"Asset CREATED: {instance.name} (ID: {instance.asset_id})")
            send_asset_change_email(instance, changed_by, {}, is_created=True)
            
        else:
            # Asset was updated - fetch previous state
            try:
                old_instance = Asset.objects.get(pk=instance.pk)
                changes = get_changed_fields(old_instance, instance)
                
                if changes:
                    print(f"Asset UPDATED: {instance.name} (ID: {instance.asset_id})")
                    print(f"Changes: {changes}")
                    send_asset_change_email(instance, changed_by, changes, is_created=False)
                else:
                    print(f"Asset saved but no field changes detected for {instance.name}")
                    
            except Asset.DoesNotExist:
                print(f"Asset UPDATED: {instance.name} (ID: {instance.asset_id}) - Could not fetch previous state")
                send_asset_change_email(instance, changed_by, {}, is_created=False)
                
    except Exception as e:
        print(f"Error in asset_created_or_updated signal: {str(e)}")
        logger.error(f"Error in asset signal: {str(e)}")