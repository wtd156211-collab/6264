# stubforge: kind=server def=billing rev=9fc7d7cd2142 skel=ffe990c8dc1c
from typing import Any

from model_billing import ChargeCardRequest, ChargeCardResponse, GetChargeRequest

OP_NAMES: dict[str, str] = {}

_METHOD_BY_WIRE: dict[str, str] = {'ChargeCard': 'charge_card', 'GetCharge': 'get_charge'}

_REQUEST_TYPES: dict[str, type] = {'charge_card': ChargeCardRequest, 'get_charge': GetChargeRequest}


class BillingServicer:
    def charge_card(self, request: ChargeCardRequest) -> ChargeCardResponse:
        # >>> stubforge:hand charge_card_impl
        # 现场手写的重试（2026-03-02 线上加的，别删）
        for attempt in range(3):
            try:
                return dispatch_upstream(request)
            except TimeoutError:
                if attempt == 2:
                    raise
        # <<< stubforge:hand charge_card_impl
        raise NotImplementedError('ChargeCard')
        # 2026-03-02 联调临时改过：上游偶发超时，先手工兜住

    def get_charge(self, request: GetChargeRequest) -> ChargeCardResponse:
        # >>> stubforge:hand get_charge_impl
        # <<< stubforge:hand get_charge_impl
        raise NotImplementedError('GetCharge')

    def dispatch(self, name: str, payload: object) -> object:
        method = _METHOD_BY_WIRE.get(name, name)
        handler = getattr(self, method, None)
        request_type = _REQUEST_TYPES.get(method)
        if handler is None or request_type is None:
            raise NotImplementedError(name)
        return handler(request_type.from_wire(payload)).to_wire()

# >>> stubforge:hand server_setup
# <<< stubforge:hand server_setup
