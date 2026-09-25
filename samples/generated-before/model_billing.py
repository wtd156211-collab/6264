# stubforge: kind=model def=billing rev=3245c9aaa114 skel=d1d0386d8c94
import dataclasses
import enum
from typing import Any

_MISSING = object()

def _record(value: object, path: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected object, got {type(value).__name__}")
    return value


def _take(data: dict, name: str, path: str, decode, default):
    if name in data and data[name] is not None:
        return decode(data[name], path)
    if default is _MISSING:
        if name in data:
            raise ValueError(f"{path}: expected value, got null")
        raise ValueError(f"{path}: missing required field")
    return default


def _map(value: object, path: str, decode) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected object, got {type(value).__name__}")
    return {key: decode(item, f"{path}.{key}") for key, item in value.items()}


def _str(value: object, path: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{path}: expected string, got {type(value).__name__}")
    return value


def _int(value: object, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{path}: expected integer, got {type(value).__name__}")
    return value


def _bool(value: object, path: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{path}: expected boolean, got {type(value).__name__}")
    return value


def _enum(enum_type, value: object, path: str):
    if not isinstance(value, str):
        raise ValueError(f"{path}: expected string, got {type(value).__name__}")
    try:
        return enum_type(value)
    except ValueError as error:
        raise ValueError(f"{path}: unknown {enum_type.__name__} value {value!r}") from error


def _enum_ChargeStatus(value: object, path: str):
    return _enum(ChargeStatus, value, path)


def _record_ChargeCardRequest(value: object, path: str):
    return ChargeCardRequest.from_wire(value)


def _record_ChargeCardResponse(value: object, path: str):
    return ChargeCardResponse.from_wire(value)


def _record_GetChargeRequest(value: object, path: str):
    return GetChargeRequest.from_wire(value)


def _record_Money(value: object, path: str):
    return Money.from_wire(value)


FIELD_NAMES: dict[str, dict[str, str]] = {}


class ChargeStatus(enum.StrEnum):
    OK = 'ok'
    DECLINED = 'declined'
    RETRY_LATER = 'retry_later'


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ChargeCardRequest:
    amount: Money
    attempts: int | None = 1
    note: str | None = None
    order_id: str
    tags: dict[str, str] | None = None

    def to_wire(self) -> dict[str, Any]:
        return {
            'amount': self.amount.to_wire(),
            'attempts': self.attempts,
            'note': self.note,
            'order_id': self.order_id,
            'tags': None if self.tags is None else {key: item for key, item in self.tags.items()},
        }

    @classmethod
    def from_wire(cls, obj: object) -> "ChargeCardRequest":
        data = _record(obj, "ChargeCardRequest")
        return cls(
            amount=_take(data, 'amount', 'ChargeCardRequest.amount', _record_Money, _MISSING),
            attempts=_take(data, 'attempts', 'ChargeCardRequest.attempts', _int, 1),
            note=_take(data, 'note', 'ChargeCardRequest.note', _str, None),
            order_id=_take(data, 'order_id', 'ChargeCardRequest.order_id', _str, _MISSING),
            tags=_take(data, 'tags', 'ChargeCardRequest.tags', lambda value, path: _map(value, path, _str), None),
        )

    def validate(self) -> None:
        # >>> stubforge:hand charge_card_request_rules
        # 现场加的：order_id 必须是大写字母开头的单号
        if not self.order_id[:1].isupper():
            raise ValueError("order_id 形状不对")
        # <<< stubforge:hand charge_card_request_rules
        return None

@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ChargeCardResponse:
    amount: Money
    charge_id: str
    status: ChargeStatus

    def to_wire(self) -> dict[str, Any]:
        return {
            'amount': self.amount.to_wire(),
            'charge_id': self.charge_id,
            'status': self.status,
        }

    @classmethod
    def from_wire(cls, obj: object) -> "ChargeCardResponse":
        data = _record(obj, "ChargeCardResponse")
        return cls(
            amount=_take(data, 'amount', 'ChargeCardResponse.amount', _record_Money, _MISSING),
            charge_id=_take(data, 'charge_id', 'ChargeCardResponse.charge_id', _str, _MISSING),
            status=_take(data, 'status', 'ChargeCardResponse.status', _enum_ChargeStatus, _MISSING),
        )

    def validate(self) -> None:
        # >>> stubforge:hand charge_card_response_rules
        # <<< stubforge:hand charge_card_response_rules
        return None

@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class GetChargeRequest:
    charge_id: str
    include_events: bool | None = False

    def to_wire(self) -> dict[str, Any]:
        return {
            'charge_id': self.charge_id,
            'include_events': self.include_events,
        }

    @classmethod
    def from_wire(cls, obj: object) -> "GetChargeRequest":
        data = _record(obj, "GetChargeRequest")
        return cls(
            charge_id=_take(data, 'charge_id', 'GetChargeRequest.charge_id', _str, _MISSING),
            include_events=_take(data, 'include_events', 'GetChargeRequest.include_events', _bool, False),
        )

    def validate(self) -> None:
        # >>> stubforge:hand get_charge_request_rules
        # <<< stubforge:hand get_charge_request_rules
        return None

@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class Money:
    amount: int
    currency: str = 'CNY'

    def to_wire(self) -> dict[str, Any]:
        return {
            'amount': self.amount,
            'currency': self.currency,
        }

    @classmethod
    def from_wire(cls, obj: object) -> "Money":
        data = _record(obj, "Money")
        return cls(
            amount=_take(data, 'amount', 'Money.amount', _int, _MISSING),
            currency=_take(data, 'currency', 'Money.currency', _str, 'CNY'),
        )

    def validate(self) -> None:
        # >>> stubforge:hand money_rules
        # 现场加的：金额一律是最小币种单位，这里只做形状校验
        if self.amount < 0:
            raise ValueError("amount 不能是负数")
        # <<< stubforge:hand money_rules
        return None
