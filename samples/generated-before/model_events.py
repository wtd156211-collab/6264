# stubforge: kind=model def=events rev=dfe9b3b4f422 skel=a05643c4c32f
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


def _list(value: object, path: str, decode) -> list:
    if not isinstance(value, list):
        raise ValueError(f"{path}: expected list, got {type(value).__name__}")
    return [decode(item, f"{path}[{index}]") for index, item in enumerate(value)]


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


def _enum_EventKind(value: object, path: str):
    return _enum(EventKind, value, path)


def _record_Event(value: object, path: str):
    return Event.from_wire(value)


def _record_ImportRequest(value: object, path: str):
    return ImportRequest.from_wire(value)


def _record_ImportResponse(value: object, path: str):
    return ImportResponse.from_wire(value)


def _record_ListRequest(value: object, path: str):
    return ListRequest.from_wire(value)


def _record_ListResponse(value: object, path: str):
    return ListResponse.from_wire(value)


FIELD_NAMES: dict[str, dict[str, str]] = {
    'Event': {'class_': 'class', 'from_': 'from', 'id_': 'id', 'type_': 'type'},
    'ListResponse': {'next_': 'next'},
}


class EventKind(enum.StrEnum):
    CREATED = 'created'
    UPDATED = 'updated'
    DELETED = 'deleted'


@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class Event:
    card_id: str | None = None
    class_: str
    from_: str | None = None
    id_: str
    kind: EventKind
    retry_count: int = 0
    type_: str

    def to_wire(self) -> dict[str, Any]:
        return {
            'card_id': self.card_id,
            'class': self.class_,
            'from': self.from_,
            'id': self.id_,
            'kind': self.kind,
            'retry_count': self.retry_count,
            'type': self.type_,
        }

    @classmethod
    def from_wire(cls, obj: object) -> "Event":
        data = _record(obj, "Event")
        return cls(
            card_id=_take(data, 'card_id', 'Event.card_id', _str, None),
            class_=_take(data, 'class', 'Event.class', _str, _MISSING),
            from_=_take(data, 'from', 'Event.from', _str, None),
            id_=_take(data, 'id', 'Event.id', _str, _MISSING),
            kind=_take(data, 'kind', 'Event.kind', _enum_EventKind, _MISSING),
            retry_count=_take(data, 'retry_count', 'Event.retry_count', _int, 0),
            type_=_take(data, 'type', 'Event.type', _str, _MISSING),
        )

    def validate(self) -> None:
        # >>> stubforge:hand event_rules
        # 现场加的：class 与 kind 不能同时是 deleted
        if self.class_ == "deleted" and self.kind == EventKind.DELETED:
            raise ValueError("class 与 kind 冲突")
        # <<< stubforge:hand event_rules
        return None

@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ImportRequest:
    dry_run: bool = False
    events: list[Event]

    def to_wire(self) -> dict[str, Any]:
        return {
            'dry_run': self.dry_run,
            'events': [item.to_wire() for item in self.events],
        }

    @classmethod
    def from_wire(cls, obj: object) -> "ImportRequest":
        data = _record(obj, "ImportRequest")
        return cls(
            dry_run=_take(data, 'dry_run', 'ImportRequest.dry_run', _bool, False),
            events=_take(data, 'events', 'ImportRequest.events', lambda value, path: _list(value, path, _record_Event), _MISSING),
        )

    def validate(self) -> None:
        # >>> stubforge:hand import_request_rules
        # <<< stubforge:hand import_request_rules
        return None

@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ImportResponse:
    accepted: int
    rejected: list[str] | None = None

    def to_wire(self) -> dict[str, Any]:
        return {
            'accepted': self.accepted,
            'rejected': None if self.rejected is None else [item for item in self.rejected],
        }

    @classmethod
    def from_wire(cls, obj: object) -> "ImportResponse":
        data = _record(obj, "ImportResponse")
        return cls(
            accepted=_take(data, 'accepted', 'ImportResponse.accepted', _int, _MISSING),
            rejected=_take(data, 'rejected', 'ImportResponse.rejected', lambda value, path: _list(value, path, _str), None),
        )

    def validate(self) -> None:
        # >>> stubforge:hand import_response_rules
        # <<< stubforge:hand import_response_rules
        return None

@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ListRequest:
    cursor: str | None = None
    limit: int = 20

    def to_wire(self) -> dict[str, Any]:
        return {
            'cursor': self.cursor,
            'limit': self.limit,
        }

    @classmethod
    def from_wire(cls, obj: object) -> "ListRequest":
        data = _record(obj, "ListRequest")
        return cls(
            cursor=_take(data, 'cursor', 'ListRequest.cursor', _str, None),
            limit=_take(data, 'limit', 'ListRequest.limit', _int, 20),
        )

    def validate(self) -> None:
        # >>> stubforge:hand list_request_rules
        # <<< stubforge:hand list_request_rules
        return None

@dataclasses.dataclass(frozen=True, slots=True, kw_only=True)
class ListResponse:
    items: list[Event]
    next_: str | None = None

    def to_wire(self) -> dict[str, Any]:
        return {
            'items': [item.to_wire() for item in self.items],
            'next': self.next_,
        }

    @classmethod
    def from_wire(cls, obj: object) -> "ListResponse":
        data = _record(obj, "ListResponse")
        return cls(
            items=_take(data, 'items', 'ListResponse.items', lambda value, path: _list(value, path, _record_Event), _MISSING),
            next_=_take(data, 'next', 'ListResponse.next', _str, None),
        )

    def validate(self) -> None:
        # >>> stubforge:hand list_response_rules
        # <<< stubforge:hand list_response_rules
        return None
