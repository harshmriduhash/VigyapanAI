import hmac
import hashlib
from typing import Dict

import razorpay
from fastapi import HTTPException, status

from config import get_settings
from credits import add_credits


PLANS_INR: Dict[str, Dict[str, int]] = {
    # simple credit packs: price in paise, credits granted
    "starter": {"amount": 49900, "credits": 20},   # INR 499
    "pro": {"amount": 149900, "credits": 80},      # INR 1,499
    "scale": {"amount": 299900, "credits": 180},   # INR 2,999
}


def razorpay_client() -> razorpay.Client:
    settings = get_settings()
    return razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))


def create_order(user_id: str, plan: str) -> dict:
    if plan not in PLANS_INR:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid plan")
    plan_info = PLANS_INR[plan]
    client = razorpay_client()
    order = client.order.create(
        dict(
            amount=plan_info["amount"],
            currency="INR",
            payment_capture=1,
            notes={"user_id": user_id, "plan": plan},
        )
    )
    return order


def verify_and_apply(payload: bytes, signature: str, order_id: str, payment_id: str) -> None:
    settings = get_settings()
    body = f"{order_id}|{payment_id}".encode()
    computed = hmac.new(settings.razorpay_key_secret.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(computed, signature):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature")

    # Razorpay recommends verifying payment status via API
    client = razorpay_client()
    payment = client.payment.fetch(payment_id)
    if payment.get("status") != "captured":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment not captured")

    notes = payment.get("notes") or {}
    user_id = notes.get("user_id")
    plan = notes.get("plan")
    if not user_id or plan not in PLANS_INR:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing user or plan in payment notes")

    credits = PLANS_INR[plan]["credits"]
    add_credits(user_id, credits)

