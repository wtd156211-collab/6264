from typing import Any, Callable

from model_events import ImportRequest, ImportResponse, ListRequest, ListResponse

OP_NAMES: dict[str, str] = {'import_': 'Import', 'list_': 'List'}


class EventsClient:
    def __init__(self, call: Callable[[str, dict[str, Any]], object]) -> None:
        self._call = call

    def import_(self, request: ImportRequest) -> ImportResponse:
        # >>> stubforge:hand import_hooks
        # 现场加的：超过 500 条先挡掉，别让上游超时
        if len(request.events) > 500:
            raise ValueError("一次最多 500 条")
        # <<< stubforge:hand import_hooks
        return ImportResponse.from_wire(self._call('Import', request.to_wire()))

    def list_(self, request: ListRequest) -> ListResponse:
        # >>> stubforge:hand list_hooks
        # <<< stubforge:hand list_hooks
        return ListResponse.from_wire(self._call('List', request.to_wire()))
