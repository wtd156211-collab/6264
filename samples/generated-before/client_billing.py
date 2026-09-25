# stubforge: kind=client def=billing rev=9fc7d7cd2142 skel=ac51202e63c8
from typing import Any, Callable

from model_billing import ChargeCardRequest, ChargeCardResponse, GetChargeRequest

OP_NAMES: dict[str, str] = {}


class BillingClient:
    def __init__(self, call: Callable[[str, dict[str, Any]], object]) -> None:
        self._call = call

    def charge_card(self, request: ChargeCardRequest) -> ChargeCardResponse:
        # >>> stubforge:hand charge_card_hooks
        # <<< stubforge:hand charge_card_hooks
        return ChargeCardResponse.from_wire(self._call('ChargeCard', request.to_wire()))

    def get_charge(self, request: GetChargeRequest) -> ChargeCardResponse:
        # >>> stubforge:hand get_charge_hooks
        # 现场加的：查询前先记一笔，线上排查用
        print("[audit] GetCharge", request.charge_id)
        # <<< stubforge:hand get_charge_hooks
        return ChargeCardResponse.from_wire(self._call('GetCharge', request.to_wire()))
