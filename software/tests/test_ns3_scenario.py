"""
Tests for the ns-3 scenario exporter.

PT-BR: O exportador e a ponte entre o modelo e o simulador. Os testes asseguram
       que o cenario gerado e um backhaul em duplo acesso consistente: cada site
       ligado por cabo a um radio remoto e a um CPE, cada CPE preso a um
       eNodeB, e rotas estaticas que realmente chegam ao destino salto a salto.
EN:    The exporter is the bridge between the model and the simulator. The tests
       ensure the generated scenario is a consistent dual-homed backhaul: every
       site wired to one remote radio and one CPE, every CPE attached to one
       eNodeB, and static routes that really reach their destination hop by hop.
"""

from __future__ import annotations

import pytest

from aisg.domain import load_topology
from aisg.simulation import (
    FORMAT_HEADER,
    NS3_PARAMETERS,
    ScenarioError,
    build_ns3_scenario,
    radio_link_budget,
)


@pytest.fixture(scope="module")
def topology():
    return load_topology("dual")


@pytest.fixture(scope="module")
def scenario(topology):
    return build_ns3_scenario(topology)


def test_export_is_deterministic(topology):
    assert build_ns3_scenario(topology).render() == build_ns3_scenario(topology).render()


def test_rendered_file_starts_with_the_format_header(scenario):
    assert scenario.render().splitlines()[0] == FORMAT_HEADER


def test_lte_relays_become_enodebs_and_their_backhaul_is_dropped(scenario, topology):
    roles = {nid: role for nid, role, _x, _y in scenario.nodes}
    relays = [n.id for n in topology.nodes.values() if n.kind == "lte_relay"]
    assert relays and all(roles[r] == "enb" for r in relays)
    for link in scenario.links:
        assert "enb" not in (roles[link.a], roles[link.b]), link


def test_every_site_is_wired_to_one_remote_radio_and_one_cpe(scenario):
    roles = {nid: role for nid, role, _x, _y in scenario.nodes}
    assert len(scenario.sites) == 15
    wired = {frozenset((l.a, l.b)) for l in scenario.links if l.cls == "wired"}
    for site in scenario.sites:
        assert roles[site.rm] == "rm" and roles[site.cpe] == "cpe"
        assert frozenset((site.er, site.rm)) in wired
        assert frozenset((site.er, site.cpe)) in wired
        assert site.primary in ("radio900", "plte")


def test_every_cpe_attaches_to_exactly_one_enodeb(scenario):
    roles = {nid: role for nid, role, _x, _y in scenario.nodes}
    cpes = [cpe for cpe, _ in scenario.attachments]
    assert len(cpes) == len(set(cpes)) == 15
    assert all(roles[enb] == "enb" for _, enb in scenario.attachments)


def test_link_networks_are_unique(scenario):
    networks = [link.network for link in scenario.links]
    assert len(networks) == len(set(networks))


def _follow(scenario, start, dest, limit=30):
    links = {frozenset((l.a, l.b)) for l in scenario.links}
    node, hops = start, [start]
    while len(hops) < limit:
        via = scenario.routes.get((node, dest))
        assert via is not None, f"{node} has no route towards {dest}"
        if via == "tunnel":
            return hops + ["tunnel"]
        assert frozenset((node, via)) in links, f"{node} -> {via} is not a link"
        hops.append(via)
        if (dest == "noc" and via == "NOC") or via == dest:
            return hops
        node = via
    raise AssertionError(f"routing loop from {start} towards {dest}: {hops}")


def test_static_routes_reach_every_site_and_back_hop_by_hop(scenario):
    for site in scenario.sites:
        forward = _follow(scenario, "NOC", site.er)
        backward = _follow(scenario, site.er, "noc")
        if site.primary == "radio900":
            assert forward[-1] == site.er and site.rm in forward
            assert backward[1] == site.rm and backward[-1] == "NOC"
        else:
            assert forward == ["NOC", "tunnel"]
            assert backward == [site.er, site.cpe, "tunnel"]
        # the 900 MHz path is always installed, so failover only touches the ends
        assert _follow(scenario, site.rm, "noc")[-1] == "NOC"
        assert scenario.routes[(site.cpe, site.er)] == site.er


def test_packet_error_rates_are_probabilities_and_nominal_radio_is_clean(scenario):
    radio = [l for l in scenario.links if l.cls == "radio"]
    assert radio
    for link in radio:
        assert 0.0 <= link.per < 0.01, link
        assert link.rssi_dbm is not None and link.snr_db is not None


def test_link_budget_degrades_with_distance():
    near = radio_link_budget(2_000, 1.0, 2.7)
    far = radio_link_budget(40_000, 1.0, 2.7)
    very_far = radio_link_budget(400_000, 1.0, 2.7)
    assert near.rssi_dbm > far.rssi_dbm > very_far.rssi_dbm
    assert near.packet_error_rate <= far.packet_error_rate <= very_far.packet_error_rate
    assert very_far.packet_error_rate > 0.5


def test_lte_carrier_is_consistent_with_band_31():
    dl = int(NS3_PARAMETERS["lte_earfcn_dl"])
    ul = int(NS3_PARAMETERS["lte_earfcn_ul"])
    assert 9870 <= dl <= 9919 and 27210 <= ul <= 27259
    dl_mhz = 462.5 + 0.1 * (dl - 9870)
    ul_mhz = 452.5 + 0.1 * (ul - 27210)
    assert dl_mhz * 1e6 == pytest.approx(float(NS3_PARAMETERS["lte_dl_frequency_hz"]))
    assert dl_mhz - ul_mhz == pytest.approx(10.0)


def test_cpe_antenna_is_declared_in_the_rendered_scenario(scenario):
    params = {
        line.split()[1]: line.split()[2]
        for line in scenario.render().splitlines()
        if line.startswith("param ")
    }
    assert float(params["cpe_antenna_max_gain_dbi"]) > 0
    assert 0 < float(params["cpe_antenna_beamwidth_deg"]) < 360


def test_every_site_declares_a_path_on_each_medium(scenario):
    links = {frozenset((l.a, l.b)) for l in scenario.links}
    by_site = {}
    for er, medium, noc_via, er_via in scenario.paths:
        by_site.setdefault(er, {})[medium] = (noc_via, er_via)
    for site in scenario.sites:
        radio_noc, radio_er = by_site[site.er]["radio900"]
        lte_noc, lte_er = by_site[site.er]["plte"]
        assert frozenset(("NOC", radio_noc)) in links and radio_er == site.rm
        assert lte_noc == "tunnel" and lte_er == site.cpe


def test_no_faults_without_a_fault_scenario(scenario):
    assert scenario.faults == [] and scenario.failovers == []
    assert "\nfault " not in scenario.render()


def test_commanded_faults_are_induced(topology):
    saf = build_ns3_scenario(topology, fault_scenario="saf-chain-outage")
    assert [(k, t) for _, k, t, _ in saf.faults] == [("node_down", "SAF_02")]

    dual = build_ns3_scenario(topology, fault_scenario="dual-outage")
    assert sorted(t for _, k, t, _ in dual.faults if k == "node_down") == ["RELAY_5", "SAF_02"]

    independent = build_ns3_scenario(topology, fault_scenario="independent-faults")
    kinds = {(k, t) for _, k, t, _ in independent.faults}
    assert ("flood", "RELAY_5") in kinds
    rm07_links = {l.id for l in independent.links if "RM_07" in (l.a, l.b) and l.cls == "radio"}
    assert {t for k, t in kinds if k == "radio_per"} == rm07_links


def test_central_failover_is_the_blackboard_plan(topology):
    """
    Only medium switches become failovers: isolated sites have nowhere to go,
    and a lost backup medium changes nothing.
    """
    saf = build_ns3_scenario(topology, fault_scenario="saf-chain-outage")
    assert [(er, m) for _, er, m in saf.failovers] == [("ER_06", "plte")]

    dual = build_ns3_scenario(topology, fault_scenario="dual-outage")
    isolated = {"ER_03", "ER_04", "ER_06", "ER_07"}
    assert not isolated & {er for _, er, _ in dual.failovers}

    independent = build_ns3_scenario(topology, fault_scenario="independent-faults")
    # ER_07 holds congested LTE rather than moving onto the interfered RM_07
    assert {(er, m) for _, er, m in independent.failovers} == {
        ("ER_03", "radio900"), ("ER_04", "radio900"),
    }
    fault_time = float(NS3_PARAMETERS["fault_time_s"])
    assert all(t > fault_time for t, _, _ in independent.failovers)


def test_an_unknown_fault_scenario_is_rejected(topology):
    with pytest.raises(ScenarioError):
        build_ns3_scenario(topology, fault_scenario="meteor-strike")


def test_a_topology_without_a_control_centre_is_rejected(topology):
    from aisg.domain.topology import Topology

    raw = {
        "id": "broken", "title_pt": "x", "title_en": "x", "provenance": "test",
        "nodes": [n for n in (
            {"id": nid, "label_pt": nid, "label_en": nid, "kind": node.kind,
             "sector": node.sector, "x": node.x, "y": node.y, "stub": node.stub}
            for nid, node in topology.nodes.items()
        ) if n["kind"] != "control_centre"],
        "links": [
            {"a": l.a, "b": l.b, "type": l.type, "quality": l.quality}
            for l in topology.links if "NOC" not in (l.a, l.b)
        ],
    }
    with pytest.raises(ScenarioError):
        build_ns3_scenario(Topology.from_dict(raw))
