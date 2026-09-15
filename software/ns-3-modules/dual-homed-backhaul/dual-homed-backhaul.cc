/*
 * SPDX-License-Identifier: MIT
 *
 * Dual-homed smart-grid backhaul: a 900 MHz store-and-forward chain and a
 * private LTE network reach the same edge routers.
 *
 * The network is read from a scenario file exported by `aisg ns3-export`; this
 * program only builds what the file declares. Everything is synthetic and every
 * parameter is nominal.
 *
 * Model summary
 *   - fibre, wired and 900 MHz hops: point-to-point links; radio hops carry a
 *     packet error model and a finite store-and-forward queue
 *   - private LTE: ns-3 LTE + EPC; each CPE is a UE
 *   - an edge router behind a CPE is reached through a NOC <-> CPE UDP tunnel,
 *     because the PGW only delivers downlink traffic to UE addresses
 *   - service addresses: NOC 10.255.0.1, site k 172.16.k.1 (on the loopback)
 *   - traffic per site: SCADA request/response polled from the NOC, and
 *     periodic telemetry from the edge router
 */

#include "ns3/core-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/internet-module.h"
#include "ns3/lte-module.h"
#include "ns3/mobility-module.h"
#include "ns3/netanim-module.h"
#include "ns3/network-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/propagation-module.h"
#include "ns3/system-path.h"
#include "ns3/virtual-net-device.h"

#include <algorithm>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <map>
#include <memory>
#include <sstream>
#include <string>
#include <vector>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE("AisgDualHomedBackhaul");

namespace
{

const Ipv4Address kNocService("10.255.0.1");
const uint16_t kScadaPort = 5000;
const uint16_t kTelemetryPort = 6000;
const uint16_t kTelemetrySourcePort = 6001;

// ---------------------------------------------------------------------------
// scenario file
// ---------------------------------------------------------------------------
struct NodeSpec
{
    std::string id;
    std::string role;
    double x;
    double y;
};

struct LinkSpec
{
    std::string id;
    std::string a;
    std::string b;
    std::string cls;
    std::string rate;
    double delayMs;
    double per;
    std::string network;
    std::string rssi;
    std::string snr;
};

struct SiteSpec
{
    std::string er;
    std::string rm;
    std::string cpe;
    std::string primary;
    uint32_t index;
};

struct RouteSpec
{
    std::string node;
    std::string dest;
    std::string via;
};

struct Scenario
{
    std::map<std::string, std::string> params;
    std::vector<NodeSpec> nodes;
    std::vector<LinkSpec> links;
    std::vector<std::pair<std::string, std::string>> attachments;
    std::vector<SiteSpec> sites;
    std::vector<RouteSpec> routes;

    std::string Param(const std::string& name) const
    {
        auto it = params.find(name);
        NS_ABORT_MSG_IF(it == params.end(), "scenario is missing param " << name);
        return it->second;
    }

    double Number(const std::string& name) const
    {
        return std::stod(Param(name));
    }
};

Scenario
LoadScenario(const std::string& path)
{
    std::ifstream in(path);
    NS_ABORT_MSG_IF(!in, "cannot open scenario file " << path);
    Scenario s;
    std::string line;
    bool header = false;
    uint32_t number = 0;
    while (std::getline(in, line))
    {
        ++number;
        if (!line.empty() && line.back() == '\r')
        {
            line.pop_back();
        }
        auto hash = line.find('#');
        if (hash != std::string::npos)
        {
            line = line.substr(0, hash);
        }
        std::istringstream ss(line);
        std::string kind;
        if (!(ss >> kind))
        {
            continue;
        }
        if (!header)
        {
            std::string version;
            ss >> version;
            NS_ABORT_MSG_IF(kind != "aisg-ns3-scenario" || version != "1",
                            "unsupported scenario format at line " << number);
            header = true;
            continue;
        }
        if (kind == "param")
        {
            std::string name;
            std::string value;
            ss >> name >> value;
            s.params[name] = value;
        }
        else if (kind == "node")
        {
            NodeSpec n;
            ss >> n.id >> n.role >> n.x >> n.y;
            s.nodes.push_back(n);
        }
        else if (kind == "p2p")
        {
            LinkSpec l;
            ss >> l.id >> l.a >> l.b >> l.cls >> l.rate >> l.delayMs >> l.per >> l.network >>
                l.rssi >> l.snr;
            s.links.push_back(l);
        }
        else if (kind == "attach")
        {
            std::string cpe;
            std::string enb;
            ss >> cpe >> enb;
            s.attachments.emplace_back(cpe, enb);
        }
        else if (kind == "site")
        {
            SiteSpec site;
            ss >> site.er >> site.rm >> site.cpe >> site.primary >> site.index;
            s.sites.push_back(site);
        }
        else if (kind == "route")
        {
            RouteSpec r;
            ss >> r.node >> r.dest >> r.via;
            s.routes.push_back(r);
        }
        else
        {
            NS_ABORT_MSG("unknown record '" << kind << "' at line " << number);
        }
        NS_ABORT_MSG_IF(ss.fail(), "malformed '" << kind << "' record at line " << number);
    }
    NS_ABORT_MSG_IF(!header, "scenario file " << path << " is empty");
    return s;
}

Ipv4Address
Dotted(const std::string& prefix, uint32_t index, const std::string& suffix)
{
    std::ostringstream out;
    out << prefix << index << suffix;
    return Ipv4Address(out.str().c_str());
}

// ---------------------------------------------------------------------------
// payloads
// ---------------------------------------------------------------------------
Ptr<Packet>
MakePayload(uint32_t sequence, uint32_t size)
{
    std::vector<uint8_t> buffer(std::max<uint32_t>(size, 4), 0);
    buffer[0] = static_cast<uint8_t>(sequence >> 24);
    buffer[1] = static_cast<uint8_t>(sequence >> 16);
    buffer[2] = static_cast<uint8_t>(sequence >> 8);
    buffer[3] = static_cast<uint8_t>(sequence);
    return Create<Packet>(buffer.data(), buffer.size());
}

uint32_t
ReadSequence(Ptr<const Packet> packet)
{
    uint8_t b[4] = {0, 0, 0, 0};
    packet->CopyData(b, 4);
    return (uint32_t(b[0]) << 24) | (uint32_t(b[1]) << 16) | (uint32_t(b[2]) << 8) | b[3];
}

// ---------------------------------------------------------------------------
// NOC <-> CPE tunnels
// ---------------------------------------------------------------------------
class TunnelHub
{
  public:
    TunnelHub(Ptr<Node> noc, uint16_t port)
    {
        m_socket = Socket::CreateSocket(noc, UdpSocketFactory::GetTypeId());
        m_socket->Bind(InetSocketAddress(Ipv4Address::GetAny(), port));
        m_socket->SetRecvCallback(MakeCallback(&TunnelHub::OnReceive, this));
    }

    Ptr<Socket> GetSocket() const
    {
        return m_socket;
    }

    void Register(Ipv4Address ueAddress, Ptr<VirtualNetDevice> tap)
    {
        m_tapByUe[ueAddress] = tap;
    }

  private:
    void OnReceive(Ptr<Socket> socket)
    {
        Address from;
        Ptr<Packet> packet;
        while ((packet = socket->RecvFrom(from)))
        {
            auto it = m_tapByUe.find(InetSocketAddress::ConvertFrom(from).GetIpv4());
            if (it != m_tapByUe.end())
            {
                it->second->Receive(packet,
                                    0x0800,
                                    it->second->GetAddress(),
                                    it->second->GetAddress(),
                                    NetDevice::PACKET_HOST);
            }
        }
    }

    Ptr<Socket> m_socket;
    std::map<Ipv4Address, Ptr<VirtualNetDevice>> m_tapByUe;
};

class SiteTunnel
{
  public:
    SiteTunnel(TunnelHub& hub,
               Ptr<Node> noc,
               Ptr<Node> cpe,
               Ipv4Address ueAddress,
               Ipv4Address nocOuterAddress,
               uint32_t index,
               uint16_t port)
        : m_hubSocket(hub.GetSocket()),
          m_ueAddress(ueAddress),
          m_nocOuterAddress(nocOuterAddress),
          m_port(port)
    {
        m_nocInner = Dotted("11.", index, ".0.1");
        m_cpeInner = Dotted("11.", index, ".0.2");

        m_nocTap = CreateObject<VirtualNetDevice>();
        m_nocTap->SetAddress(Mac48Address::Allocate());
        m_nocTap->SetSendCallback(MakeCallback(&SiteTunnel::NocSend, this));
        noc->AddDevice(m_nocTap);
        Ptr<Ipv4> nocIp = noc->GetObject<Ipv4>();
        m_nocInterface = nocIp->AddInterface(m_nocTap);
        nocIp->AddAddress(m_nocInterface,
                          Ipv4InterfaceAddress(m_nocInner, Ipv4Mask("255.255.255.252")));
        nocIp->SetUp(m_nocInterface);

        m_cpeTap = CreateObject<VirtualNetDevice>();
        m_cpeTap->SetAddress(Mac48Address::Allocate());
        m_cpeTap->SetSendCallback(MakeCallback(&SiteTunnel::CpeSend, this));
        cpe->AddDevice(m_cpeTap);
        Ptr<Ipv4> cpeIp = cpe->GetObject<Ipv4>();
        m_cpeInterface = cpeIp->AddInterface(m_cpeTap);
        cpeIp->AddAddress(m_cpeInterface,
                          Ipv4InterfaceAddress(m_cpeInner, Ipv4Mask("255.255.255.252")));
        cpeIp->SetUp(m_cpeInterface);

        m_cpeSocket = Socket::CreateSocket(cpe, UdpSocketFactory::GetTypeId());
        m_cpeSocket->Bind(InetSocketAddress(Ipv4Address::GetAny(), port));
        m_cpeSocket->SetRecvCallback(MakeCallback(&SiteTunnel::CpeReceive, this));

        hub.Register(ueAddress, m_nocTap);
    }

    uint32_t NocInterface() const
    {
        return m_nocInterface;
    }

    uint32_t CpeInterface() const
    {
        return m_cpeInterface;
    }

    Ipv4Address NocInner() const
    {
        return m_nocInner;
    }

    Ipv4Address CpeInner() const
    {
        return m_cpeInner;
    }

  private:
    bool NocSend(Ptr<Packet> packet, const Address&, const Address&, uint16_t)
    {
        m_hubSocket->SendTo(packet, 0, InetSocketAddress(m_ueAddress, m_port));
        return true;
    }

    bool CpeSend(Ptr<Packet> packet, const Address&, const Address&, uint16_t)
    {
        m_cpeSocket->SendTo(packet, 0, InetSocketAddress(m_nocOuterAddress, m_port));
        return true;
    }

    void CpeReceive(Ptr<Socket> socket)
    {
        Ptr<Packet> packet;
        while ((packet = socket->Recv()))
        {
            m_cpeTap->Receive(packet,
                              0x0800,
                              m_cpeTap->GetAddress(),
                              m_cpeTap->GetAddress(),
                              NetDevice::PACKET_HOST);
        }
    }

    Ptr<Socket> m_hubSocket;
    Ptr<Socket> m_cpeSocket;
    Ptr<VirtualNetDevice> m_nocTap;
    Ptr<VirtualNetDevice> m_cpeTap;
    Ipv4Address m_ueAddress;
    Ipv4Address m_nocOuterAddress;
    Ipv4Address m_nocInner;
    Ipv4Address m_cpeInner;
    uint32_t m_nocInterface{0};
    uint32_t m_cpeInterface{0};
    uint16_t m_port;
};

// ---------------------------------------------------------------------------
// traffic
// ---------------------------------------------------------------------------
struct TrafficConfig
{
    Time start;
    Time stop;
    Time scadaInterval;
    Time telemetryInterval;
    uint32_t requestBytes;
    uint32_t responseBytes;
    uint32_t telemetryBytes;
};

class SiteTraffic
{
  public:
    SiteTraffic(const SiteSpec& spec,
                Ipv4Address siteAddress,
                Ptr<Node> noc,
                Ptr<Node> er,
                const TrafficConfig& config)
        : m_spec(spec),
          m_address(siteAddress),
          m_config(config)
    {
        m_nocPoll = Socket::CreateSocket(noc, UdpSocketFactory::GetTypeId());
        m_nocPoll->Bind(InetSocketAddress(kNocService, static_cast<uint16_t>(20000 + spec.index)));
        m_nocPoll->SetRecvCallback(MakeCallback(&SiteTraffic::OnReply, this));

        m_erResponder = Socket::CreateSocket(er, UdpSocketFactory::GetTypeId());
        m_erResponder->Bind(InetSocketAddress(m_address, kScadaPort));
        m_erResponder->SetRecvCallback(MakeCallback(&SiteTraffic::OnRequest, this));

        m_erTelemetry = Socket::CreateSocket(er, UdpSocketFactory::GetTypeId());
        m_erTelemetry->Bind(InetSocketAddress(m_address, kTelemetrySourcePort));

        // Stagger the sites so their packets do not all leave in the same instant.
        Simulator::Schedule(config.start + MilliSeconds(37 * spec.index % 1000),
                            &SiteTraffic::Poll,
                            this);
        Simulator::Schedule(config.start + MilliSeconds(53 * spec.index % 1000),
                            &SiteTraffic::SendTelemetry,
                            this);
    }

    const SiteSpec& Spec() const
    {
        return m_spec;
    }

    Ipv4Address ServiceAddress() const
    {
        return m_address;
    }

    void CountTelemetry()
    {
        ++m_telemetryReceived;
    }

    void WriteCsvRow(std::ostream& out) const
    {
        double loss = m_scadaSent ? 100.0 * (m_scadaSent - m_scadaReceived) / m_scadaSent : 0.0;
        double mean = m_scadaReceived ? m_rttSumMs / m_scadaReceived : 0.0;
        out << m_spec.index << ',' << m_spec.er << ',' << m_spec.primary << ',' << m_scadaSent
            << ',' << m_scadaReceived << ',' << std::fixed << std::setprecision(2) << loss << ','
            << mean << ',' << m_rttMaxMs << ',' << m_telemetrySent << ',' << m_telemetryReceived
            << '\n';
        out.unsetf(std::ios::fixed);
    }

  private:
    void Poll()
    {
        if (Simulator::Now() >= m_config.stop)
        {
            return;
        }
        m_pending[m_sequence] = Simulator::Now();
        m_nocPoll->SendTo(MakePayload(m_sequence, m_config.requestBytes),
                          0,
                          InetSocketAddress(m_address, kScadaPort));
        ++m_sequence;
        ++m_scadaSent;
        Simulator::Schedule(m_config.scadaInterval, &SiteTraffic::Poll, this);
    }

    void OnRequest(Ptr<Socket> socket)
    {
        Address from;
        Ptr<Packet> packet;
        while ((packet = socket->RecvFrom(from)))
        {
            if (packet->GetSize() >= 4)
            {
                socket->SendTo(MakePayload(ReadSequence(packet), m_config.responseBytes), 0, from);
            }
        }
    }

    void OnReply(Ptr<Socket> socket)
    {
        Ptr<Packet> packet;
        while ((packet = socket->Recv()))
        {
            auto it = m_pending.find(ReadSequence(packet));
            if (it == m_pending.end())
            {
                continue;
            }
            double rtt = (Simulator::Now() - it->second).GetSeconds() * 1e3;
            m_pending.erase(it);
            ++m_scadaReceived;
            m_rttSumMs += rtt;
            m_rttMaxMs = std::max(m_rttMaxMs, rtt);
        }
    }

    void SendTelemetry()
    {
        if (Simulator::Now() >= m_config.stop)
        {
            return;
        }
        ++m_telemetrySent;
        m_erTelemetry->SendTo(MakePayload(m_telemetrySent, m_config.telemetryBytes),
                              0,
                              InetSocketAddress(kNocService, kTelemetryPort));
        Simulator::Schedule(m_config.telemetryInterval, &SiteTraffic::SendTelemetry, this);
    }

    SiteSpec m_spec;
    Ipv4Address m_address;
    TrafficConfig m_config;
    Ptr<Socket> m_nocPoll;
    Ptr<Socket> m_erResponder;
    Ptr<Socket> m_erTelemetry;
    uint32_t m_sequence{0};
    std::map<uint32_t, Time> m_pending;
    uint64_t m_scadaSent{0};
    uint64_t m_scadaReceived{0};
    uint64_t m_telemetrySent{0};
    uint64_t m_telemetryReceived{0};
    double m_rttSumMs{0.0};
    double m_rttMaxMs{0.0};
};

class TelemetrySink
{
  public:
    TelemetrySink(Ptr<Node> noc)
    {
        m_socket = Socket::CreateSocket(noc, UdpSocketFactory::GetTypeId());
        m_socket->Bind(InetSocketAddress(kNocService, kTelemetryPort));
        m_socket->SetRecvCallback(MakeCallback(&TelemetrySink::OnReceive, this));
    }

    void Register(SiteTraffic* site)
    {
        m_siteByAddress[site->ServiceAddress()] = site;
    }

  private:
    void OnReceive(Ptr<Socket> socket)
    {
        Address from;
        Ptr<Packet> packet;
        while ((packet = socket->RecvFrom(from)))
        {
            auto it = m_siteByAddress.find(InetSocketAddress::ConvertFrom(from).GetIpv4());
            if (it != m_siteByAddress.end())
            {
                it->second->CountTelemetry();
            }
        }
    }

    Ptr<Socket> m_socket;
    std::map<Ipv4Address, SiteTraffic*> m_siteByAddress;
};

// ---------------------------------------------------------------------------
// building blocks
// ---------------------------------------------------------------------------
struct Endpoint
{
    uint32_t interface;
    Ipv4Address address;
};

double
HeightFor(const std::string& role)
{
    if (role == "enb")
    {
        return 30.0;
    }
    if (role == "cpe" || role == "rm")
    {
        return 6.0;
    }
    return 10.0;
}

void
AddServiceAddress(Ptr<Node> node, Ipv4Address address)
{
    // Interface 0 is the loopback. With the weak end-system model, a packet
    // arriving on any interface is delivered locally when its destination is
    // any of the node's addresses, so the service address is reachable over
    // either access network.
    node->GetObject<Ipv4>()->AddAddress(
        0,
        Ipv4InterfaceAddress(address, Ipv4Mask("255.255.255.255")));
}

} // namespace

int
main(int argc, char* argv[])
{
    std::string scenarioPath;
    std::string outDir = "aisg-ns3-output";
    double simTimeOverride = 0.0;
    uint32_t earfcnDlOverride = 0;
    uint32_t earfcnUlOverride = 0;
    bool animate = false;

    CommandLine cmd(__FILE__);
    cmd.AddValue("scenario", "scenario file exported by `aisg ns3-export`", scenarioPath);
    cmd.AddValue("outDir", "directory for results", outDir);
    cmd.AddValue("simTime", "override the simulated time, in seconds", simTimeOverride);
    cmd.AddValue("earfcnDl", "override the LTE downlink EARFCN", earfcnDlOverride);
    cmd.AddValue("earfcnUl", "override the LTE uplink EARFCN", earfcnUlOverride);
    cmd.AddValue("animate", "write a NetAnim trace", animate);
    cmd.Parse(argc, argv);
    NS_ABORT_MSG_IF(scenarioPath.empty(), "--scenario is required");

    Scenario scenario = LoadScenario(scenarioPath);
    SystemPath::MakeDirectories(outDir);
    double simTime = simTimeOverride > 0 ? simTimeOverride : scenario.Number("sim_time_s");

    // --- LTE configuration (before any LTE object exists) -------------------
    uint32_t earfcnDl = earfcnDlOverride ? earfcnDlOverride
                                         : static_cast<uint32_t>(scenario.Number("lte_earfcn_dl"));
    uint32_t earfcnUl = earfcnUlOverride ? earfcnUlOverride
                                         : static_cast<uint32_t>(scenario.Number("lte_earfcn_ul"));
    auto bandwidth = static_cast<uint16_t>(scenario.Number("lte_bandwidth_rb"));
    Config::SetDefault("ns3::LteEnbNetDevice::DlEarfcn", UintegerValue(earfcnDl));
    Config::SetDefault("ns3::LteEnbNetDevice::UlEarfcn", UintegerValue(earfcnUl));
    Config::SetDefault("ns3::LteUeNetDevice::DlEarfcn", UintegerValue(earfcnDl));
    Config::SetDefault("ns3::LteEnbNetDevice::DlBandwidth", UintegerValue(bandwidth));
    Config::SetDefault("ns3::LteEnbNetDevice::UlBandwidth", UintegerValue(bandwidth));
    Config::SetDefault("ns3::LteEnbPhy::TxPower", DoubleValue(scenario.Number("enb_tx_power_dbm")));
    Config::SetDefault("ns3::LteUePhy::TxPower", DoubleValue(scenario.Number("ue_tx_power_dbm")));

    Ptr<LteHelper> lteHelper = CreateObject<LteHelper>();
    Ptr<PointToPointEpcHelper> epcHelper = CreateObject<PointToPointEpcHelper>();
    lteHelper->SetEpcHelper(epcHelper);
    lteHelper->SetAttribute("PathlossModel", StringValue("ns3::OkumuraHataPropagationLossModel"));
    lteHelper->SetPathlossModelAttribute("Frequency",
                                         DoubleValue(scenario.Number("lte_dl_frequency_hz")));
    lteHelper->SetPathlossModelAttribute("Environment", EnumValue(SubUrbanEnvironment));
    lteHelper->SetPathlossModelAttribute("CitySize", EnumValue(SmallCity));

    // --- nodes -------------------------------------------------------------
    std::map<std::string, Ptr<Node>> nodes;
    std::map<std::string, std::string> roles;
    NodeContainer enbNodes;
    NodeContainer cpeNodes;
    NodeContainer ipNodes;
    for (const auto& spec : scenario.nodes)
    {
        Ptr<Node> node = CreateObject<Node>();
        nodes[spec.id] = node;
        roles[spec.id] = spec.role;
        Ptr<ConstantPositionMobilityModel> position =
            CreateObject<ConstantPositionMobilityModel>();
        position->SetPosition(Vector(spec.x, spec.y, HeightFor(spec.role)));
        node->AggregateObject(position);
        if (spec.role == "enb")
        {
            enbNodes.Add(node);
        }
        else
        {
            ipNodes.Add(node);
            if (spec.role == "cpe")
            {
                cpeNodes.Add(node);
            }
        }
    }
    auto node = [&nodes](const std::string& id) {
        auto it = nodes.find(id);
        NS_ABORT_MSG_IF(it == nodes.end(), "unknown node " << id);
        return it->second;
    };
    Ptr<Node> noc;
    for (const auto& [id, role] : roles)
    {
        if (role == "noc")
        {
            noc = nodes[id];
        }
    }
    NS_ABORT_MSG_IF(!noc, "scenario declares no NOC");

    InternetStackHelper internet;
    internet.Install(ipNodes);

    // --- fibre, wired and 900 MHz links ---------------------------------------
    std::map<std::pair<std::string, std::string>, std::pair<Endpoint, Endpoint>> adjacency;
    std::map<std::string, Ptr<RateErrorModel>> radioErrorModels;
    std::string radioQueue = scenario.Param("radio_queue_packets") + "p";
    for (const auto& link : scenario.links)
    {
        PointToPointHelper p2p;
        p2p.SetDeviceAttribute("DataRate", DataRateValue(DataRate(link.rate)));
        p2p.SetChannelAttribute("Delay",
                                TimeValue(MicroSeconds(std::llround(link.delayMs * 1000.0))));
        if (link.cls == "radio")
        {
            p2p.SetQueue("ns3::DropTailQueue<Packet>", "MaxSize", StringValue(radioQueue));
        }
        NetDeviceContainer devices = p2p.Install(node(link.a), node(link.b));
        if (link.cls == "radio")
        {
            for (uint32_t i = 0; i < 2; ++i)
            {
                Ptr<RateErrorModel> em = CreateObject<RateErrorModel>();
                em->SetUnit(RateErrorModel::ERROR_UNIT_PACKET);
                em->SetRate(link.per);
                DynamicCast<PointToPointNetDevice>(devices.Get(i))->SetReceiveErrorModel(em);
                radioErrorModels[link.id + "@" + (i == 0 ? link.a : link.b)] = em;
            }
        }
        Ipv4AddressHelper addresses;
        addresses.SetBase(Ipv4Address(link.network.c_str()), Ipv4Mask("255.255.255.0"));
        Ipv4InterfaceContainer interfaces = addresses.Assign(devices);
        Endpoint ea{interfaces.Get(0).second, interfaces.GetAddress(0)};
        Endpoint eb{interfaces.Get(1).second, interfaces.GetAddress(1)};
        adjacency[{link.a, link.b}] = {ea, eb};
        adjacency[{link.b, link.a}] = {eb, ea};
    }

    // --- service addresses ---------------------------------------------------
    AddServiceAddress(noc, kNocService);
    std::map<std::string, Ipv4Address> siteAddress;
    std::map<std::string, const SiteSpec*> siteByEr;
    std::map<std::string, const SiteSpec*> siteByCpe;
    for (const auto& site : scenario.sites)
    {
        siteAddress[site.er] = Dotted("172.16.", site.index, ".1");
        siteByEr[site.er] = &site;
        siteByCpe[site.cpe] = &site;
        AddServiceAddress(node(site.er), siteAddress[site.er]);
    }

    // --- private LTE -----------------------------------------------------------
    Ptr<Node> pgw = epcHelper->GetPgwNode();
    PointToPointHelper core;
    core.SetDeviceAttribute("DataRate", DataRateValue(DataRate("10Gbps")));
    core.SetChannelAttribute("Delay", TimeValue(MilliSeconds(1)));
    NetDeviceContainer coreDevices = core.Install(noc, pgw);
    Ipv4AddressHelper coreAddresses;
    coreAddresses.SetBase("10.254.0.0", "255.255.255.0");
    Ipv4InterfaceContainer coreInterfaces = coreAddresses.Assign(coreDevices);
    Ipv4Address nocOuterAddress = coreInterfaces.GetAddress(0);

    Ipv4StaticRoutingHelper routing;
    routing.GetStaticRouting(noc->GetObject<Ipv4>())
        ->AddNetworkRouteTo(Ipv4Address("7.0.0.0"),
                            Ipv4Mask("255.0.0.0"),
                            coreInterfaces.GetAddress(1),
                            coreInterfaces.Get(0).second);

    NetDeviceContainer enbDevices = lteHelper->InstallEnbDevice(enbNodes);
    NetDeviceContainer ueDevices = lteHelper->InstallUeDevice(cpeNodes);
    Ipv4InterfaceContainer ueInterfaces = epcHelper->AssignUeIpv4Address(ueDevices);

    std::map<std::string, Ptr<NetDevice>> enbDeviceById;
    for (uint32_t i = 0; i < enbNodes.GetN(); ++i)
    {
        for (const auto& [id, n] : nodes)
        {
            if (n == enbNodes.Get(i))
            {
                enbDeviceById[id] = enbDevices.Get(i);
            }
        }
    }
    std::map<std::string, Ptr<NetDevice>> ueDeviceById;
    std::map<std::string, Ipv4Address> ueAddressById;
    for (uint32_t i = 0; i < cpeNodes.GetN(); ++i)
    {
        for (const auto& [id, n] : nodes)
        {
            if (n == cpeNodes.Get(i))
            {
                ueDeviceById[id] = ueDevices.Get(i);
                ueAddressById[id] = ueInterfaces.GetAddress(i);
            }
        }
        Ptr<Ipv4> ipv4 = cpeNodes.Get(i)->GetObject<Ipv4>();
        int32_t lteInterface = ipv4->GetInterfaceForDevice(ueDevices.Get(i));
        routing.GetStaticRouting(ipv4)->SetDefaultRoute(epcHelper->GetUeDefaultGatewayAddress(),
                                                        lteInterface);
    }
    for (const auto& [cpe, enb] : scenario.attachments)
    {
        NS_ABORT_MSG_IF(!ueDeviceById.count(cpe) || !enbDeviceById.count(enb),
                        "cannot attach " << cpe << " to " << enb);
        lteHelper->Attach(ueDeviceById[cpe], enbDeviceById[enb]);
    }

    // --- tunnels -----------------------------------------------------------------
    uint16_t tunnelPort = static_cast<uint16_t>(scenario.Number("tunnel_port"));
    TunnelHub hub(noc, tunnelPort);
    std::map<std::string, std::unique_ptr<SiteTunnel>> tunnelByEr;
    for (const auto& site : scenario.sites)
    {
        tunnelByEr[site.er] = std::make_unique<SiteTunnel>(hub,
                                                           noc,
                                                           node(site.cpe),
                                                           ueAddressById.at(site.cpe),
                                                           nocOuterAddress,
                                                           site.index,
                                                           tunnelPort);
    }

    // --- static routes -----------------------------------------------------------
    for (const auto& route : scenario.routes)
    {
        Ptr<Ipv4StaticRouting> table = routing.GetStaticRouting(node(route.node)->GetObject<Ipv4>());
        Ipv4Address dest = route.dest == "noc" ? kNocService : siteAddress.at(route.dest);
        if (route.via == "tunnel")
        {
            if (route.node == "NOC" || roles[route.node] == "noc")
            {
                const SiteTunnel& tunnel = *tunnelByEr.at(route.dest);
                table->AddHostRouteTo(dest, tunnel.CpeInner(), tunnel.NocInterface());
            }
            else
            {
                const SiteSpec* site = siteByCpe.at(route.node);
                const SiteTunnel& tunnel = *tunnelByEr.at(site->er);
                table->AddHostRouteTo(dest, tunnel.NocInner(), tunnel.CpeInterface());
            }
            continue;
        }
        auto it = adjacency.find({route.node, route.via});
        NS_ABORT_MSG_IF(it == adjacency.end(),
                        "route " << route.node << " -> " << route.via << " is not a link");
        table->AddHostRouteTo(dest, it->second.second.address, it->second.first.interface);
    }

    // --- traffic -------------------------------------------------------------------
    TrafficConfig config{Seconds(scenario.Number("traffic_start_s")),
                         Seconds(simTime - 1.0),
                         Seconds(scenario.Number("scada_interval_s")),
                         Seconds(scenario.Number("telemetry_interval_s")),
                         static_cast<uint32_t>(scenario.Number("scada_request_bytes")),
                         static_cast<uint32_t>(scenario.Number("scada_response_bytes")),
                         static_cast<uint32_t>(scenario.Number("telemetry_bytes"))};
    TelemetrySink sink(noc);
    std::vector<std::unique_ptr<SiteTraffic>> traffic;
    for (const auto& site : scenario.sites)
    {
        traffic.push_back(std::make_unique<SiteTraffic>(site,
                                                        siteAddress.at(site.er),
                                                        noc,
                                                        node(site.er),
                                                        config));
        sink.Register(traffic.back().get());
    }

    FlowMonitorHelper flowHelper;
    Ptr<FlowMonitor> monitor = flowHelper.InstallAll();

    std::unique_ptr<AnimationInterface> animation;
    if (animate)
    {
        animation = std::make_unique<AnimationInterface>(outDir + "/animation.xml");
        animation->SetMaxPktsPerTraceFile(500000);
        for (const auto& spec : scenario.nodes)
        {
            animation->UpdateNodeDescription(nodes[spec.id], spec.id);
        }
    }

    NS_LOG_UNCOND("aisg dual-homed backhaul: " << scenario.nodes.size() << " nodes, "
                                               << scenario.links.size() << " point-to-point links, "
                                               << scenario.sites.size() << " sites, "
                                               << simTime << " s simulated");
    Simulator::Stop(Seconds(simTime));
    Simulator::Run();

    monitor->SerializeToXmlFile(outDir + "/flowmon.xml", true, true);
    std::ofstream csv(outDir + "/sites.csv");
    csv << "index,site,primary,scada_sent,scada_received,scada_loss_pct,rtt_mean_ms,rtt_max_ms,"
           "telemetry_sent,telemetry_received\n";
    for (const auto& site : traffic)
    {
        site->WriteCsvRow(csv);
        site->WriteCsvRow(std::cout);
    }
    Simulator::Destroy();
    return 0;
}
