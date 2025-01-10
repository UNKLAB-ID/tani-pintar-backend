from celery import shared_task


@shared_task
def send_verification_code(verification_code_id):
    from accounts.models import VerificationCode

    verification_code = VerificationCode.objects.get(id=verification_code_id)
    verification_code.send_discord_webhook_notification()


@shared_task
def send_login_code(login_code_id):
    from accounts.models import LoginCode

    login_code = LoginCode.objects.get(id=login_code_id)
    login_code.send_discord_webhook_notification()
