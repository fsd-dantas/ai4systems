"""Shared domain model / Modelo de dominio compartilhado."""

from aisg.domain.topology import (
    LINK_TYPES,
    MAX_SPEED_M_PER_MS,
    Link,
    LinkType,
    Node,
    Topology,
    TopologyError,
    load_default_topology,
)

__all__ = [
    "LINK_TYPES",
    "MAX_SPEED_M_PER_MS",
    "Link",
    "LinkType",
    "Node",
    "Topology",
    "TopologyError",
    "load_default_topology",
]
