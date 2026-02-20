from dataclasses import dataclass
from typing import Any, Dict

import requests


@dataclass
class FileMeta:
    uuid: str
    filename: str
    file_extension: str
    size: int
    path: str
    comment: str | None
    created_at: str
    updated_at: str | None


class APIError(Exception):
    pass


class FileAlreadyExistsError(APIError):
    pass


class FileNotFoundError(APIError):
    pass


class FileService:
    """Синхронный клиент для управления файлами через HTTP API

    Методы реализуют эндпоинты:
    - POST /files
    - GET /files/{file_id}/meta
    - GET /files/{file_id}
    """

    def __init__(
        self,
        host: str,
        session: requests.Session | None = None,
        timeout_seconds: int = 30,
        port: int | None = None,
    ):
        self._host = host.rstrip("/")
        if port is not None:
            self._host += f":{port}"
        self._session = session or requests.Session()
        self._timeout = timeout_seconds

    def _url(self, path: str) -> str:
        return f"{self._host}{path}"

    def _raise(self, resp: requests.Response) -> None:
        if resp.status_code == 409:
            raise FileAlreadyExistsError(f"File already exists: {resp.text}")
        elif resp.status_code == 404:
            raise FileNotFoundError(f"File not found: {resp.text}")
        elif not resp.ok:
            raise APIError(
                f"API request failed with status {resp.status_code}: {resp.text}"
            )

    def post_file(
        self,
        filename: str,
        file_extension: str,
        path: str,
        file_content: bytes,
        comment: str | None = None,
    ) -> FileMeta:
        """Загружает файл и метаданные; возвращает `FileMeta`-объект."""
        files = {"file": (f"{filename}.{file_extension}", file_content)}
        data: Dict[str, Any] = {
            "filename": filename,
            "file_extension": file_extension,
            "path": path,
        }
        if comment is not None:
            data["comment"] = comment

        resp = self._session.post(
            self._url("/files"), files=files, data=data, timeout=self._timeout
        )
        self._raise(resp)
        response_data: Dict[str, Any] = resp.json()

        uuid = response_data.get("uuid", None)
        if uuid is None:
            raise APIError("Failed to retrieve UUID from response")
        return FileMeta(**response_data)

    def get_file_meta(self, file_id: str) -> FileMeta:
        resp = self._session.get(
            self._url(f"/files/{file_id}/meta"), timeout=self._timeout
        )
        self._raise(resp)
        return FileMeta(**resp.json())

    def get_file(self, file_id: str) -> bytes:
        resp = self._session.get(self._url(f"/files/{file_id}"), timeout=self._timeout)
        self._raise(resp)
        return resp.content


if __name__ == "__main__":
    file_service = FileService(host="http://localhost:8000")
    file_content = b"file filler"
    response = file_service.post_file(
        filename="example",
        file_extension="txt",
        path="/documents/",
        file_content=file_content,
        comment="Example file upload",
    )

    print("файл:", response)

    file_id = response.uuid
    meta = file_service.get_file_meta(file_id)
    print("файл:", meta)

    content = file_service.get_file(file_id)
    print("файл:", content.decode())
