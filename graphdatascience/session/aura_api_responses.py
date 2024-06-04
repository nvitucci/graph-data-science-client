from __future__ import annotations

import dataclasses
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, NamedTuple, Optional, Set


@dataclass(repr=True, frozen=True)
class SessionDetails:
    id: str
    name: str
    instance_id: str
    memory: str
    status: str
    host: Optional[str]
    expiry_date: Optional[datetime]
    created_at: datetime

    @classmethod
    def fromJson(cls, json: Dict[str, Any]) -> SessionDetails:
        expiry_date = json.get("expiry_date")

        return cls(
            id=json["id"],
            name=json["name"],
            instance_id=json["instance_id"],
            memory=json["memory"],
            status=json["status"],
            host=json.get("host"),
            expiry_date=TimeParser.fromisoformat(expiry_date) if expiry_date else None,
            created_at=TimeParser.fromisoformat(json["created_at"]),
        )

    def bolt_connection_url(self) -> str:
        return f"neo4j+ssc://{self.host}"  # TODO use neo4j+s


@dataclass(repr=True, frozen=True)
class InstanceDetails:
    id: str
    name: str
    tenant_id: str
    cloud_provider: str

    @classmethod
    def fromJson(cls, json: Dict[str, Any]) -> InstanceDetails:
        return cls(
            id=json["id"],
            name=json["name"],
            tenant_id=json["tenant_id"],
            cloud_provider=json["cloud_provider"],
        )


@dataclass(repr=True, frozen=True)
class InstanceSpecificDetails(InstanceDetails):
    status: str
    connection_url: str
    memory: str
    type: str
    region: str

    @classmethod
    def fromJson(cls, json: Dict[str, Any]) -> InstanceSpecificDetails:
        return cls(
            id=json["id"],
            name=json["name"],
            tenant_id=json["tenant_id"],
            cloud_provider=json["cloud_provider"],
            status=json["status"],
            connection_url=json.get("connection_url", ""),
            memory=json.get("memory", ""),
            type=json["type"],
            region=json["region"],
        )


@dataclass(repr=True, frozen=True)
class InstanceCreateDetails:
    id: str
    username: str
    password: str
    connection_url: str

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> InstanceCreateDetails:
        fields = dataclasses.fields(cls)
        if any(f.name not in json for f in fields):
            raise RuntimeError(f"Missing required field. Expected `{[f.name for f in fields]}` but got `{json}`")

        return cls(**{f.name: json[f.name] for f in fields})


@dataclass(repr=True, frozen=True)
class EstimationDetails:
    min_required_memory: str
    recommended_size: str
    did_exceed_maximum: bool

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> EstimationDetails:
        fields = dataclasses.fields(cls)
        if any(f.name not in json for f in fields):
            raise RuntimeError(f"Missing required field. Expected `{[f.name for f in fields]}` but got `{json}`")

        return cls(**{f.name: json[f.name] for f in fields})


class WaitResult(NamedTuple):
    connection_url: str
    error: str

    @classmethod
    def from_error(cls, error: str) -> WaitResult:
        return cls(connection_url="", error=error)

    @classmethod
    def from_connection_url(cls, connection_url: str) -> WaitResult:
        return cls(connection_url=connection_url, error="")


@dataclass(repr=True, frozen=True)
class TenantDetails:
    id: str
    ds_type: str
    regions_per_provider: Dict[str, Set[str]]

    @classmethod
    def from_json(cls, json: Dict[str, Any]) -> TenantDetails:
        regions_per_provider = defaultdict(set)
        instance_types = set()
        ds_type = None

        for configs in json["instance_configurations"]:
            type = configs["type"]
            if type.split("-")[1] == "ds":
                regions_per_provider[configs["cloud_provider"]].add(configs["region"])
                ds_type = type
            instance_types.add(configs["type"])

        id = json["id"]
        if not ds_type:
            raise RuntimeError(
                f"Tenant with id `{id}` cannot create DS instances. Available instances are `{instance_types}`."
            )

        return cls(
            id=id,
            ds_type=ds_type,
            regions_per_provider=regions_per_provider,
        )


# datetime.fromisoformat only works with Python version > 3.9
class TimeParser:

    @staticmethod
    def fromisoformat(date: str) -> datetime:
        if sys.version_info >= (3, 11):
            return datetime.fromisoformat(date)
        else:
            # Aura API example: 1970-01-01T00:00:00Z
            return datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
