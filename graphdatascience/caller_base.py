from abc import ABC
from typing import NoReturn

from .error.endpoint_suggester import generate_suggestive_error_message
from .query_runner.query_runner import QueryRunner
from .server_version.server_version import ServerVersion


all_endpoints = {
    "gds.kmeans.stream"
}


class CallerBase(ABC):
    def __init__(self, query_runner: QueryRunner, namespace: str, server_version: ServerVersion):
        self._query_runner = query_runner
        self._namespace = namespace
        self._server_version = server_version

        self.__name__ = f"{namespace}"

        signature = """\n
            Args:
                param1: The first parameter.
                param2: The second parameter.

            Returns:
                The return value. True for success, False otherwise.
        """

        if namespace in all_endpoints:
            self.__doc__ = signature

        if namespace + ".stream" in all_endpoints:
            self.__custom_documentations__ = {
                "stream": signature,
            }

    def _raise_suggestive_error_message(self, requested_endpoint: str) -> NoReturn:
        list_result = self._query_runner.call_procedure(
            endpoint="gds.list",
            yields=["name"],
            custom_error=False,
        )
        all_endpoints = list_result["name"].tolist()

        raise SyntaxError(generate_suggestive_error_message(requested_endpoint, all_endpoints))
