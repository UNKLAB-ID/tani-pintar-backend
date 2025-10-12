import requests
from celery import shared_task
from django.conf import settings


@shared_task(
    autoretry_for=(requests.RequestException,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=False,
)
def send_vendor_discord_notification(
    vendor_id,
    notification_type="created",
    old_status=None,
):
    """
    Send Discord webhook notification for vendor lifecycle events.

    This task retrieves a vendor by ID and sends a formatted Discord
    notification with vendor details. The notification content varies
    based on the event type (creation, status change, etc.).

    Automatically retries up to 3 times on network failures with exponential backoff.

    Args:
        vendor_id: The ID of the vendor to send notification for.
        notification_type: Type of notification - "created" or "status_changed".
        old_status: The previous review status (only for status_changed).

    Returns:
        bool: True if notification was sent successfully, False otherwise.

    Raises:
        requests.RequestException: If all retry attempts fail.
    """
    from vendors.models import Vendor

    try:
        vendor = Vendor.objects.select_related("user").get(id=vendor_id)

        webhook_url = settings.VENDORS_NOTIFICATION_DISCORD_WEBHOOK_URL

        # Determine embed properties based on notification type
        if notification_type == "created":
            title = "New Vendor Registration"
            description = f"**{vendor.name}**"
            color = 0x00D166  # Green
            fields = [
                {
                    "name": "Type",
                    "value": vendor.get_vendor_type_display(),
                    "inline": True,
                },
                {
                    "name": "Status",
                    "value": vendor.get_review_status_display(),
                    "inline": True,
                },
                {"name": "User", "value": vendor.user.username, "inline": True},
            ]
        elif notification_type == "status_changed":
            title = "Vendor Status Changed"
            status_emoji = {
                Vendor.STATUS_APPROVED: "✅",
                Vendor.STATUS_REJECTED: "❌",
                Vendor.STATUS_RESUBMISSION: "🔄",
                Vendor.STATUS_PENDING: "⏳",
            }
            emoji = status_emoji.get(vendor.review_status, "")
            description = (
                f"**{vendor.name}**: `{old_status}` → `{vendor.review_status}` {emoji}"
            )
            # Color based on new status
            color_map = {
                Vendor.STATUS_APPROVED: 0x00D166,  # Green
                Vendor.STATUS_REJECTED: 0xFF0000,  # Red
                Vendor.STATUS_RESUBMISSION: 0xFFA500,  # Orange
                Vendor.STATUS_PENDING: 0x808080,  # Gray
            }
            color = color_map.get(vendor.review_status, 0x7289DA)
            fields = [
                {
                    "name": "Status",
                    "value": vendor.get_review_status_display(),
                    "inline": True,
                },
                {"name": "User", "value": vendor.user.username, "inline": True},
            ]
        else:
            # Default fallback
            title = "Vendor Notification"
            description = f"**{vendor.name}**"
            color = 0x7289DA  # Blue
            fields = [
                {"name": "User", "value": vendor.user.username, "inline": True},
            ]

        # Create Discord embed
        embed = {
            "title": title,
            "description": description,
            "fields": fields,
            "color": color,
        }

        payload = {"embeds": [embed]}
        response = requests.post(webhook_url, json=payload, timeout=10)

        return response.ok  # noqa: TRY300

    except Vendor.DoesNotExist:
        return False
