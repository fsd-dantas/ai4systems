"""Build the institutional deck, synchronized script and provenance manifest.

Run from the repository root:
    python docs/presentation/build_academic_deck.py

Edit academic_content.py, then rebuild both deliverables together.
The preserved .baseline.pptx supplies the institutional master and cover artwork.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.util import Inches, Pt

from academic_content import REFERENCES, SLIDES

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
from aisg.domain import load_topology

# The deck is its own template donor: the build strips slides 2..n and the
# cover text, keeping the master, layouts and cover artwork. Git is the
# backup - restore with git checkout if a build is interrupted.
BASELINE = HERE / "mini-systems-presentation.pptx"
OUTPUT = HERE / "mini-systems-presentation.pptx"
SCRIPT = HERE / "mini-systems-presentation-script.md"
MANIFEST = HERE / "presentation-manifest.json"

INK, WINE, BLUE, GREEN = "172235", "8C3041", "274C77", "3E6B5C"
GRAY, PALE, LINE, WHITE = "4D5968", "F0F2F5", "D5DCE4", "FFFFFF"
FONT = "Aptos"


def rgb(value):
    return RGBColor.from_string(value)


def box(slide, x, y, w, h, text, size=21, color=INK, bold=False,
        font=FONT, align=PP_ALIGN.LEFT, name=None):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if name:
        shape.name = name
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    for i, line in enumerate(str(text).split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = 1.08
        p.space_before = p.space_after = Pt(0)
        run = p.add_run()
        run.text = line
        run.font.name = font
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = rgb(color)
    return shape


def rect(slide, x, y, w, h, fill=PALE, border=None, kind=MSO_SHAPE.RECTANGLE):
    shape = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(fill)
    if border:
        shape.line.color.rgb = rgb(border)
        shape.line.width = Pt(0.6)
    else:
        shape.line.fill.background()
    return shape


def line(slide, x1, y1, x2, y2, color=LINE, width=1):
    shape = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    shape.line.color.rgb = rgb(color)
    shape.line.width = Pt(width)
    return shape


def points(slide, items, x=.86, y=3.75, w=11.6, step=.67, size=22):
    for i, item in enumerate(items):
        rect(slide, x, y + i * step + .115, .065, .065, BLUE, kind=MSO_SHAPE.OVAL)
        box(slide, x + .21, y + i * step, w - .21, step - .08, item, size=size)


def takeaway(slide, text):
    rect(slide, .83, 6.23, 11.65, .46, PALE)
    box(slide, 1.01, 6.30, 11.28, .31, text, 13.5, BLUE)


def header(slide, item, number):
    box(slide, .65, .24, 9.5, .22, item["section"], 10, WINE)
    box(slide, 11.7, .25, .98, .22, f"{number:02d} / {len(SLIDES):02d}", 10, GRAY, align=PP_ALIGN.RIGHT)
    box(slide, .65, .55, 11.85, .53, item["title"], 27, bold=True, name=f"slide-title-{number:02d}")
    line(slide, .65, 1.15, 12.68, 1.15, WINE, 1.0)
    if item["source"]:
        box(slide, 2.05, 6.87, 10.2, .25, item["source"], 9.2, GRAY, name="source")


def table(slide, data):
    rows = data["rows"]
    cols = data["headers"]
    available = 4.53 if len(rows) >= 7 else min(4.45, .76 * (len(rows) + 1))
    shape = slide.shapes.add_table(len(rows) + 1, len(cols), Inches(.85), Inches(1.53), Inches(11.75), Inches(available))
    shape.name = "academic-table"
    tab = shape.table
    for col, width in zip(tab.columns, data.get("widths", [11.75 / len(cols)] * len(cols))):
        col.width = Inches(width)
    header_height = .51
    tab.rows[0].height = Inches(header_height)
    for row in list(tab.rows)[1:]:
        row.height = Inches((available - header_height) / len(rows))
    for i, row in enumerate([cols] + rows):
        for j, value in enumerate(row):
            cell = tab.cell(i, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(INK if i == 0 else (PALE if i % 2 == 0 else WHITE))
            cell.margin_left = cell.margin_right = Inches(.09)
            cell.margin_top = cell.margin_bottom = Inches(.06)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tf = cell.text_frame
            tf.clear()
            tf.word_wrap = True
            tf.auto_size = MSO_AUTO_SIZE.NONE
            p = tf.paragraphs[0]
            p.line_spacing = 1.02
            p.space_after = Pt(0)
            r = p.add_run()
            r.text = str(value)
            r.font.name = FONT
            r.font.size = Pt(data.get("size", 18) if i else 16.5)
            r.font.color.rgb = rgb(WHITE if i == 0 else INK)
            r.font.bold = i == 0 or j == 0
    if data.get("takeaway"):
        takeaway(slide, data["takeaway"])


def topology(slide, data):
    t = load_topology("simulated")
    points(slide, data["items"], x=.9, y=1.7, w=4.3, step=1.0, size=20)
    # Editable schematic: layout is normalized to the available space, not a floor plan.
    xs = [n.x for n in t.nodes.values()]
    ys = [n.y for n in t.nodes.values()]
    positions = {n.id: (5.70 + 6.0 * (n.x - min(xs)) / (max(xs) - min(xs)),
                        5.63 - 3.85 * (n.y - min(ys)) / (max(ys) - min(ys)))
                 for n in t.nodes.values()}
    done = set()
    for u in t.nodes:
        for v, _ in t.successors(u):
            key = tuple(sorted((u, v)))
            if key in done:
                continue
            done.add(key)
            line(slide, *positions[u], *positions[v], color="C5CBD3", width=.8)
    for n in t.nodes.values():
        x, y = positions[n.id]
        color = WINE if n.id.startswith("AP_") else (GREEN if n.id.startswith("RM_") else BLUE)
        shape_kind = MSO_SHAPE.OVAL if n.id.startswith("RM_") else MSO_SHAPE.RECTANGLE
        rect(slide, x - .045, y - .045, .09, .09, color, WHITE, shape_kind)
        labelled = {"NOC", "LTE_CORE", "LTE_ENB", "AP_A", "AP_B", "AP_C",
                    "SAF_A1", "FD_A", "FD_B", "FD_C", "RM_A5", "RM_B4", "RM_C4"}
        if n.id in labelled:
            dx = -.71 if n.id in {"SAF_A1", "LTE_CORE"} else .075
            dy = -.19 if n.id == "SAF_A1" else .055
            if n.id == "NOC":
                dx, dy = -.20, -.25
            box(slide, x + dx, y + dy, .87, .24, n.id, 10, color, name="diagram-label")
    box(slide, 5.65, 5.97, 6.30, .2, "AP: acesso · RM: nó remoto · SAF: repetidor · FD: dispositivo", 10, GRAY)
    takeaway(slide, data["takeaway"])


def body(slide, item):
    kind, data = item["kind"], item["content"]
    if kind == "agenda":
        for i, (number, title, detail) in enumerate(data):
            y = 1.47 + i * .675
            color = [BLUE, WINE, GREEN, "A56A24", WINE, BLUE, GRAY][i]
            box(slide, .94, y, .35, .34, number, 18, color, True)
            box(slide, 1.5, y, 4.4, .48, title, 18, color, True)
            box(slide, 6.03, y, 6.2, .48, detail, 17)
            line(slide, 1.5, y + .54, 12.25, y + .54)
    elif kind == "table":
        table(slide, data)
    elif kind == "cards":
        for i, (title, detail) in enumerate(data):
            x = .83 + i * 4.04
            color = [BLUE, WINE, GREEN][i]
            box(slide, x, 1.70, 3.68, .80, title, 22, color, True)
            box(slide, x, 2.78, 3.50, 3.1, detail, 21)
            if i < 2:
                line(slide, x + 3.78, 1.60, x + 3.78, 5.85)
    elif kind == "statement":
        rect(slide, .84, 1.59, .055, 1.65, WINE)
        box(slide, 1.12, 1.61, 11.02, 1.66, data["statement"], 29, WINE, True)
        points(slide, data["items"], y=3.52, step=.73, size=22)
        takeaway(slide, data["takeaway"])
    elif kind == "flow":
        for i, (title, detail) in enumerate(data["steps"]):
            x = .85 + i * 3.0
            rect(slide, x, 1.65, 2.68, 1.55, PALE)
            box(slide, x + .15, 1.84, 2.38, .37, title, 21, [BLUE, WINE, GREEN, BLUE][i], True)
            box(slide, x + .15, 2.33, 2.38, .74, detail, 17)
            if i < 3:
                rect(slide, x + 2.77, 2.19, .16, .23, WINE, kind=MSO_SHAPE.CHEVRON)
        points(slide, data["items"], y=3.58, step=.73, size=21)
        takeaway(slide, data["takeaway"])
    elif kind == "formula":
        formula_lines = len(data["formula"].splitlines())
        height = max(1.15, .5 * formula_lines + .25)
        rect(slide, .85, 1.55, 11.72, height, PALE)
        box(slide, 1.08, 1.72, 11.22, height - .2, data["formula"], 25, BLUE, font="Cambria Math")
        points(slide, data["items"], y=1.88 + height, step=.72, size=21)
        takeaway(slide, data["takeaway"])
    elif kind == "code":
        lines = len(data["code"].splitlines())
        height = max(2.25, lines * .315 + .4)
        rect(slide, .85, 1.5, 11.72, height, PALE)
        box(slide, 1.08, 1.68, 11.22, height - .2, data["code"], 17.5, INK, font="Consolas")
        if data.get("items"):
            points(slide, data["items"], y=1.67 + height, step=.54, size=18.5)
        takeaway(slide, data["takeaway"])
    elif kind == "topology":
        topology(slide, data)
    elif kind == "bars":
        maximum = max(v for _, v in data["values"])
        for i, (label, value) in enumerate(data["values"]):
            y = 1.83 + i * 1.12
            box(slide, .9, y + .12, 2.68, .4, label, 22, bold=True)
            width = 7.08 * value / maximum
            rect(slide, 3.65, y, width, .67, [GRAY, GREEN][i])
            box(slide, 3.80 + width, y + .12, 1.28, .37, f"{value:,}".replace(",", " "), 22, bold=True)
        points(slide, data["items"], y=4.0, step=.58, size=21)
        takeaway(slide, data["takeaway"])
    elif kind == "references":
        for i, (number, text, url) in enumerate(data):
            y = 1.48 + i * .76
            box(slide, .84, y, .43, .3, number, 16, WINE, True)
            shape = box(slide, 1.40, y, 10.92, .66, text, 16)
            for p in shape.text_frame.paragraphs:
                for r in p.runs:
                    r.hyperlink.address = url
        takeaway(slide, "Referências primárias; resultados do projeto reproduzidos pelo script acompanhante.")
    else:
        raise ValueError(kind)


def durations():
    # Rehearsal estimates include diagrams, live demonstrations and discussion.
    values = [0] * len(SLIDES)
    for start, end, seconds in [(1, 2, 120), (3, 10, 600), (11, 24, 1320),
                                (25, 38, 1320), (39, 49, 1200), (50, 53, 480),
                                (54, 55, 180), (56, 57, 180)]:
        weights = [len(SLIDES[i]["speech"].split()) + (110 if SLIDES[i]["cue"].startswith("Executar") else 0)
                   for i in range(start - 1, end)]
        allocations = [round(seconds * w / sum(weights)) for w in weights]
        allocations[-1] += seconds - sum(allocations)
        values[start - 1:end] = allocations
    assert sum(values) == 5400
    return values


def clock(seconds):
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def notes_text(item, number, seconds, start):
    text = (f"SLIDE {number:02d} — {item['title']}\n{item['section']}\n"
            f"Tempo previsto: {clock(seconds)} | Janela: {clock(start)}–{clock(start + seconds)}\n\n"
            f"FALA SUGERIDA\n{item['speech']}")
    if item["cue"]:
        text += f"\n\nCONDUÇÃO / DEMONSTRAÇÃO\n{item['cue']}"
    if item["source"]:
        text += f"\n\nFONTE / PROCEDÊNCIA\n{item['source']}"
    if item["kind"] == "references":
        text += "\n\n" + "\n".join(f"{n} {url}" for n, _, url in REFERENCES)
    return text


def screen_md(item):
    data = item["content"]
    kind = item["kind"]
    if kind == "table":
        rows = [data["headers"], ["---"] * len(data["headers"]), *data["rows"]]
        return "\n".join("| " + " | ".join(str(c).replace("|", "\\|") for c in row) + " |" for row in rows)
    if kind == "code":
        return "```text\n" + data["code"] + "\n```\n\n" + "\n".join("- " + x for x in data.get("items", []))
    if kind == "formula":
        return "```text\n" + data["formula"] + "\n```\n\n" + "\n".join("- " + x for x in data["items"])
    if kind == "agenda":
        return "\n".join(f"- {n}. **{title}** — {detail}" for n, title, detail in data)
    if kind == "cards":
        return "\n".join(f"- **{title}:** {detail.replace(chr(10), ' ')}" for title, detail in data)
    if kind == "references":
        return "\n".join(f"- {n} [{title}]({url})" for n, title, url in data)
    if kind == "cover":
        return data["subtitle"]
    lines = []
    if kind == "statement":
        lines.append("> " + data["statement"] + "\n")
    if kind == "flow":
        lines.append(" → ".join(f"{a} ({b})" for a, b in data["steps"]) + "\n")
    if kind == "bars":
        lines += [f"- {a}: **{b} expansões**." for a, b in data["values"]]
    lines += ["- " + item for item in data.get("items", [])]
    return "\n".join(lines)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def slide_by_title(fragment):
    """
    Look a slide up by title rather than by position.

    Positional constants silently attach themselves to the wrong slide the first
    time anyone inserts one, and the assertions below would then verify the
    wrong table while still passing.
    """
    matches = [item for item in SLIDES if fragment in item["title"]]
    assert len(matches) == 1, f"expected exactly one slide matching {fragment!r}"
    return matches[0]


def verify_bundle():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert sha(OUTPUT) == manifest["deck_sha256"], "Presentation changed after the synchronized build"
    assert sha(SCRIPT) == manifest["script_sha256"], "Speaking script changed after the synchronized build"
    for relative, expected in manifest["source_sha256"].items():
        assert sha(ROOT / relative) == expected, f"Source changed: {relative}; review evidence and rebuild"
    prs = Presentation(OUTPUT)
    assert len(prs.slides) == len(SLIDES) == manifest["slides"]
    script = SCRIPT.read_text(encoding="utf-8")
    elapsed = 0
    for i, (slide, item, seconds) in enumerate(zip(prs.slides, SLIDES, durations()), 1):
        expected = notes_text(item, i, seconds, elapsed)
        assert slide.notes_slide.notes_text_frame.text == expected, f"Speaker notes differ on slide {i}"
        assert item["speech"] in script, f"Speaking text differs on slide {i}"
        assert f"## Slide {i:02d} — {item['title']}" in script
        if i > 1:
            assert item["title"] in [s.text for s in slide.shapes if s.has_text_frame]
        elapsed += seconds
    # Compare the numeric result table to the recorded demonstration output.
    evidence = json.loads((HERE / "presentation-evidence.json").read_text(encoding="utf-8"))
    keys = ["rf_interference", "excess_path_loss", "mac_contention", "node_failure",
            "upstream_relay_failure", "routing_misconfiguration", "congestion", "healthy"]
    for row, key in zip(slide_by_title("oito casos ilustrativos")["content"]["rows"], keys):
        expected = evidence["diagnose"][key]
        assert abs(float(row[1].replace(",", ".")) - expected["diagnosis"]["cf"]) <= .000051
        assert row[2] == expected["recommended_action"]["value"]
    algorithms = ["Breadth-first", "Depth-first", "Uniform cost (Dijkstra)", "Greedy best-first", "A*"]
    for row, algorithm in zip(slide_by_title("Comparação: NOC")["content"]["rows"], algorithms):
        expected = evidence["route"][algorithm]
        assert int(row[1]) == expected["hops"] and int(row[3]) == expected["expanded"]
        assert abs(float(row[2].replace(" ms", "").replace(",", ".")) - expected["cost"]) <= .0051
    benchmark_data = evidence["benchmark"]
    bars = slide_by_title("Esforço de busca")["content"]["values"]
    assert bars[0][1] == benchmark_data["uniform_expanded"]
    assert bars[1][1] == benchmark_data["astar_expanded"]
    print(f"Synchronization verified: {len(SLIDES)} titles, {len(SLIDES)} complete notes, script, source hashes and displayed result tables.")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify existing artifacts without regenerating them")
    args = parser.parse_args()
    if args.check:
        verify_bundle()
        return
    assert len(SLIDES) == 59
    prs = Presentation(BASELINE)
    # Keep the original cover, master, layout relationships and embedded branding.
    for slide_id in list(prs.slides._sldIdLst)[1:]:
        prs.part.drop_rel(slide_id.rId)
        prs.slides._sldIdLst.remove(slide_id)
    cover = prs.slides[0]
    for shape in list(cover.shapes):
        if shape.has_text_frame:
            shape._element.getparent().remove(shape._element)
    box(cover, 4.50, 2.05, 8.03, 2.22, "Sistema especialista,\nplanejamento automático\ne busca A*", 34, WHITE, True)
    box(cover, 4.50, 4.45, 7.90, .95, SLIDES[0]["content"]["subtitle"], 24, WHITE)
    box(cover, 4.50, 5.63, 7.65, .45, "INTRODUÇÃO À INTELIGÊNCIA ARTIFICIAL", 19, WHITE, True)
    box(cover, 4.50, 6.15, 6.52, .42, "Fernando Sabino Dantas", 21, WHITE)
    box(cover, 4.50, 6.68, 6.52, .35, "Prof. Edson Emílio Scalabrin", 18, WHITE)
    times = durations()
    running = 0
    notes = []
    for index, (item, seconds) in enumerate(zip(SLIDES, times), 1):
        slide = cover if index == 1 else prs.slides.add_slide(prs.slide_layouts[1])
        if index > 1:
            for shape in list(slide.shapes):
                shape._element.getparent().remove(shape._element)
            header(slide, item, index)
            body(slide, item)
        text = notes_text(item, index, seconds, running)
        slide.notes_slide.notes_text_frame.text = text
        notes.append(text)
        running += seconds
    props = prs.core_properties
    props.title = "Sistema especialista, planejamento automático e busca A* em redes sem fio simuladas"
    props.subject = "Três minissistemas de inteligência artificial: modelo, implementação e avaliação"
    props.author = "Fernando Sabino Dantas"
    props.keywords = "sistema especialista; STRIPS; GPS; A*; simulação; redes sem fio"
    props.comments = "Roteiro e notas gerados a partir de academic_content.py."
    props.language = "pt-BR"
    props.last_modified_by = "Fernando Sabino Dantas"
    prs.save(OUTPUT)

    md = ["# Roteiro de apresentação — três minissistemas de inteligência artificial", "",
          "Apresentação: [mini-systems-presentation.pptx](mini-systems-presentation.pptx).", "",
          "**57 slides · duração de ensaio: aproximadamente 90 minutos**, incluindo demonstrações, leitura de diagramas e discussão. "
          "A duração é uma previsão; ajustar o ritmo após ensaio. O texto abaixo é uma fala sugerida, não uma transcrição de execução experimental.", "",
          "**Sincronização:** este arquivo e as notas do PowerPoint são gerados da mesma fonte, "
          "[academic_content.py](academic_content.py). Alterar a fonte e executar `python docs/presentation/build_academic_deck.py` para atualizar ambos. "
          "Evitar editar somente o PPTX ou somente este Markdown. Verificar a correspondência sem regenerar com "
          "`python docs/presentation/build_academic_deck.py --check`.", "",
          "**Preparação:** usar o ambiente Python do projeto com `python-pptx` para regenerar o deck. "
          "As demonstrações precisam apenas da biblioteca padrão e do código local. Executar os comandos a partir da raiz do repositório.", "",
          "```powershell", "python docs/presentation/presentation_demo.py all", "```", "",
          "Os exemplos usam explicitamente a base simulada e a API do planejador. Não executam ns-3. "
          "A execução completa também verifica o caso de destino isolado e compara custos com Floyd–Warshall.", "",
          "## Índice e tempo previsto", "", "| Slide | Título | Janela de ensaio |", "| --- | --- | --- |"]
    elapsed = 0
    for i, (item, seconds) in enumerate(zip(SLIDES, times), 1):
        md.append(f"| {i:02d} | [{item['title']}](#slide-{i:02d}) | {clock(elapsed)}–{clock(elapsed + seconds)} |")
        elapsed += seconds
    elapsed = 0
    for i, (item, seconds) in enumerate(zip(SLIDES, times), 1):
        md += ["", f'<a id="slide-{i:02d}"></a>', "", f"## Slide {i:02d} — {item['title']}", "",
               f"**Seção:** {item['section']}  ",
               f"**Tempo previsto:** {clock(seconds)} · **Janela:** {clock(elapsed)}–{clock(elapsed + seconds)}", "",
               "### Conteúdo exibido", "", screen_md(item), ""]
        if isinstance(item["content"], dict) and item["content"].get("takeaway"):
            md += ["**Mensagem central:** " + item["content"]["takeaway"], ""]
        md += ["### Fala sugerida", "", item["speech"], ""]
        if item["cue"]:
            md += ["### Condução / demonstração", "", item["cue"], ""]
        if item["source"]:
            md += ["**Fonte / procedência:** " + item["source"], ""]
        if i < len(SLIDES):
            md += ["**Transição:** " + SLIDES[i]["title"] + ".", ""]
        elapsed += seconds
    SCRIPT.write_text("\n".join(md), encoding="utf-8")

    git_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    sources = [HERE / "academic_content.py", HERE / "build_academic_deck.py", HERE / "presentation_demo.py",
               HERE / "presentation-evidence.json",
               ROOT / "src/aisg/expert_system/engine.py", ROOT / "src/aisg/expert_system/kb_simulated.py",
               ROOT / "src/aisg/planning/domain_restoration.py", ROOT / "src/aisg/planning/forward.py",
               ROOT / "src/aisg/planning/gps.py", ROOT / "src/aisg/search/algorithms.py",
               ROOT / "src/aisg/domain/topology.py", ROOT / "src/aisg/domain/data/backhaul-topology-30.json"]
    manifest = {"slides": len(SLIDES), "speech_words": sum(len(s["speech"].split()) for s in SLIDES),
                "rehearsal_seconds": sum(times), "repository_head_at_build": git_head,
                "baseline_sha256": sha(BASELINE), "deck_sha256": sha(OUTPUT), "script_sha256": sha(SCRIPT),
                "source_sha256": {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p) for p in sources},
                "slide_mapping": [{"number": i, "title": item["title"],
                                   "notes_sha256": hashlib.sha256(note.encode()).hexdigest()}
                                  for i, (item, note) in enumerate(zip(SLIDES, notes), 1)]}
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Verify the saved package, complete notes and display headings against the source.
    reopened = Presentation(OUTPUT)
    assert len(reopened.slides) == len(SLIDES)
    for i, (slide, item, expected) in enumerate(zip(reopened.slides, SLIDES, notes), 1):
        assert slide.notes_slide.notes_text_frame.text == expected, f"Notes mismatch: {i}"
        if i > 1:
            assert item["title"] in [s.text for s in slide.shapes if s.has_text_frame], f"Title mismatch: {i}"
        assert f"## Slide {i:02d} — {item['title']}" in SCRIPT.read_text(encoding="utf-8")
        assert item["speech"] in SCRIPT.read_text(encoding="utf-8")
    verify_bundle()
    print(f"Generated {len(SLIDES)} slides and {manifest['speech_words']} spoken-script words; all titles and notes synchronized.")


if __name__ == "__main__":
    main()
