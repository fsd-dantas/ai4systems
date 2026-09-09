"""Shared domain model / Modelo de dominio compartilhado."""

from aisg.domain.topology import (
    BUNDLED_TOPOLOGIES,
    LINK_TYPES,
    MAX_SPEED_M_PER_MS,
    Link,
    LinkType,
    Node,
    Topology,
    TopologyError,
    load_default_topology,
    load_topology,
)

__all__ = [
    "BUNDLED_TOPOLOGIES",
    "LINK_TYPES",
    "MAX_SPEED_M_PER_MS",
    "Link",
    "LinkType",
    "Node",
    "Topology",
    "TopologyError",
    "load_default_topology",
    "load_topology",
]
