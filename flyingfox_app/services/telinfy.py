import requests

from django.conf import settings


def send_otp_sms(phone_number, otp):
    url = f"{settings.TELINFY_BASE_URL}/api/v1/sms/send"

    payload = {
        "Sender_Name": settings.TELINFY_SMS_SENDER_NAME,
        "SMS_Message": f"Your OTP is {otp}. Thank you.",
        "mobile_Number": phone_number,
        "template_id": settings.TELINFY_SMS_TEMPLATE_ID,
        "campaign_name": "OTP",
    }

    headers = {
        "x-api-key": settings.TELINFY_API_KEY,
        "Content-Type": "application/json",
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=15,
    )

    response.raise_for_status()

    return response.json()