from typing import Any, Dict, List

from ..error.illegal_attr_checker import IllegalAttrChecker
from ..query_runner.query_runner import QueryResult, QueryRunner


class SimilarityAlgoRunner(IllegalAttrChecker):
    def __init__(self, query_runner: QueryRunner, namespace: str):
        self._query_runner = query_runner
        self._namespace = namespace

    def stats(self, **config: Any) -> QueryResult:
        self._namespace += ".stats"
        return self._run_procedure(config)

    def stream(self, **config: Any) -> QueryResult:
        self._namespace += ".stream"
        return self._run_procedure(config)

    def write(self, **config: Any) -> QueryResult:
        self._namespace += ".write"
        return self._run_procedure(config)

    def _run_procedure(self, config: Dict[str, Any]) -> QueryResult:
        return self._query_runner.run_query(
            f"CALL {self._namespace}($config)", {"config": config}
        )

    def __call__(self, vector1: List[int], vector2: List[int]) -> float:
        result = self._query_runner.run_query(
            f"RETURN {self._namespace}({vector1}, {vector2}) AS similarity"
        )

        return result[0]["similarity"]  # type: ignore
