#!/usr/bin/env python3
"""Generate the scope_training_backpack KiCad 9 schematic set.

Usage: generate_schematic.py OUTPUT_DIR

Writes the root sheet, the four sub-sheets in Schematics/, a small project
symbol library, sym-lib-table and intent_netlist.json (the connectivity this
script meant to draw, which verify_schematic.py compares with KiCad's netlist).

WARNING: running this against the project folder overwrites hand edits made
in KiCad. Treat it as a one-time bootstrap unless you edit the design here.
"""
import json, os, re, sys, uuid

KICAD = r"C:\Program Files\KiCad\9.0\share\kicad"
PROJECT = "scope_training_backpack"
ROOT_UUID = "2a9d4f5e-6b3c-4d7f-8e9a-1b2c3d4e5f6a"
NS = uuid.UUID("7f1f0c52-9c55-4d0e-9d7e-3a6a7f6e1b11")
DATE = "2026-11-04"
REV = "2.0"

def uid(seed):
    return str(uuid.uuid5(NS, seed))

# ---------------------------------------------------------------- s-expr
TOK = re.compile(r'\s*(\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+)')

def parse(text):
    stack, cur, pos = [], [], 0
    n = len(text)
    while pos < n:
        m = TOK.match(text, pos)
        if not m:
            break
        pos = m.end()
        t = m.group(1)
        if t == "(":
            stack.append(cur)
            cur = []
        elif t == ")":
            stack[-1].append(cur)
            cur = stack.pop()
        else:
            cur.append(t)
    return cur

def dump(x, ind=0):
    if not isinstance(x, list):
        return x
    if all(not isinstance(i, list) for i in x):
        return "(" + " ".join(x) + ")"
    pad = "\t" * (ind + 1)
    out, head = [], []
    i = 0
    while i < len(x) and not isinstance(x[i], list):
        head.append(x[i])
        i += 1
    for c in x[i:]:
        out.append(pad + dump(c, ind + 1))
    return "(" + " ".join(head) + "\n" + "\n".join(out) + "\n" + "\t" * ind + ")"

def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'

def uq(s):
    return s[1:-1].replace('\\"', '"') if s.startswith('"') else s

_libs = {}

def load_lib(lib):
    if lib not in _libs:
        path = os.path.join(KICAD, "symbols", lib + ".kicad_sym")
        tree = parse(open(path, encoding="utf8").read())[0]
        _libs[lib] = {uq(c[1]): c for c in tree if isinstance(c, list) and c[0] == "symbol"}
    return _libs[lib]

LOCAL_LIB_SRC = {}

def local_symbols():
    """+3.3VD does not exist in KiCad's power library; derive it from +3.3VA."""
    s = dump(load_lib("power")["+3.3VA"]).replace("+3.3VA", "+3.3VD")
    return {"+3.3VD": parse(s)[0]}

def flat_symbol(lib_id):
    lib, name = lib_id.split(":")
    if lib == PROJECT:
        node = local_symbols()[name]
        return parse(dump(node))[0]
    syms = load_lib(lib)
    node = syms[name]
    ext = [c for c in node if isinstance(c, list) and c[0] == "extends"]
    if not ext:
        return parse(dump(node))[0]
    parent_name = uq(ext[0][1])
    parent = parse(dump(flat_symbol(lib + ":" + parent_name)))[0]
    own = {uq(c[1]): c for c in node if isinstance(c, list) and c[0] == "property"}
    res = [parent[0], q(name)]
    for c in parent[2:]:
        if isinstance(c, list) and c[0] == "property" and uq(c[1]) in own:
            res.append(own[uq(c[1])])
        elif isinstance(c, list) and c[0] == "symbol":
            c[1] = q(uq(c[1]).replace(parent_name, name, 1))
            res.append(c)
        else:
            res.append(c)
    have = {uq(c[1]) for c in res if isinstance(c, list) and c[0] == "property"}
    at = next(i for i, c in enumerate(res) if isinstance(c, list) and c[0] == "symbol")
    for k, c in own.items():
        if k not in have:
            res.insert(at, c)
            at += 1
    return res

def sym_info(lib_id):
    """pins: {num: (x, y)} by unit; props: lib property nodes; attrs."""
    node = flat_symbol(lib_id)
    props = {uq(c[1]): c for c in node if isinstance(c, list) and c[0] == "property"}
    pins = {}
    for c in node:
        if isinstance(c, list) and c[0] == "symbol":
            m = re.match(r".*_(\d+)_(\d+)$", uq(c[1]))
            unit = int(m.group(1))
            for p in c:
                if isinstance(p, list) and p[0] == "pin":
                    at = next(a for a in p if isinstance(a, list) and a[0] == "at")
                    num = uq(next(a for a in p if isinstance(a, list) and a[0] == "number")[1])
                    pins.setdefault(unit, {})[num] = (float(at[1]), float(at[2]))
    attrs = {k: next((c[1] for c in node if isinstance(c, list) and c[0] == k), "yes")
             for k in ("in_bom", "on_board")}
    return node, props, pins, attrs

class Pin(tuple):
    """Absolute pin coordinate that remembers which component pin it is."""
    def __new__(cls, x, y, ref, num):
        o = super().__new__(cls, (x, y))
        o.ref, o.num = ref, num
        return o

def fmt(v):
    s = "%.4f" % v
    return s.rstrip("0").rstrip(".") if "." in s else s

FP = dict(
    R="Resistor_SMD:R_0603_1608Metric",
    C="Capacitor_SMD:C_0603_1608Metric",
    CP="Capacitor_SMD:C_0805_2012Metric",
    FB="Inductor_SMD:L_0805_2012Metric",
    L="Inductor_SMD:L_1210_3225Metric",
    SOIC8="Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
    SSOP20="Package_SO:SSOP-20_5.3x7.2mm_P0.65mm",
    TSSOP16="Package_SO:TSSOP-16_4.4x5mm_P0.65mm",
    SC70="Package_TO_SOT_SMD:SOT-363_SC-70-6",
    SOT236="Package_TO_SOT_SMD:SOT-23-6",
    C1206="Capacitor_SMD:C_1206_3216Metric",
    CTANT="Capacitor_Tantalum_SMD:CP_EIA-7343-31_Kemet-D",
    SOT23="Package_TO_SOT_SMD:SOT-23",
    SMA="Connector_Coaxial:SMA_Samtec_SMA-J-P-H-ST-EM1_EdgeMount",
    TP="TestPoint:TestPoint_Pad_D1.5mm",
    H2="Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
    H3="Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
    H5="Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical",
    S10="Connector_PinSocket_2.54mm:PinSocket_1x10_P2.54mm_Vertical",
    S40="Connector_PinSocket_2.54mm:PinSocket_2x20_P2.54mm_Vertical",
    IDC16="Connector_IDC:IDC-Header_2x08_P2.54mm_Vertical",
    IDC24="Connector_IDC:IDC-Header_2x12_P2.54mm_Vertical",
    TVS="Diode_SMD:D_SOD-882",
)

REFS = {"pwr": 0, "flg": 0}
ALL_FOOTPRINTS = set()
ALL_REFS = {}

class Sheet:
    def __init__(self, fname, title, name, comments=(), paper="A3"):
        self.fname, self.title, self.name, self.comments, self.paper = fname, title, name, comments, paper
        self.path = "/" + ROOT_UUID + ("/" + uid("sheet:" + name) if name else "")
        self.uuid = ROOT_UUID if not name else uid("doc:" + name)
        self.syms, self.wires, self.labels, self.texts, self.ncs, self.sheets = [], [], [], [], [], []
        self.used = {}
        self.nets = {}      # logical net -> set of "REF.pin"
        self.hier = []      # (name, shape)
        self.n = 0
        self.points = []    # pin / label points that can need wire splitting

    def _u(self, tag=""):
        self.n += 1
        return uid("%s:%d:%s" % (self.fname, self.n, tag))

    def sym(self, lib_id, ref, value, x, y, rot=0, unit=1, fp="", dnp=False, mpn=None,
            ref_at=None, val_at=None, hide_value=False):
        x, y = round(x, 4), round(y, 4)
        node, props, pins, attrs = sym_info(lib_id)
        node = list(node); node[1] = q(lib_id)
        self.used[lib_id] = node
        if not ref.startswith("#"):
            key = ALL_REFS.setdefault(ref, set())
            if unit in key:
                raise SystemExit("duplicate reference %s unit %d" % (ref, unit))
            key.add(unit)
        if fp:
            ALL_FOOTPRINTS.add(fp)
        a = [rot % 360 * 3.141592653589793 / 180]
        import math
        c, s = round(math.cos(a[0])), round(math.sin(a[0]))
        def tr(px, py):
            return round(x + px * c - py * s, 4), round(y - (px * s + py * c), 4)
        vals = {"Reference": ref, "Value": value, "Footprint": fp}
        lines = []
        for pname, pnode in props.items():
            at = next(k for k in pnode if isinstance(k, list) and k[0] == "at")
            eff = next(k for k in pnode if isinstance(k, list) and k[0] == "effects")
            px, py, pa = float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0
            ax, ay = tr(px, py)
            ang = (pa + rot) % 360
            if pname == "Reference" and ref_at:
                ax, ay, ang = x + ref_at[0], y + ref_at[1], ref_at[2]
            if pname == "Value" and val_at:
                ax, ay, ang = x + val_at[0], y + val_at[1], val_at[2]
            effs = dump(eff)
            if (pname == "Reference" and ref_at) or (pname == "Value" and val_at):
                spec = ref_at if pname == "Reference" else val_at
                j = " (justify %s)" % spec[3] if len(spec) > 3 else ""
                effs = "(effects (font (size 1.27 1.27))%s)" % j
            if pname == "Value" and hide_value:
                effs = "(effects (font (size 1.27 1.27)) (hide yes))"
            v = vals.get(pname, uq(pnode[2]))
            lines.append('(property %s %s (at %s %s %s) %s)' % (q(pname), q(v), fmt(ax), fmt(ay), fmt(ang), effs))
        if mpn:
            lines.append('(property "MPN" %s (at %s %s 0) (effects (font (size 1.27 1.27)) (hide yes)))' % (q(mpn), fmt(x), fmt(y)))
        visible = dict(pins.get(0, {}))
        visible.update(pins.get(unit, {}))
        for num in visible:
            lines.append('(pin %s (uuid "%s"))' % (q(num), self._u("pin" + ref + num)))
        lines.append('(instances (project "%s" (path "%s" (reference %s) (unit %d))))' % (PROJECT, self.path, q(ref), unit))
        self.syms.append('(symbol (lib_id %s) (at %s %s %s) (unit %d) (exclude_from_sim no) (in_bom %s) (on_board %s) (dnp %s) (uuid "%s")\n\t\t%s)' % (
            q(lib_id), fmt(x), fmt(y), fmt(rot), unit, attrs["in_bom"], attrs["on_board"], "yes" if dnp else "no",
            self._u("sym" + ref), "\n\t\t".join(lines)))
        out = {}
        for num, (px, py) in visible.items():
            ax, ay = tr(px, py)
            out[num] = Pin(ax, ay, ref, num)
            self.points.append((ax, ay))
        return out

    def two(self, kind, ref, value, x, y, horiz=True, dnp=False, rot=None, lib=None, fp=None, mpn=None):
        """Two-terminal part. Horizontal: pin 1 left. Vertical: pin 1 top."""
        lib_id = lib or {"R": "Device:R", "C": "Device:C", "CP": "Device:C_Polarized",
                         "FB": "Device:FerriteBead", "L": "Device:L"}[kind]
        fp = fp if fp is not None else FP.get(kind, "")
        if rot is None:
            rot = 90 if horiz else 0
        ang = 90 if rot % 180 == 90 else 0
        if horiz:
            off = 3.81 if kind == "FB" else 2.54
            ra, va = (0, -off, ang), (0, off, ang)
        else:
            ra, va = (3.3, -1.27, ang, "left"), (3.3, 1.27, ang, "left")
        return self.sym(lib_id, ref, value, x, y, rot=rot, fp=fp, dnp=dnp, ref_at=ra, val_at=va, mpn=mpn)

    def _rec(self, net, pts):
        s = self.nets.setdefault(net, set())
        for p in pts:
            if isinstance(p, Pin):
                s.add(p.ref + "." + p.num)

    def w(self, net, *pts):
        """Orthogonal polyline. Non-aligned neighbours route horizontal first."""
        self._rec(net, pts)
        for a, b in zip(pts, pts[1:]):
            a, b = (round(a[0], 4), round(a[1], 4)), (round(b[0], 4), round(b[1], 4))
            if a == b:
                continue
            if a[0] != b[0] and a[1] != b[1]:
                mid = (b[0], a[1])
                self.wires.append((a, mid))
                self.wires.append((mid, b))
            else:
                self.wires.append((a, b))

    def lab(self, net, pin, d="R", stub=2.54):
        dx, dy, rot, just = {"R": (1, 0, 0, "left"), "L": (-1, 0, 180, "right"),
                             "U": (0, -1, 90, "left"), "D": (0, 1, 270, "right")}[d]
        end = (round(pin[0] + dx * stub, 4), round(pin[1] + dy * stub, 4))
        self.w(net, pin, end)
        self.labels.append('(label %s (at %s %s %d) (effects (font (size 1.27 1.27)) (justify %s bottom)) (uuid "%s"))' % (
            q(net), fmt(end[0]), fmt(end[1]), rot, just, self._u("lab" + net)))
        self.points.append(end)
        return end

    def hl(self, net, pin, shape="input", d="L", stub=2.54):
        dx, rot, just = {"L": (-1, 180, "right"), "R": (1, 0, "left")}[d]
        end = (round(pin[0] + dx * stub, 4), round(pin[1], 4))
        self.w(net, pin, end)
        self.labels.append('(hierarchical_label %s (shape %s) (at %s %s %d) (effects (font (size 1.27 1.27)) (justify %s)) (uuid "%s"))' % (
            q(net), shape, fmt(end[0]), fmt(end[1]), rot, just, self._u("hl" + net)))
        self.points.append(end)
        if (net, shape) not in self.hier:
            self.hier.append((net, shape))
        return end

    def pwr(self, net, pin, d=None, stub=2.54):
        """Stub + power symbol. d is the direction the symbol points."""
        ground = net.startswith("GND")
        d = d or ("D" if ground else "U")
        dx, dy = {"R": (1, 0), "L": (-1, 0), "U": (0, -1), "D": (0, 1)}[d]
        end = (round(pin[0] + dx * stub, 4), round(pin[1] + dy * stub, 4))
        self.w(net, pin, end)
        base = "D" if ground else "U"
        order = ["U", "L", "D", "R"]   # counter-clockwise on screen
        rot = ((order.index(d) - order.index(base)) * 90) % 360
        REFS["pwr"] += 1
        lib = PROJECT + ":+3.3VD" if net == "+3.3VD" else "power:" + net
        va = None
        if d in "LR":
            off = 3.3 + len(net) * 0.55
            va = ((off if d == "R" else -off), 0, 90)
        self.sym(lib, "#PWR%03d" % REFS["pwr"], net, end[0], end[1], rot=rot, val_at=va)
        return end

    def flag(self, net, x, y):
        REFS["flg"] += 1
        self.sym("power:PWR_FLAG", "#FLG%03d" % REFS["flg"], "PWR_FLAG", x, y)
        ground = net.startswith("GND")
        if ground:
            self.pwr(net, (x, y), "D", 2.54)
        else:
            self.w(net, (x, y), (x + 5.08, y))
            self.pwr(net, (x + 5.08, y), "U", 2.54)

    def nc(self, pin):
        self.ncs.append('(no_connect (at %s %s) (uuid "%s"))' % (fmt(pin[0]), fmt(pin[1]), self._u("nc")))

    def text(self, s, x, y, size=1.27, bold=False):
        b = " (bold yes)" if bold else ""
        self.texts.append('(text %s (exclude_from_sim no) (at %s %s 0) (effects (font (size %s %s)%s) (justify left top)) (uuid "%s"))' % (
            q(s), fmt(x), fmt(y), size, size, b, self._u("txt")))

    def add_sheet(self, sub, x, y, w, file_rel, page, pins):
        h = len(pins) * 2.54 + 5.08
        lines = []
        spts = []
        for i, (n, shape) in enumerate(pins):
            py = y + 2.54 * (i + 1)
            lines.append('(pin %s %s (at %s %s 180) (uuid "%s") (effects (font (size 1.27 1.27)) (justify left)))' % (
                q(n), shape, fmt(x), fmt(py), self._u("spin" + n)))
            spts.append((n, (x, py)))
        self.sheets.append(
            '(sheet (at %s %s) (size %s %s) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (fields_autoplaced yes)\n'
            '\t\t(stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0.0)) (uuid "%s")\n'
            '\t\t(property "Sheetname" %s (at %s %s 0) (effects (font (size 1.4 1.4)) (justify left bottom)))\n'
            '\t\t(property "Sheetfile" %s (at %s %s 0) (effects (font (size 1.27 1.27)) (justify left top)))\n\t\t%s\n'
            '\t\t(instances (project "%s" (path "/%s" (page "%d")))))' % (
                fmt(x), fmt(y), fmt(w), fmt(h), uid("sheet:" + sub.name), q(sub.name), fmt(x), fmt(y - 0.7),
                q(file_rel), fmt(x), fmt(y + h + 0.7), "\n\t\t".join(lines), PROJECT, ROOT_UUID, page))
        return spts

    def render(self):
        segs = []
        for a, b in self.wires:
            segs.append((a, b))
        # gather split points: every endpoint or pin lying on the interior of a wire
        pts = set(self.points)
        for a, b in segs:
            pts.add(a); pts.add(b)
        def on(p, a, b):
            if a[0] == b[0] == p[0]:
                return min(a[1], b[1]) < p[1] < max(a[1], b[1])
            if a[1] == b[1] == p[1]:
                return min(a[0], b[0]) < p[0] < max(a[0], b[0])
            return False
        final = []
        junction = set()
        for a, b in segs:
            cuts = sorted([p for p in pts if on(p, a, b)], key=lambda p: (p[0], p[1]))
            seq = sorted({a, b, *cuts}, key=lambda p: (p[0], p[1]))
            final += list(zip(seq, seq[1:]))
            junction.update(cuts)
        final = list({tuple(sorted(s)) for s in final})
        ends = {}
        for a, b in final:
            ends[a] = ends.get(a, 0) + 1
            ends[b] = ends.get(b, 0) + 1
        for p, cnt in ends.items():
            if cnt >= 3:
                junction.add(p)
        body = []
        for j in sorted(junction):
            body.append('(junction (at %s %s) (diameter 0) (color 0 0 0 0) (uuid "%s"))' % (fmt(j[0]), fmt(j[1]), self._u("j")))
        for a, b in sorted(final):
            body.append('(wire (pts (xy %s %s) (xy %s %s)) (stroke (width 0) (type default)) (uuid "%s"))' % (
                fmt(a[0]), fmt(a[1]), fmt(b[0]), fmt(b[1]), self._u("w")))
        libs = "\n\t\t".join(dump(self.used[k], 2) for k in sorted(self.used))
        comments = "\n\t\t".join('(comment %d %s)' % (i + 1, q(c)) for i, c in enumerate(self.comments))
        inst = '(sheet_instances (path "/" (page "1")))\n\t(embedded_fonts no)' if not self.name else '(embedded_fonts no)'
        return ('(kicad_sch\n\t(version 20250114)\n\t(generator "eeschema")\n\t(generator_version "9.0")\n'
                '\t(uuid "%s")\n\t(paper "%s")\n\t(title_block\n\t\t(title %s)\n\t\t(date "%s")\n\t\t(rev "%s")\n'
                '\t\t(company "DIY Training Project")\n\t\t%s\n\t)\n\t(lib_symbols\n\t\t%s\n\t)\n\t%s\n\t%s\n\t%s\n\t%s\n\t%s\n\t%s\n\t%s\n)\n' % (
                    self.uuid, self.paper, q(self.title), DATE, REV, comments, libs,
                    "\n\t".join(body), "\n\t".join(self.ncs), "\n\t".join(self.labels), "\n\t".join(self.texts),
                    "\n\t".join(self.syms), "\n\t".join(self.sheets), inst))

def G(k):
    return round(k * 2.54, 4)

# ================================================================ ANALOG
def out_stage(s, net, x, y, rref, rval, tp, sma, smaval, gnd="GNDA"):
    """(x,y) -> series R -> test-point node -> SMA."""
    r = s.two("R", rref, rval, x + 10.16, y)
    s.w(net, (x, y), r["1"])
    node = (x + 19.05, y)
    onet = net + "_OUT"
    s.w(onet, r["2"], node)
    t = s.sym("Connector:TestPoint", tp, onet, node[0], y - 5.08, fp=FP["TP"], hide_value=False)
    s.w(onet, node, t["1"])
    c = s.sym("Connector:Conn_Coaxial", sma, smaval, node[0] + 10.16, y, fp=FP["SMA"], mpn="CONSMA003.062-G")
    s.w(onet, node, c["1"])
    s.pwr(gnd, c["2"])

def buf(s, ref, unit, ox, y, nin, nout):
    a = s.sym("Amplifier_Operational:MCP6002-xSN", ref, "MCP6002", ox, y + 2.54, unit=unit, fp=FP["SOIC8"], mpn="MCP6002-E/SN")
    fb = [a["2"] if unit == 1 else a["6"]]
    out = a["1"] if unit == 1 else a["7"]
    inp = a["3"] if unit == 1 else a["5"]
    s.w(nin, inp, inp)
    s._rec(nin, [inp])
    corner = (ox + 10.16, y + 2.54)
    s.w(nout, fb[0], (ox - 10.16, y + 5.08), (ox - 10.16, y + 10.16), (ox + 10.16, y + 10.16), corner)
    s.w(nout, out, corner)
    return inp, corner

def gen_analog():
    s = Sheet("analog_output.kicad_sch", "Analog Output Section", "Analog_Output",
              ["MCP6002 buffers, 47R damping, test points, SMA outputs",
               "SMA6/SMA7 are CAN (Digital_Protocols). SMA8 is the amplified AD9851 output."])
    # --- DAC0
    y = 45.72
    s.text("DAC0 -> SMA1  (0-3.3 V, DC-500 kHz)", 22.86, y - 15.24, 1.8, True)
    r1 = s.two("R", "R1", "0R", 45.72, y)
    c1 = s.two("C", "C1", "100nF", 45.72, y - 7.62, dnp=True)
    s.hl("DAC0", (38.1, y), "input", "L", 12.7)
    s.w("DAC0", (38.1, y), r1["1"]); s.w("DAC0", (38.1, y), (38.1, y - 7.62), c1["1"])
    i, o = buf(s, "U1", 1, 76.2, y, "DAC0_B", "DAC0_F")
    s.w("DAC0_B", r1["2"], (53.34, y), i); s.w("DAC0_B", c1["2"], (53.34, y - 7.62), (53.34, y))
    out_stage(s, "DAC0_F", o[0], o[1], "R2", "47R", "TP1", "SMA1", "DAC0")
    # --- DAC1
    y = 96.52
    s.text("DAC1 -> SMA2  (0-3.3 V with R7 fitted; about 0-300 mV with R5/R6 fitted and R7 removed)", 22.86, y - 15.24, 1.8, True)
    r3 = s.two("R", "R3", "0R", 45.72, y)
    c2 = s.two("C", "C2", "100nF", 45.72, y - 7.62, dnp=True)
    s.hl("DAC1", (38.1, y), "input", "L", 12.7)
    s.w("DAC1", (38.1, y), r3["1"]); s.w("DAC1", (38.1, y), (38.1, y - 7.62), c2["1"])
    i, o = buf(s, "U1", 2, 76.2, y, "DAC1_B", "DAC1_F")
    s.w("DAC1_B", r3["2"], (53.34, y), i); s.w("DAC1_B", c2["2"], (53.34, y - 7.62), (53.34, y))
    yo = o[1]
    r4 = s.two("R", "R4", "47R", o[0] + 10.16, yo)
    s.w("DAC1_F", o, r4["1"])
    n1x = o[0] + 17.78
    r7 = s.two("R", "R7", "0R", n1x + 7.62, yo)
    r5 = s.two("R", "R5", "10k", n1x + 7.62, yo - 7.62, dnp=True)
    s.w("DAC1_D", r4["2"], (n1x, yo), r7["1"]); s.w("DAC1_D", (n1x, yo), (n1x, yo - 7.62), r5["1"])
    n2x = n1x + 15.24
    s.w("DAC1_F_OUT", r7["2"], (n2x, yo)); s.w("DAC1_F_OUT", r5["2"], (n2x, yo - 7.62), (n2x, yo))
    r6 = s.two("R", "R6", "1k", n2x, yo + 7.62, horiz=False, dnp=True)
    s.w("DAC1_F_OUT", (n2x, yo), r6["1"]); s.pwr("GNDA", r6["2"])
    tp2x = n2x + 7.62
    t = s.sym("Connector:TestPoint", "TP2", "DAC1_OUT", tp2x, yo - 5.08, fp=FP["TP"])
    s.w("DAC1_F_OUT", (n2x, yo), (tp2x, yo), t["1"])
    c = s.sym("Connector:Conn_Coaxial", "SMA2", "DAC1", tp2x + 10.16, yo, fp=FP["SMA"], mpn="CONSMA003.062-G")
    s.w("DAC1_F_OUT", (tp2x, yo), c["1"]); s.pwr("GNDA", c["2"])
    # --- PWM0
    y = 147.32
    s.text("PWM0 -> 1.6 kHz low-pass -> SMA3", 22.86, y - 15.24, 1.8, True)
    r8 = s.two("R", "R8", "1k", 45.72, y)
    s.hl("PWM0", r8["1"], "input", "L", 16.51)
    i, o = buf(s, "U2", 1, 76.2, y, "PWM0_B", "PWM0_F")
    s.w("PWM0_B", r8["2"], (55.88, y), i)
    c3 = s.two("C", "C3", "100nF", 55.88, y + 6.35, horiz=False)
    s.w("PWM0_B", (55.88, y), c3["1"]); s.pwr("GNDA", c3["2"])
    out_stage(s, "PWM0_F", o[0], o[1], "R9", "47R", "TP3", "SMA3", "PWM_FILT")

    # ---- right column
    ox = 165.1
    # --- Runt
    y = 45.72
    s.text("PWM1 -> runt network -> SMA4  (buffer slew limit turns narrow pulses into runts)", ox + 22.86, y - 15.24, 1.8, True)
    r11 = s.two("R", "R11", "100R", ox + 45.72, y)
    r10 = s.two("R", "R10", "100R", ox + 40.64, y - 7.62)
    c4 = s.two("C", "C4", "10pF", ox + 50.8, y - 7.62)
    s.hl("PWM1", (ox + 33.02, y), "input", "L", 7.62)
    s.w("PWM1", (ox + 33.02, y), r11["1"]); s.w("PWM1", (ox + 33.02, y), (ox + 33.02, y - 7.62), r10["1"])
    s.w("RUNT_RC", r10["2"], c4["1"])
    i, o = buf(s, "U2", 2, ox + 76.2, y, "RUNT_B", "RUNT_F")
    s.w("RUNT_B", r11["2"], (ox + 58.42, y), i); s.w("RUNT_B", c4["2"], (ox + 58.42, y - 7.62), (ox + 58.42, y))
    out_stage(s, "RUNT_F", o[0], o[1], "R12", "47R", "TP4", "SMA4", "RUNT")
    # --- Mixed
    ya, yc, yb = 76.2, 96.52, 111.76
    s.text("PWM2 -> SMA5  fit exactly ONE of R15 (small signal), R17 (glitch), R18 (direct, default)", ox + 22.86, ya - 10.16, 1.8, True)
    tx, bus = ox + 30.48, ox + 83.82
    s.hl("PWM2", (tx, yc), "input", "L", 5.08)
    s.w("PWM2", (tx, ya), (tx, yb))
    r13a = s.two("R", "R13", "95.3k", ox + 38.1, ya)
    r13b = s.two("R", "R58", "3.3k", ox + 48.26, ya)
    r13c = s.two("R", "R59", "390R", ox + 58.42, ya)
    s.w("PWM2", (tx, ya), r13a["1"]); s.w("MIXA1", r13a["2"], r13b["1"]); s.w("MIXA2", r13b["2"], r13c["1"])
    nA = ox + 64.77
    r14 = s.two("R", "R14", "1k", nA, ya + 6.35, horiz=False)
    r15 = s.two("R", "R15", "0R", ox + 73.66, ya, dnp=True)
    s.w("MIXA", r13c["2"], (nA, ya), r15["1"]); s.w("MIXA", (nA, ya), r14["1"]); s.pwr("GNDA", r14["2"])
    s.w("MIX", r15["2"], (bus, ya), (bus, yb))
    r18 = s.two("R", "R18", "0R", ox + 73.66, yc)
    s.w("PWM2", (tx, yc), r18["1"]); s.w("MIX", r18["2"], (bus, yc))
    c5 = s.two("C", "C5", "22pF", ox + 45.72, yb)
    nB = ox + 55.88
    r16 = s.two("R", "R16", "100R", nB, yb + 6.35, horiz=False)
    r17 = s.two("R", "R17", "0R", ox + 73.66, yb, dnp=True)
    s.w("PWM2", (tx, yb), c5["1"]); s.w("MIXB", c5["2"], (nB, yb), r17["1"]); s.w("MIXB", (nB, yb), r16["1"]); s.pwr("GNDA", r16["2"])
    s.w("MIX", r17["2"], (bus, yb))
    out_stage(s, "MIX", bus, yc, "R19", "47R", "TP5", "SMA5", "MIXED")
    # --- ADC
    y = 160.02
    s.text("ADC input header J10 -> protection, 1.6 MHz anti-alias, buffer -> ADC_IN", ox + 22.86, y - 25.4, 1.8, True)
    j = s.sym("Connector_Generic:Conn_01x02", "J10", "ADC_INPUT", ox + 22.86, y, rot=180, fp=FP["H2"],
              ref_at=(-1.27, 3.81, 0), val_at=(-1.27, 6.35, 0))
    s.pwr("GNDA", j["2"], "R")
    n1 = ox + 38.1
    s.w("ADC_RAW", j["1"], (n1, y))
    r26 = s.two("R", "R26", "10k", n1, y + 6.35, horiz=False)
    s.w("ADC_RAW", (n1, y), r26["1"]); s.pwr("GNDA", r26["2"])
    d1 = s.sym("Diode:BAT54S", "D1", "BAT54S", n1, y - 12.7, fp=FP["SOT23"], mpn="BAT54S")
    s.w("ADC_RAW", (n1, y), d1["3"])
    s.pwr("GNDA", d1["1"], "L"); s.pwr("+3.3VA", d1["2"], "U")
    r24 = s.two("R", "R24", "1k", ox + 45.72, y)
    r25 = s.two("R", "R25", "1k", ox + 55.88, y)
    s.w("ADC_RAW", (n1, y), r24["1"]); s.w("ADC_S", r24["2"], r25["1"])
    i, o = buf(s, "U3", 2, ox + 76.2, y, "ADC_B", "ADC_IN")
    s.w("ADC_B", r25["2"], (ox + 63.5, y), i)
    c6 = s.two("C", "C6", "100pF", ox + 63.5, y + 6.35, horiz=False)
    s.w("ADC_B", (ox + 63.5, y), c6["1"]); s.pwr("GNDA", c6["2"])
    t = s.sym("Connector:TestPoint", "TP7", "ADC_IN", o[0] + 5.08, o[1] - 5.08, fp=FP["TP"])
    s.w("ADC_IN", o, (o[0] + 5.08, o[1]), t["1"])
    s.hl("ADC_IN", (o[0] + 5.08, o[1]), "output", "R", 7.62)

    # --- DDS amplifier: gain of 2 on a filtered +5V rail, AC-coupled in and out
    ox, y = 220.98, 220.98
    yr = y - 25.4
    y0 = y + 2.54
    ax = ox + 66.04
    s.text("AD9851 module -> J12 -> gain of 2 -> SMA8  (1 Vpp into 50R, 2 Vpp into high-Z, 10 Hz-20 MHz)", ox, yr - 11.43, 1.8, True)
    # filtered rail
    fb3 = s.two("FB", "FB3", "220R@100MHz", ox + 30.48, yr, mpn="ILBB0805ER221V")
    s.w("+5V", fb3["1"], (ox + 20.32, yr)); s.pwr("+5V", (ox + 20.32, yr), "U")
    c30 = s.two("CP", "C30", "10uF", ox + 40.64, yr + 6.35, horiz=False)
    c31 = s.two("C", "C31", "100nF", ox + 53.34, yr + 6.35, horiz=False)
    railx = ax - 2.54
    s.w("+5V_DDS", fb3["2"], (ox + 40.64, yr), (ox + 53.34, yr), (railx, yr))
    s.w("+5V_DDS", (ox + 40.64, yr), c30["1"]); s.w("+5V_DDS", (ox + 53.34, yr), c31["1"])
    s.pwr("GNDA", c30["2"]); s.pwr("GNDA", c31["2"])
    REFS["flg"] += 1
    s.sym("power:PWR_FLAG", "#FLG%03d" % REFS["flg"], "PWR_FLAG", ox + 53.34, yr - 5.08)
    s.w("+5V_DDS", (ox + 53.34, yr), (ox + 53.34, yr - 5.08))
    # input and bias
    j12 = s.sym("Connector_Generic:Conn_01x02", "J12", "DDS_IN", ox + 2.54, y, rot=180, fp=FP["H2"],
                ref_at=(-1.27, -8.89, 0), val_at=(-1.27, -6.35, 0))
    s.pwr("GNDA", j12["2"], "R")
    c27 = s.two("C", "C27", "10uF", ox + 22.86, y, fp=FP["CP"])
    s.w("DDS_IN", j12["1"], c27["1"])
    b, xd, vb = ox + 30.48, ox + 20.32, y + 17.78
    r64 = s.two("R", "R64", "10k", b, y + 10.16, horiz=False)
    r62 = s.two("R", "R62", "10k", xd, y + 11.43, horiz=False)
    r63 = s.two("R", "R63", "10k", xd, y + 24.13, horiz=False)
    c29 = s.two("CP", "C29", "10uF", b, y + 24.13, horiz=False)
    s.lab("+5V_DDS", r62["1"], "L", 2.54)
    s.w("DDS_VB", r62["2"], (xd, vb), r63["1"]); s.w("DDS_VB", (xd, vb), (b, vb), r64["2"]); s.w("DDS_VB", (b, vb), c29["1"])
    s.pwr("GNDA", r63["2"]); s.pwr("GNDA", c29["2"])
    # amplifier
    u = s.sym("Amplifier_Operational:OPA355NA", "U12", "OPA355NA", ax, y0, fp=FP["SOT236"], mpn="OPA355NA/250")
    s.w("DDS_P", c27["2"], (b, y), u["3"]); s.w("DDS_P", (b, y), r64["1"])
    s.w("+5V_DDS", (railx, yr), u["6"])
    s.lab("+5V_DDS", (railx, yr), "R", 5.08)
    s.pwr("GNDA", u["2"])
    s.lab("+5V_DDS", (ax + 5.08, y0 + 10.16), "R", 0.0)
    s.w("+5V_DDS", u["5"], (ax, y0 + 10.16), (ax + 5.08, y0 + 10.16))
    cx = ax + 17.78
    fby = y + 22.86
    r60 = s.two("R", "R60", "1k", ax, fby)
    r61 = s.two("R", "R61", "1k", ax - 17.78, fby)
    s.w("DDS_N", u["4"], (ax - 10.16, y + 5.08), (ax - 10.16, fby), r60["1"])
    s.w("DDS_N", (ax - 10.16, fby), r61["2"])
    s.w("DDS_A", r60["2"], (cx, fby), (cx, y0)); s.w("DDS_A", u["1"], (cx, y0))
    c28 = s.two("C", "C28", "47uF", ax - 21.59, y + 29.21, horiz=False, fp=FP["C1206"])
    s.w("DDS_G", r61["1"], (ax - 21.59, fby), c28["1"]); s.pwr("GNDA", c28["2"])
    # output coupling
    c32 = s.two("CP", "C32", "220uF 6.3V", cx + 8.89, y0, fp=FP["CTANT"])
    c33 = s.two("C", "C33", "100nF", cx + 8.89, y0 - 7.62)
    nd = cx + 17.78
    s.w("DDS_A", (cx, y0), c32["1"]); s.w("DDS_A", (cx, y0), (cx, y0 - 7.62), c33["1"])
    s.w("DDS", c32["2"], (nd, y0)); s.w("DDS", c33["2"], (nd, y0 - 7.62), (nd, y0))
    r65 = s.two("R", "R65", "1k", nd, y0 + 6.35, horiz=False)
    s.w("DDS", (nd, y0), r65["1"]); s.pwr("GNDA", r65["2"])
    out_stage(s, "DDS", nd, y0, "R23", "47R", "TP6", "SMA8", "DDS")
    s.text("Amp output sits at 2.5 V DC. C32 blocks it; R65 bleeds C32 so\nthe SMA settles near 0 V. At 10 Hz: about -0.8 dB into high-Z,\n-3 dB into 50R. Limit firmware to 10 Hz-20 MHz.", nd + 6.35, y0 + 15.24)

    # --- power + spare
    yc = 228.6
    s.text("Op-amp supplies and spare section", 22.86, yc - 22.86, 1.8, True)
    a = s.sym("Amplifier_Operational:MCP6002-xSN", "U3", "MCP6002", 50.8, yc, unit=1, fp=FP["SOIC8"], mpn="MCP6002-E/SN")
    s.pwr("GNDA", a["3"], "L")
    k = (60.96, yc)
    s.w("U3A_FB", a["2"], (40.64, yc + 2.54), (40.64, yc + 7.62), (60.96, yc + 7.62), k)
    s.w("U3A_FB", a["1"], k)
    s.text("U3A unused: follower with +IN tied low", 35.56, yc + 11.43)
    caps = [("U1", "C7", "C8"), ("U2", "C10", "C11"), ("U3", "C13", "C14")]
    for n, (u, c01, c10) in enumerate(caps):
        x = 96.52 + n * 45.72
        p = s.sym("Amplifier_Operational:MCP6002-xSN", u, "MCP6002", x, yc, unit=3, fp=FP["SOIC8"], mpn="MCP6002-E/SN")
        s.pwr("+3.3VA", p["8"]); s.pwr("GNDA", p["4"])
        c = s.two("C", c01, "100nF", x + 10.16, yc, horiz=False)
        s.pwr("+3.3VA", c["1"]); s.pwr("GNDA", c["2"])
        c = s.two("CP", c10, "10uF", x + 22.86, yc, horiz=False)
        s.pwr("+3.3VA", c["1"]); s.pwr("GNDA", c["2"])
    s.text("C1/C2: AC coupling is only active with R1/R3 removed; the buffer input then needs a DC bias path (not provided).\n"
           "SMA shells return to GNDA. Keep analog traces away from digital clocks.", 22.86, yc + 25.4)
    return s

# ================================================================ DIGITAL
BUFMAP = ["SPI_CLK", "SPI_MOSI", "SPI_MISO", "SPI_CS", "I2C_SDA", "I2C_SCL", "UART_TX", "UART_RX"]

def gen_digital():
    s = Sheet("digital_protocols.kicad_sch", "Digital Protocols Section", "Digital_Protocols",
              ["74HC541 monitor buffer, headers, LA/AD9851 mux, CAN on SMA6/SMA7",
               "MCP2562 VDD is +5V (datasheet minimum 4.5 V); Vio is +3.3VD"])
    # --- buffer
    x, y = 76.2, 60.96
    s.text("Protocol monitor buffer (MCU side -> headers)", 22.86, 22.86, 1.8, True)
    u = s.sym("74xx:74LS541", "U4", "SN74HC541DBR", x, y, fp=FP["SSOP20"], mpn="SN74HC541DBR")
    for k, name in enumerate(BUFMAP):
        s.hl(name, u[str(2 + k)], "bidirectional" if name in ("I2C_SDA",) else "input", "L", 7.62)
        s.lab("BUF_" + name, u[str(18 - k)], "R", 5.08)
    g = (x - 15.24, y + 10.16)
    s.w("GNDD", u["1"], g); s.w("GNDD", u["19"], (x - 15.24, y + 12.7), g)
    s.pwr("GNDD", g, "L")
    s.pwr("+3.3VD", u["20"]); s.pwr("GNDD", u["10"])
    r50 = s.two("R", "R50", "2.2k", 27.94, 96.52, horiz=False)
    r51 = s.two("R", "R51", "2.2k", 43.18, 96.52, horiz=False)
    for r, n in ((r50, "I2C_SDA"), (r51, "I2C_SCL")):
        s.pwr("+3.3VD", r["1"]); s.lab(n, r["2"], "D", 2.54)
    s.text("I2C pull-ups sit on the MCU side so the bus works; U4 only\nmirrors it to J7. J6 MISO and J8 RX are monitor outputs too.", 22.86, 110.49)
    # --- headers
    hx = 139.7
    s.text("Protocol headers", 127, 22.86, 1.8, True)
    j = s.sym("Connector_Generic:Conn_01x05", "J6", "SPI", hx, 35.56, fp=FP["H5"])
    s.pwr("GNDD", j["1"], "L")
    for p, n in zip("2345", ["SPI_CLK", "SPI_MOSI", "SPI_MISO", "SPI_CS"]):
        s.lab("BUF_" + n, j[p], "L", 2.54)
    j = s.sym("Connector_Generic:Conn_01x03", "J7", "I2C", hx, 55.88, fp=FP["H3"])
    s.pwr("GNDD", j["1"], "L")
    s.lab("BUF_I2C_SDA", j["2"], "L"); s.lab("BUF_I2C_SCL", j["3"], "L")
    j = s.sym("Connector_Generic:Conn_01x03", "J8", "UART", hx, 71.12, fp=FP["H3"])
    s.pwr("GNDD", j["1"], "L")
    s.lab("BUF_UART_TX", j["2"], "L"); s.lab("BUF_UART_RX", j["3"], "L")
    # --- J5
    jx, jy = 139.7, 104.14
    s.text("J5 IDC-16: AD9851 module / logic analyzer", 121.92, jy - 15.24, 1.8, True)
    j = s.sym("Connector_Generic:Conn_02x08_Odd_Even", "J5", "AD9851_LA", jx, jy, fp=FP["IDC16"])
    s.pwr("+3.3VD", j["1"], "L")
    s.pwr("GNDD", j["2"], "R")
    for k in range(12):
        s.lab("IDC%d" % k, j[str(3 + k)], "L" if (3 + k) % 2 else "R", 2.54)
    s.w("GNDD", j["15"], (jx - 10.16, jy + 11.43 - 1.27))
    s.pwr("GNDD", (jx - 10.16, jy + 10.16), "L")
    s.pwr("GNDD", j["16"], "R")
    s.text("Pin 1 +3.3V, 2 GND, 3-10 D0-D7 / CH0-7\n11 W_CLK / CH8, 12 FQ_UD / CH9\n13 RESET / CH10, 14 AUX / CH11, 15-16 GND", 121.92, jy + 20.32)
    # --- mux
    LA = [("BUF_SPI_CLK", 0), ("BUF_SPI_MOSI", 0), ("BUF_SPI_MISO", 0), ("BUF_SPI_CS", 0),
          ("BUF_I2C_SDA", 0), ("BUF_I2C_SCL", 0), ("BUF_UART_TX", 0), ("BUF_UART_RX", 0),
          ("PWM0", 1), ("PWM1", 1), ("PWM2", 1), ("PWM3", 1)]
    DDS = ["DDS_D%d" % i for i in range(8)] + ["DDS_W_CLK", "DDS_FQ_UD", "DDS_RESET", "DDS_AUX"]
    s.text("Mode mux: MUX_SEL LOW = logic analyzer (channel 0), HIGH = AD9851 (channel 1)", 195.58, 22.86, 1.8, True)
    chips = [("U6", 233.68, 53.34), ("U9", 335.28, 53.34), ("U10", 233.68, 109.22), ("U11", 335.28, 109.22)]
    ch = 0
    rn = 38
    for ref, x, y in chips:
        u = s.sym("Analog_Switch:CD4053B", ref, "CD74HC4053PWR", x, y, fp=FP["TSSOP16"], mpn="CD74HC4053PWR")
        b = x - 15.24
        s.w("MUX_SEL", u["11"], (b, y - 12.7), (b, y - 7.62), u["9"])
        s.w("MUX_SEL", u["10"], (b, y - 10.16))
        s.lab("MUX_SEL", (b, y - 12.7), "L", 2.54)
        s.w("GNDD", u["6"], (x - 15.24, y + 12.7), (x - 15.24, y + 20.32), (x - 2.54, y + 20.32))
        s.w("GNDD", u["7"], (x - 2.54, y + 20.32), (x, y + 20.32), u["8"])
        s.pwr("GNDD", (x, y + 20.32), "D")
        s.pwr("+3.3VD", u["16"])
        for com, p0, p1 in (("14", "12", "13"), ("15", "2", "1"), ("4", "5", "3")):
            r = s.two("R", "R%d" % rn, "100R", x - 22.86, u[com][1])
            s.w("IDC_M%d" % ch, u[com], r["2"])
            s.lab("IDC%d" % ch, r["1"], "L", 2.54)
            la, is_hier = LA[ch]
            if is_hier:
                s.hl(la, u[p0], "input", "R", 2.54)
            else:
                s.lab(la, u[p0], "R", 2.54)
            s.hl(DDS[ch], u[p1], "input", "R", 2.54)
            ch += 1
            rn += 1
    r57 = s.two("R", "R57", "10k", 187.96, 45.72, horiz=False)
    s.hl("MUX_SEL", r57["1"], "input", "L", 7.62)
    s.pwr("GNDD", r57["2"])
    s.lab("MUX_SEL", r57["1"], "U", 2.54)
    # --- CAN
    x, y = 76.2, 170.18
    s.text("CAN: MCP2562, jumper-selectable 120R termination, dual SMA outputs", 22.86, 142.24, 1.8, True)
    u = s.sym("Interface_CAN_LIN:MCP2562-E-SN", "U8", "MCP2562T-E/SN", x, y, fp=FP["SOIC8"], mpn="MCP2562T-E/SN")
    s.hl("CAN_TX", u["1"], "input", "L", 7.62)
    s.hl("CAN_RX", u["4"], "output", "L", 7.62)
    s.pwr("+3.3VD", u["5"], "L", 5.08)
    s.pwr("GNDD", u["8"], "L")
    s.pwr("+5V", u["3"]); s.pwr("GNDD", u["2"])
    yH, yL = 167.64, 200.66
    tx = 99.06
    s.w("CANH_T", u["7"], (tx, yH))
    s.w("CANL_T", u["6"], (91.44, u["6"][1]), (91.44, yL), (tx, yL))
    r82 = s.two("R", "R82", "120R 1%", tx, 176.53, horiz=False)
    jp = s.two("", "JP1", "TERM", tx, 190.5, horiz=False, rot=270, lib="Jumper:Jumper_2_Open", fp=FP["H2"])
    s.w("CANH_T", (tx, yH), r82["1"])
    s.w("CAN_TJ", r82["2"], jp["1"])
    s.w("CANL_T", jp["2"], (tx, yL))
    for yy, rr, dd, tv, sm, lbl, nt, ns in ((yH, "R80", "D12", "D13", "SMA6", "CAN-H", "CANH_T", "CANH"),
                                            (yL, "R81", "D14", "D15", "SMA7", "CAN-L", "CANL_T", "CANL")):
        r = s.two("R", rr, "49.9R", 111.76, yy)
        s.w(nt, (tx, yy), r["1"])
        n = 125.73
        d = s.sym("Diode:BAT54S", dd, "BAT54S", n, yy - 7.62, fp=FP["SOT23"], mpn="BAT54S")
        s.w(ns, r["2"], (n, yy)); s.w(ns, (n, yy), d["3"])
        s.pwr("GNDD", d["1"], "L"); s.pwr("+5V", d["2"], "U")
        tvx = n + 12.7
        t = s.sym("Device:D_TVS", tv, "PESD5V0S1BL", tvx, yy + 6.35, rot=270, fp=FP["TVS"], mpn="PESD5V0S1BL",
                  ref_at=(3.3, -1.27, 90, "left"), val_at=(3.3, 1.27, 90, "left"))
        s.w(ns, (n, yy), (tvx, yy), t["1"]); s.pwr("GNDD", t["2"])
        c = s.sym("Connector:Conn_Coaxial", sm, lbl, tvx + 22.86, yy, fp=FP["SMA"], mpn="CONSMA003.062-G")
        s.w(ns, (tvx, yy), c["1"]); s.pwr("GNDD", c["2"])
    s.text("Termination is R82 in SERIES with JP1. Fit shunt = terminated; remove = unterminated demo.", 22.86, 221.0)
    # --- bypass
    yc = 243.84
    s.text("Digital decoupling", 195.58, yc - 12.7, 1.8, True)
    items = [("C15", "100nF", "+3.3VD", "C", "U4"), ("C18", "100nF", "+3.3VD", "C", "U6"), ("C24", "100nF", "+3.3VD", "C", "U9"),
             ("C25", "100nF", "+3.3VD", "C", "U10"), ("C26", "100nF", "+3.3VD", "C", "U11"), ("C17", "100nF", "+3.3VD", "C", "U8 Vio"),
             ("C61", "100nF", "+5V", "C", "U8 VDD"), ("C62", "10uF", "+5V", "CP", "U8 VDD")]
    for n, (ref, v, rail, kind, who) in enumerate(items):
        px = 195.58 + n * 20.32
        c = s.two(kind, ref, v, px, yc, horiz=False)
        s.pwr(rail, c["1"]); s.pwr("GNDD", c["2"])
        s.text(who, px - 5.08, yc + 11.43)
    return s

# ================================================================ DISPLAY
def gen_display():
    s = Sheet("display_interface.kicad_sch", "Display Interface", "Display_Interface",
              ["ILI9488 3.5in TFT, 8-bit parallel, resistive touch on J9 (IDC-24)",
               "Check the J9 pinout against the actual display module before ordering"])
    x, y = 180.34, 91.44
    s.text("Display connector J9", x - 45, y - 30.48, 1.8, True)
    j = s.sym("Connector_Generic:Conn_02x12_Odd_Even", "J9", "ILI9488_IDC24", x, y, fp=FP["IDC24"])
    left = {"3": "LCD_D0", "5": "LCD_D2", "7": "LCD_D4", "9": "LCD_D6", "11": "LCD_CS", "13": "LCD_WR", "15": "LCD_RST"}
    right = {"4": "LCD_D1", "6": "LCD_D3", "8": "LCD_D5", "10": "LCD_D7", "12": "LCD_RS"}
    for p, n in left.items():
        s.hl(n, j[p], "input", "L", 7.62)
    for p, n in right.items():
        s.hl(n, j[p], "input", "R", 7.62)
    s.lab("T_XP", j["17"], "L", 7.62); s.lab("T_YP", j["19"], "L", 7.62)
    s.lab("T_XN", j["18"], "R", 7.62); s.lab("T_YN", j["20"], "R", 7.62)
    s.lab("LCD_RD", j["14"], "R", 7.62); s.lab("BL_K", j["16"], "R", 7.62)
    s.pwr("GNDD", j["1"], "L", 7.62); s.pwr("+3.3VD", j["2"], "R", 7.62)
    s.pwr("GNDD", j["21"], "L", 7.62); s.pwr("GNDD", j["22"], "R", 7.62)
    s.nc(j["23"]); s.nc(j["24"])
    # --- touch
    s.text("Resistive touch: 1k series + 100nF filter", 22.86, 133.35, 1.8, True)
    rows = [("TOUCH_X+", "R102", "C70", "T_XP"), ("TOUCH_X-", "R103", "C71", "T_XN"),
            ("TOUCH_Y+", "R104", "C72", "T_YP"), ("TOUCH_Y-", "R105", "C73", "T_YN")]
    for n, (h, r_, c_, t) in enumerate(rows):
        px = 45.72 + (n % 2) * 91.44
        py = 149.86 + (n // 2) * 30.48
        r = s.two("R", r_, "1k", px, py)
        s.hl(h, r["1"], "input", "L", 7.62)
        nx = px + 10.16
        c = s.two("C", c_, "100nF", nx, py + 6.35, horiz=False)
        s.w(t, r["2"], (nx, py), c["1"])
        s.pwr("GNDD", c["2"])
        s.lab(t, (nx, py), "R", 7.62)
    # --- backlight
    bx, by = 325.12, 76.2
    s.text("Backlight: low-side switch. Module LED anode must be tied to +3.3V on the module.", bx - 50.8, by - 25.4, 1.8, True)
    q_ = s.sym("Transistor_FET:2N7002", "Q2", "2N7002K", bx, by, fp=FP["SOT23"], mpn="2N7002K")
    r100 = s.two("R", "R100", "1k", bx - 17.78, q_["1"][1])
    s.w("BL_G", r100["2"], q_["1"])
    s.hl("LCD_BL", r100["1"], "input", "L", 7.62)
    r101 = s.two("R", "R101", "10R", q_["3"][0], q_["3"][1] - 6.35, horiz=False)
    s.w("BL_D", r101["2"], q_["3"])
    s.lab("BL_K", r101["1"], "U", 2.54)
    s.pwr("GNDD", q_["2"])
    # --- RD pull-up + bypass
    bx2 = 289.56
    s.text("LCD_RD held high (write-only)", bx2 - 7.62, 116.84, 1.8, True)
    r52 = s.two("R", "R52", "10k", bx2, 132.08, horiz=False)
    s.pwr("+3.3VD", r52["1"]); s.lab("LCD_RD", r52["2"], "D", 2.54)
    c74 = s.two("C", "C74", "100nF", bx2 + 30.48, 132.08, horiz=False)
    s.pwr("+3.3VD", c74["1"]); s.pwr("GNDD", c74["2"])
    s.text("J9 bypass", bx2 + 25.4, 143.51)
    return s

# ================================================================ POWER
def gen_power():
    s = Sheet("power_distribution.kicad_sch", "Power Distribution", "Power_Distribution",
              ["+3.3V split to +3.3VA/+3.3VD by ferrite beads; +5V boost for MCP2562",
               "Analog and digital grounds meet only at the R53/R54 star point"])
    for y, fb, c, tp, rail, ttl in ((50.8, "FB1", "C20", "TP8", "+3.3VA", "Analog rail"),
                                    (91.44, "FB2", "C21", "TP9", "+3.3VD", "Digital rail")):
        s.text(ttl, 38.1, y - 17.78, 1.8, True)
        f = s.two("FB", fb, "220R@100MHz", 60.96, y, mpn="ILBB0805ER221V")
        s.pwr("+3.3V", f["1"], "U", 0.0001) if False else None
        s.w("+3.3V", f["1"], (50.8, y)); s.pwr("+3.3V", (50.8, y), "U", 2.54)
        nx = 76.2
        cc = s.two("CP", c, "10uF", nx, y + 6.35, horiz=False)
        s.w(rail, f["2"], (nx, y), cc["1"]); s.pwr("GNDA" if rail == "+3.3VA" else "GNDD", cc["2"])
        t = s.sym("Connector:TestPoint", tp, rail, nx + 12.7, y - 5.08, fp=FP["TP"])
        s.w(rail, (nx, y), (nx + 12.7, y), t["1"])
        s.w(rail, (nx + 12.7, y), (nx + 22.86, y))
        s.pwr(rail, (nx + 22.86, y), "U", 2.54)
    # --- boost
    x, y = 101.6, 149.86
    s.text("+5V boost for MCP2562 VDD: VOUT = 0.5 V x (1 + R55/R56) = 5.05 V", 38.1, y - 22.86, 1.8, True)
    u = s.sym("Regulator_Switching:TPS61220DCK", "U7", "TPS61220DCKR", x, y, fp=FP["SC70"], mpn="TPS61220DCKR",
              ref_at=(-8.89, -7.62, 0), val_at=(3.81, -7.62, 0))
    c22 = s.two("CP", "C22", "10uF", 50.8, y + 2.54, horiz=False)
    l1 = s.two("L", "L1", "4.7uH", 73.66, u["5"][1])
    rail = (60.96, u["5"][1])
    s.w("+3.3V", (50.8, rail[1]), rail, l1["1"])
    s.w("+3.3V", c22["1"], (50.8, rail[1]))
    s.pwr("+3.3V", (50.8, rail[1]), "U", 2.54)
    s.pwr("GNDD", c22["2"])
    s.w("L_SW", l1["2"], u["5"])
    s.w("L_SW", (83.82, u["5"][1]), (83.82, u["5"][1] - 5.08))
    REFS["flg"] += 1
    s.sym("power:PWR_FLAG", "#FLG%03d" % REFS["flg"], "PWR_FLAG", 83.82, u["5"][1] - 5.08)
    b = x - 15.24
    s.w("+3.3V", u["1"], (b, y), (b, u["6"][1]), u["6"])
    s.w("+3.3V", (b, u["6"][1]), (b, y + 7.62), (60.96, y + 7.62), rail)
    s.pwr("GNDD", u["3"])
    nx = x + 22.86
    r55 = s.two("R", "R55", "90.9k 1%", nx, 151.13, horiz=False)
    s.w("+5V", u["4"], (nx, u["4"][1]), r55["1"])
    fbn = (nx, 157.48)
    s.w("FB_5V", u["2"], (x + 12.7, u["2"][1]), (x + 12.7, fbn[1]), fbn)
    s.w("FB_5V", r55["2"], fbn)
    r56 = s.two("R", "R56", "10k 1%", nx, 161.29, horiz=False)
    s.w("FB_5V", fbn, r56["1"]); s.pwr("GNDD", r56["2"])
    cx = nx + 15.24
    c23 = s.two("CP", "C23", "10uF", cx, 151.13, horiz=False)
    s.w("+5V", (nx, u["4"][1]), (cx, u["4"][1]), c23["1"]); s.pwr("GNDD", c23["2"])
    s.w("+5V", (cx, u["4"][1]), (cx + 10.16, u["4"][1]))
    s.pwr("+5V", (cx + 10.16, u["4"][1]), "U", 2.54)
    # --- star
    y = 200.66
    s.text("Ground star point (FRDM GND reaches the board only through R53/R54)", 38.1, y - 17.78, 1.8, True)
    for n, (ref, g) in enumerate((("R53", "GNDA"), ("R54", "GNDD"))):
        px = 66.04 + n * 40.64
        r = s.two("R", ref, "0R", px, y)
        s.pwr("GND", r["1"], "L"); s.pwr(g, r["2"], "R")
    t = s.sym("Connector:TestPoint", "TP10", "GNDA", 149.86, y, fp=FP["TP"])
    s.pwr("GNDA", t["1"], "D", 2.54) if False else None
    s.w("GNDA", t["1"], (149.86, y + 2.54)); s.pwr("GNDA", (149.86, y + 2.54), "D", 2.54)
    # --- flags
    s.text("ERC power flags", 210.82, 33.02, 1.8, True)
    for n, net in enumerate(["+3.3V", "+3.3VA", "+3.3VD", "GND", "GNDA", "GNDD"]):
        s.flag(net, 215.9 + (n % 3) * 30.48, 50.8 + (n // 3) * 22.86)
    return s

# ================================================================ ROOT
# Mating pinout read from the FRDM-MCXN947 schematic (SCH-90818 rev C, sheet 12).
# pin: (MCU pin / function on FRDM, backpack net or None for not connected)
FRDM = {
    "J1": ("Connector_Generic:Conn_02x08_Odd_Even", "FRDM_J1", "PinHeader_2x08", {
        1: ("P3_16", "DDS_D0"), 2: ("P4_3 DAC1_OUT", "DAC1"), 3: ("P4_13 (LCD_D5 on J13)", None),
        4: ("P4_2 DAC0_OUT", "DAC0"), 5: ("P3_20", "DDS_D4"), 6: ("P0_29", "TOUCH_Y-"),
        7: ("P1_21 ENET_MDIO", None), 8: ("P1_23", "DDS_W_CLK"), 9: ("P3_18", "DDS_D2"),
        10: ("P0_30", "DDS_D6"), 11: ("P3_17", "DDS_D1"), 12: ("P1_21 ENET_MDIO", None),
        13: ("P3_19", "DDS_D3"), 14: ("P1_2 LED_BLUE", None), 15: ("P3_21", "DDS_D5"),
        16: ("P0_31", "DDS_D7")}),
    "J2": ("Connector_Generic:Conn_02x10_Odd_Even", "FRDM_J2", "PinHeader_2x10", {
        1: ("ADC1_B0", None), 2: ("P0_28", "MUX_SEL"), 3: ("P5_2", None), 4: ("P0_10 LED_RED", None),
        5: ("P5_3", None), 6: ("P0_27 FC1_P3 (LED_GREEN)", "SPI_CS"), 7: ("P5_4", None),
        8: ("P0_24 FC1_P0", "SPI_MOSI"), 9: ("P0_3 TDI", None), 10: ("P0_26 FC1_P2", "SPI_MISO"),
        11: ("P1_12 CAN1_RXD", "CAN_RX"), 12: ("P0_25 FC1_P1", "SPI_CLK"), 13: ("P0_19", "DDS_FQ_UD"),
        14: ("GND", "GND"), 15: ("P1_1 FC3_P1", "UART_TX"), 16: ("AREF / VDD_ANA", None),
        17: ("P1_0 FC3_P0", "UART_RX"), 18: ("P4_0 FC2_P0", "I2C_SDA"), 19: ("not connected on FRDM", None),
        20: ("P4_1 FC2_P1", "I2C_SCL")}),
    "J3": ("Connector_Generic:Conn_02x08_Odd_Even", "FRDM_J3", "PinHeader_2x08", {
        1: ("P2_0", None), 2: ("ADC0_A3", None), 3: ("P1_22", None), 4: ("IOREF (P3V3)", None),
        5: ("P2_3", "DDS_RESET"), 6: ("RESET_B", None), 7: ("P2_2 PWM1_A2", "PWM2"),
        8: ("P3V3 (700 mA LDO)", "+3.3V"), 9: ("P2_5 PWM1_B1", "LCD_BL"), 10: ("P5V0", None),
        11: ("P2_4 PWM1_A1", "PWM1"), 12: ("GND", "GND"), 13: ("P2_7 PWM1_B0", "PWM3"),
        14: ("GND", "GND"), 15: ("P2_6 PWM1_A0", "PWM0"), 16: ("VIN", None)}),
    "J4": ("Connector_Generic:Conn_02x06_Odd_Even", "FRDM_J4", "PinHeader_2x06", {
        1: ("P4_12 (LCD_D4 on J13)", None), 2: ("ADC0_A0", "ADC_IN"), 3: ("OPAMP0_INN", None),
        4: ("ADC0_B0", None), 5: ("P4_16 CAN1_TXD", "CAN_TX"), 6: ("P0_14 ADC0_B14", "TOUCH_X+"),
        7: ("OPAMP1_INN", None), 8: ("P0_22 ADC0_A14", "TOUCH_Y+"), 9: ("P4_20", None),
        10: ("P0_15", "TOUCH_X-"), 11: ("OPAMP2_INN", None), 12: ("P0_23 WAKEUP_B", None)}),
    "J13": ("Connector_Generic:Conn_02x14_Odd_Even", "FRDM_J8", "PinSocket_2x14", {
        1: ("P3V3", None), 2: ("GND", "GND"), 3: ("P4_1 (I2C on J2)", None), 4: ("P4_0 (I2C on J2)", None),
        5: ("P4_6", None), 6: ("P4_5", "DDS_AUX"), 7: ("P4_7", "LCD_RST"), 8: ("P0_7", "LCD_RS"),
        9: ("P0_12", "LCD_CS"), 10: ("P0_9 FLEXIO0_D1", "LCD_WR"), 11: ("P0_8", None), 12: ("P0_13", None),
        13: ("P2_8 FLEXIO0_D16", "LCD_D0"), 14: ("P2_9 FLEXIO0_D17", "LCD_D1"),
        15: ("P2_10 FLEXIO0_D18", "LCD_D2"), 16: ("P2_11 FLEXIO0_D19", "LCD_D3"),
        17: ("P4_12 FLEXIO0_D20", "LCD_D4"), 18: ("P4_13 FLEXIO0_D21", "LCD_D5"),
        19: ("P4_14 FLEXIO0_D22", "LCD_D6"), 20: ("P4_15 FLEXIO0_D23", "LCD_D7"),
        21: ("P4_16 (CAN on J4)", None), 22: ("P4_17 USB OC", None), 23: ("P4_18", None), 24: ("P4_19", None),
        25: ("P4_20", None), 26: ("P4_21", None), 27: ("P4_22", None), 28: ("P4_23", None)}),
}

def gen_root(subs):
    s = Sheet(PROJECT + ".kicad_sch", "Oscilloscope Training Backpack for FRDM-MCXN947", "",
              ["Board-level interconnect. Sheet nets join by label name.",
               "J1-J4 mate with FRDM J1-J4. J13 mates with FRDM J8.",
               "Pinout from FRDM schematic SCH-90818 rev C sheet 12, default solder jumpers.",
               "Check pin-1 orientation of every mating connector during layout."])
    x = 76.2
    places = (("J1", 45.72, 27.94), ("J2", 91.44, 71.12), ("J3", 139.7, 119.38), ("J4", 177.8, 160.02), ("J13", 226.06, 198.12))
    for ref, y, hy in places:
        lib, val, fpname, pins = FRDM[ref]
        s.text(ref + (" - mates with FRDM J8 (FlexIO LCD)" if ref == "J13" else " - mates with FRDM " + ref), x - 40, hy, 1.8, True)
        if ref == "J13":
            fp = "Connector_PinSocket_2.54mm:PinSocket_2x14_P2.54mm_Vertical"
        else:
            fp = "Connector_PinHeader_2.54mm:%s_P2.54mm_Vertical" % fpname
        j = s.sym(lib, ref, val, x, y, fp=fp)
        for n, (mcu, net) in pins.items():
            pin = j[str(n)]
            side = "L" if n % 2 else "R"
            if net is None:
                s.nc(pin)
            elif net in ("GND", "+3.3V"):
                s.pwr(net, pin, side, 5.08)
            else:
                s.lab(net, pin, side, 5.08)
        lines = ["%d: %s%s" % (n, mcu, "" if net is None else " = " + net) for n, (mcu, net) in sorted(pins.items())]
        half = (len(lines) + 1) // 2
        s.text(chr(10).join(lines[:half]), x + 40, hy + 3.81, 1.0)
        s.text(chr(10).join(lines[half:]), x + 85, hy + 3.81, 1.0)
    return s

def write_lib(out):
    node = local_symbols()["+3.3VD"]
    with open(os.path.join(out, PROJECT + ".kicad_sym"), "w", encoding="utf8", newline="\n") as f:
        f.write('(kicad_symbol_lib\n\t(version 20241209)\n\t(generator "kicad_symbol_editor")\n\t(generator_version "9.0")\n\t%s\n)\n' % dump(node, 1))
    with open(os.path.join(out, "sym-lib-table"), "w", encoding="utf8", newline="\n") as f:
        f.write('(sym_lib_table\n\t(version 7)\n\t(lib (name "%s")(type "KiCad")(uri "${KIPRJMOD}/%s.kicad_sym")(options "")(descr "Project symbols"))\n)\n' % (PROJECT, PROJECT))

def main(out):
    os.makedirs(os.path.join(out, "Schematics"), exist_ok=True)
    subs = [gen_analog(), gen_digital(), gen_display(), gen_power()]
    root = gen_root(subs)
    placements = [(subs[0], 215.9, 30.48), (subs[1], 215.9, 85.09), (subs[2], 317.5, 30.48), (subs[3], 317.5, 106.68)]
    for page, (sub, sx, sy) in enumerate(placements, start=2):
        if sub.hier:
            pins = [(n, sh) for n, sh in sub.hier]
        else:
            pins = []
        spts = root.add_sheet(sub, sx, sy, 50.8, "Schematics/" + sub.fname, page, pins)
        for n, pt in spts:
            root.lab(n, pt, "L", 5.08)
    root.text("Design source: Schematics/README_SCHEMATICS.md (Nov 2025 dual-CAN revision) and COMPLETE_DESIGN_SPEC.md.\n"
              "See SCHEMATIC_NOTES.md for every deviation from those documents and the open items.", 215.9, 200)
    write_lib(out)
    for sh in subs:
        with open(os.path.join(out, "Schematics", sh.fname), "w", encoding="utf8", newline="\n") as f:
            f.write(sh.render())
    with open(os.path.join(out, root.fname), "w", encoding="utf8", newline="\n") as f:
        f.write(root.render())
    # intent netlist
    hier = {n for sh in subs for n, _ in sh.hier}
    glob = {"+3.3V", "+3.3VA", "+3.3VD", "+5V", "GND", "GNDA", "GNDD"}
    intent = {}
    for sh in subs + [root]:
        for net, pins in sh.nets.items():
            key = net if (net in hier or net in glob or not sh.name) else sh.name + "/" + net
            intent.setdefault(key, set()).update(pins)
    with open(os.path.join(out, "intent_netlist.json"), "w") as f:
        json.dump({k: sorted(v) for k, v in intent.items()}, f, indent=0)
    missing = []
    for fp in sorted(ALL_FOOTPRINTS):
        lib, name = fp.split(":")
        if not os.path.exists(os.path.join(KICAD, "footprints", lib + ".pretty", name + ".kicad_mod")):
            missing.append(fp)
    print("footprints missing:", missing)
    print("sheet uuids:", {sh.name: uid("doc:" + sh.name) for sh in subs})

if __name__ == "__main__":
    main(sys.argv[1])
