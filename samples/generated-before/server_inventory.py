# stubforge: kind=server def=inventory rev=69186e2c563c skel=c52856022b2e
from typing import Any

from model_inventory import ReserveRequest, ReserveResponse, SnapshotRequest, SnapshotResponse

OP_NAMES: dict[str, str] = {}

_METHOD_BY_WIRE: dict[str, str] = {'Reserve': 'reserve', 'Snapshot': 'snapshot'}

_REQUEST_TYPES: dict[str, type] = {'reserve': ReserveRequest, 'snapshot': SnapshotRequest}


class InventoryServicer:
    def reserve(self, request: ReserveRequest) -> ReserveResponse:
        raise NotImplementedError('Reserve')

    def snapshot(self, request: SnapshotRequest) -> SnapshotResponse:
        raise NotImplementedError('Snapshot')

    def dispatch(self, name: str, payload: object) -> object:
        method = _METHOD_BY_WIRE.get(name, name)
        handler = getattr(self, method, None)
        request_type = _REQUEST_TYPES.get(method)
        if handler is None or request_type is None:
            raise NotImplementedError(name)
        return handler(request_type.from_wire(payload)).to_wire()

