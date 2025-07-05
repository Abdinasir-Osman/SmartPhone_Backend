import httpx
import uuid
import os
from fastapi import APIRouter, Query
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/payment", tags=["Payment"])

API_URL = "https://api.waafipay.net/asm"


@router.post("/checkout")
async def process_payment(
    account_no: str = Query(..., description="Payer Account Number"),
    reference_id: str = Query(..., description="Reference ID"),
    invoice_id: str = Query(..., description="Invoice ID"),
    amount: float = Query(..., description="Amount to Pay")
):
    payload = {
        "schemaVersion": "1.0",
        "requestId": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "channelName": "WEB",
        "serviceName": "API_PURCHASE",
        "serviceParams": {
            "merchantUid": os.getenv("MERCHANT_UID"),
            "apiUserId": os.getenv("API_USER_ID"),
            "apiKey": os.getenv("API_KEY"),
            "paymentMethod": "MWALLET_ACCOUNT",
            "payerInfo": {
                "accountNo": account_no
            },
            "transactionInfo": {
                "referenceId": reference_id,
                "invoiceId": invoice_id,
                "amount": str(amount),
                "currency": "USD",
                "description": "Test Payment"
            }
        }
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(API_URL, json=payload)
            response.raise_for_status()  # optional: raise for bad HTTP codes
            return response.json()

    except httpx.ReadTimeout:
        return {
            "success": False,
            "message": "WaafiPay is taking too long to respond. Please try again later."
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        }
