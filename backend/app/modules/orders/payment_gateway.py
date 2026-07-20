from dataclasses import dataclass
from decimal import Decimal
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import Settings, get_settings


class PaymentGatewayError(ValueError):
    def __init__(self, code: str, message: str, *, terminal: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.terminal = terminal


@dataclass(frozen=True)
class GatewayRequestResult:
    authority: str
    redirect_url: str
    raw_response: dict


@dataclass(frozen=True)
class GatewayVerifyResult:
    reference_id: str
    code: int
    raw_response: dict


class ZarinpalGateway:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.base_url = (
            "https://sandbox.zarinpal.com"
            if self.settings.payment_zarinpal_sandbox
            else "https://payment.zarinpal.com"
        )

    def ensure_configured(self) -> None:
        if not self.settings.payment_gateway_enabled:
            raise PaymentGatewayError("GATEWAY_DISABLED", "Payment gateway is disabled")
        if self.settings.payment_gateway != "zarinpal":
            raise PaymentGatewayError("GATEWAY_UNSUPPORTED", "Payment gateway is unsupported")
        if len(self.settings.payment_merchant_id.strip()) != 36:
            raise PaymentGatewayError("MERCHANT_NOT_CONFIGURED", "Payment merchant is not configured")
        if not self.settings.payment_callback_base_url.startswith("https://") and not (
            self.settings.app_env == "development"
            and self.settings.payment_callback_base_url.startswith("http://localhost")
        ):
            raise PaymentGatewayError(
                "CALLBACK_URL_INVALID", "Payment callback must use HTTPS"
            )

    def request_payment(
        self, *, amount: Decimal, invoice_id: int, description: str
    ) -> GatewayRequestResult:
        self.ensure_configured()
        if amount != amount.to_integral_value() or amount <= 0:
            raise PaymentGatewayError(
                "INVALID_TOMAN_AMOUNT", "Gateway amount must be a positive whole toman value",
                terminal=True,
            )
        payload = self._post("/pg/v4/payment/request.json", {
            "merchant_id": self.settings.payment_merchant_id,
            "amount": int(amount),
            "currency": "IRT",
            "description": description,
            "callback_url": self.settings.payment_callback_base_url,
            "metadata": {"order_id": str(invoice_id), "auto_verify": False},
        })
        data = payload.get("data") or {}
        authority = str(data.get("authority") or "")
        if data.get("code") != 100 or not authority:
            raise self._provider_error(payload, "PAYMENT_REQUEST_REJECTED")
        return GatewayRequestResult(
            authority=authority,
            redirect_url=f"{self.base_url}/pg/StartPay/{authority}",
            raw_response=payload,
        )

    def verify_payment(self, *, amount: Decimal, authority: str) -> GatewayVerifyResult:
        self.ensure_configured()
        if amount != amount.to_integral_value() or amount <= 0:
            raise PaymentGatewayError(
                "INVALID_TOMAN_AMOUNT", "Gateway amount must be a positive whole toman value",
                terminal=True,
            )
        payload = self._post("/pg/v4/payment/verify.json", {
            "merchant_id": self.settings.payment_merchant_id,
            "amount": int(amount),
            "authority": authority,
        })
        data = payload.get("data") or {}
        code = data.get("code")
        if code not in {100, 101} or data.get("ref_id") is None:
            raise self._provider_error(payload, "PAYMENT_VERIFY_REJECTED")
        return GatewayVerifyResult(
            reference_id=str(data["ref_id"]), code=int(code), raw_response=payload
        )

    def _post(self, path: str, payload: dict) -> dict:
        request = Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(
                request, timeout=self.settings.payment_gateway_timeout_seconds
            ) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise PaymentGatewayError(
                f"GATEWAY_HTTP_{exc.code}", "Payment gateway rejected the request",
                terminal=400 <= exc.code < 500 and exc.code not in {408, 429},
            ) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise PaymentGatewayError("GATEWAY_NETWORK_ERROR", str(exc)) from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise PaymentGatewayError("GATEWAY_INVALID_RESPONSE", "Invalid gateway response") from exc

    @staticmethod
    def _provider_error(payload: dict, fallback: str) -> PaymentGatewayError:
        errors = payload.get("errors") or {}
        code = str(errors.get("code") or fallback) if isinstance(errors, dict) else fallback
        message = (
            str(errors.get("message") or "Payment gateway rejected the operation")
            if isinstance(errors, dict) else "Payment gateway rejected the operation"
        )
        return PaymentGatewayError(code, message, terminal=True)
