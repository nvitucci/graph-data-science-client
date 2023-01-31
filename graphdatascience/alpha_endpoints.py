from .algo.algo_endpoints import AlgoEndpoints
from .algo.single_mode_algo_endpoints import SingleModeAlgoEndpoints
from .call_builder import CallBuilder
from .graph.graph_endpoints import GraphAlphaEndpoints
from .model.model_endpoints import ModelAlphaEndpoints
from .pipeline.pipeline_endpoints import PipelineAlphaEndpoints
from .query_runner.query_runner import QueryRunner
from .server_version.server_version import ServerVersion
from .system.config_endpoints import ConfigEndpoints
from .system.system_endpoints import SystemAlphaEndpoints
from .topological_lp.topological_lp_endpoints import TopologicalLPEndpoints

"""
This class should inherit endpoint classes that only contain endpoints that can be called directly from
the `gds` namespace. Example of such endpoints are: "graph" and "list".
"""


class AlphaEndpoints(
    AlgoEndpoints,
    GraphAlphaEndpoints,
    PipelineAlphaEndpoints,
    TopologicalLPEndpoints,
    ModelAlphaEndpoints,
    SingleModeAlgoEndpoints,
    SystemAlphaEndpoints,
    ConfigEndpoints,
):
    def __init__(self, query_runner: QueryRunner, namespace: str, server_version: ServerVersion):
        super().__init__(query_runner, namespace, server_version)

    def __getattr__(self, attr: str) -> CallBuilder:
        return CallBuilder(self._query_runner, f"{self._namespace}.{attr}", self._server_version)
