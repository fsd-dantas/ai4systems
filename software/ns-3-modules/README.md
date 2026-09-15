# ns-3 — backhaul em duplo acesso / dual-homed backhaul

Programa ns-3 que constrói o backhaul multi-RAT declarado na topologia: uma cadeia de repetidores armazena-e-encaminha em 900 MHz e uma rede LTE privativa alcançando os mesmos roteadores de borda, cada um ligado por cabo a um rádio remoto e a um CPE.

ns-3 program that builds the multi-RAT backhaul declared in the topology: a 900 MHz store-and-forward relay chain and a private LTE network reaching the same edge routers, each wired to one remote radio and one CPE.

Testado com / tested with **ns-3.48**. Cenário e parâmetros sintéticos e nominais. / Synthetic scenario, nominal parameters.

## Modelo / Model

| Elemento / Element | ns-3 | Parâmetros / Parameters |
|---|---|---|
| Fibra / Fibre | `PointToPoint` | taxa nominal; atraso = distância / 2·10⁸ m/s / nominal rate; delay = distance / 2·10⁸ m/s |
| Rádio 900 MHz armazena-e-encaminha / 900 MHz store-and-forward radio | `PointToPoint` + `DropTailQueue` + `RateErrorModel` | taxa nominal; atraso = propagação + sobrecarga do modelo de custo; PER do orçamento de enlace / nominal rate; delay = propagation + cost-model overhead; PER from the link budget |
| Cabo até o roteador de borda / Cable to the edge router | `PointToPoint` | 100 Mbps |
| LTE privativo / Private LTE | `LteHelper` + `PointToPointEpcHelper`, Okumura-Hata | banda 31 (465 MHz DL), 5 MHz / band 31 (465 MHz DL), 5 MHz |
| Repetidores LTE / LTE relays | modelados como eNodeBs / modelled as eNodeBs | o ns-3 não implementa repetidores LTE / ns-3 implements no LTE relays |
| Roteador atrás do CPE / Router behind the CPE | túnel UDP NOC ↔ CPE (`VirtualNetDevice`) / NOC ↔ CPE UDP tunnel | o PGW só entrega tráfego a endereços de UE / the PGW only delivers to UE addresses |
| Tráfego / Traffic | sockets UDP / UDP sockets | SCADA pedido/resposta a partir do NOC; telemetria periódica do site / SCADA request/response from the NOC; periodic site telemetry |

Endereços de serviço sintéticos / synthetic service addresses: NOC `10.255.0.1`, site *k* `172.16.k.1`.

## Execução / Run

```bash
# 1. exportar o cenário / export the scenario (Windows ou Linux / Windows or Linux)
aisg ns3-export --out experiments/004-multi-rat-simulation/configuration/dual-homed-60.scn

# 2. no ns-3 (WSL/Linux) / in ns-3 (WSL/Linux)
cd ~/ns-allinone-3.48/ns-3.48
patch -p1 < /path/to/ai4systems/software/ns-3-modules/patches/lte-band-31.patch
ln -sfn /path/to/ai4systems/software/ns-3-modules/dual-homed-backhaul scratch/dual-homed-backhaul
./ns3 build dual-homed-backhaul

# 3. executar / run
./ns3 run "dual-homed-backhaul --scenario=/path/to/dual-homed-60.scn --outDir=/path/to/results"
```

Sem o patch da banda 31, use / without the band 31 patch, use `--earfcnDl=2525 --earfcnUl=20525` (banda 5 / band 5).

## Saídas / Outputs

| Arquivo / File | Conteúdo / Contents |
|---|---|
| `sites.csv` | por site: meio primário, pedidos SCADA enviados/recebidos, perda, RTT médio e máximo, telemetria / per site: primary medium, SCADA requests sent/received, loss, mean and max RTT, telemetry |
| `flowmon.xml` | FlowMonitor por fluxo / per-flow FlowMonitor |
| `animation.xml` | traço NetAnim, com `--animate` / NetAnim trace, with `--animate` |

## Limites / Limits

- Remotos sob o mesmo repetidor não disputam o meio: cada salto de rádio é um enlace dedicado. / Remote radios under the same relay do not contend for airtime: each radio hop is a dedicated link.
- Sem MAC proprietário nem modulação adaptativa; retransmissão de enlace não é modelada quadro a quadro. / No proprietary MAC or adaptive modulation; link-layer retransmission is not modelled frame by frame.
- O orçamento de enlace é nominal (log-distância, BPSK) e serve para parametrizar, não para prever um rádio real. / The link budget is nominal (log-distance, BPSK) and parameterises the model; it does not predict a real radio.
