from celery import shared_task


@shared_task
def send_verification_code(verification_code_id):
    from accounts.models import VerificationCode

    verification_code = VerificationCode.objects.get(id=verification_code_id)
    verification_code.send_discord_webhook_notification()
