#!/usr/bin/env python3
"""Compare KiCad's exported netlist with intent_netlist.json and design rules.

Usage: verify_schematic.py NETLIST.net INTENT.json
Exit status is non-zero if anything disagrees.
"""
import json, re, sys

def kicad_nets(path):
    t = open(path, encoding="utf8").read()
    nets = {}
    for block in re.split(r'\(net \(code', t)[1:]:
        name = re.search(r'\(name "((?:[^"\\]|\\.)*)"\)', block).group(1)
        nodes = re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', block)
        nodes = {r + "." + p for r, p in nodes if not r.startswith("#")}
        nets[name] = nodes
    return nets

def main(net_path, intent_path):
    actual = kicad_nets(net_path)
    intent = {k: {p for p in v if not p.startswith("#")} for k, v in json.load(open(intent_path)).items()}
    A = {frozenset(v) for v in actual.values() if len(v) > 1}
    # merge intent nets that share a pin (a pin can be recorded under one name only once)
    I = [set(v) for v in intent.values() if v]
    changed = True
    while changed:
        changed = False
        for i in range(len(I)):
            for j in range(i + 1, len(I)):
                if I[i] & I[j]:
                    I[i] |= I.pop(j)
                    changed = True
                    break
            if changed:
                break
    I = {frozenset(v) for v in I if len(v) > 1}
    bad = 0
    for v in sorted(I - A, key=sorted):
        print("INTENDED BUT NOT IN KICAD:", sorted(v)); bad += 1
    for v in sorted(A - I, key=sorted):
        print("IN KICAD BUT NOT INTENDED:", sorted(v)); bad += 1

    # Independent design rules, written from the datasheets rather than the layout code.
    def same(*pins):
        return any(all(p in v for p in pins) for v in actual.values())
    named = lambda net, *pins: all(p in actual.get(net, ()) for p in pins)
    rules = {
        "MCP6002 V+ on +3.3VA (pin 8)": named("+3.3VA", "U1.8", "U2.8", "U3.8"),
        "MCP6002 V- on GNDA (pin 4)": named("GNDA", "U1.4", "U2.4", "U3.4"),
        "U1A/U2A/U3A followers": all(same(u + ".1", u + ".2") for u in ("U1", "U2", "U3")),
        "U1B/U2B/U3B followers": all(same(u + ".7", u + ".6") for u in ("U1", "U2", "U3")),
        "DAC0 path": same("J1.4", "R1.1") and same("R1.2", "U1.3") and same("U1.1", "R2.1") and same("R2.2", "TP1.1", "SMA1.1"),
        "DAC1 path": same("J1.2", "R3.1") and same("R3.2", "U1.5") and same("U1.7", "R4.1") and same("R7.2", "TP2.1", "SMA2.1"),
        "PWM0 path": same("J3.15", "R8.1") and same("R8.2", "C3.1", "U2.3") and same("U2.1", "R9.1") and same("R9.2", "TP3.1", "SMA3.1"),
        "PWM1 path": same("J3.11", "R10.1", "R11.1") and same("R11.2", "C4.2", "U2.5") and same("R12.2", "TP4.1", "SMA4.1"),
        "PWM2 path": same("J3.7", "R13.1", "R18.1", "C5.1") and same("R15.2", "R17.2", "R18.2", "R19.1") and same("R19.2", "TP5.1", "SMA5.1"),
        "ADC path": same("J10.1", "R26.1", "D1.3", "R24.1") and same("R25.2", "C6.1", "U3.5") and same("U3.7", "TP7.1", "J4.2"),
        "D1 clamps to +3.3VA/GNDA": named("+3.3VA", "D1.2") and named("GNDA", "D1.1"),
        "SMA1-5 shells GNDA": named("GNDA", *["SMA%d.2" % i for i in (1, 2, 3, 4, 5, 8)]),
        "MCP2562 VDD on +5V, VSS GNDD": named("+5V", "U8.3") and named("GNDD", "U8.2"),
        "MCP2562 Vio on +3.3VD, STBY low": named("+3.3VD", "U8.5") and named("GNDD", "U8.8"),
        "CAN TX/RX": same("J4.5", "U8.1") and same("J2.11", "U8.4"),
        "CANH (pin 7) to SMA6": same("U8.7", "R80.1", "R82.1") and same("R80.2", "D12.3", "D13.1", "SMA6.1"),
        "CANL (pin 6) to SMA7": same("U8.6", "R81.1", "JP1.2") and same("R81.2", "D14.3", "D15.1", "SMA7.1"),
        "Termination is series R82+JP1": same("R82.2", "JP1.1") and not same("R82.1", "R82.2"),
        "U4 enabled and powered": named("GNDD", "U4.1", "U4.19", "U4.10") and named("+3.3VD", "U4.20"),
        "U4 A0..A7 map to Y0..Y7": all(same("J2.%d" % h, "U4.%d" % (k + 2)) for k, h in enumerate((12, 8, 10, 6, 18, 20, 15, 17))),
        "I2C pull-ups on MCU side": same("R50.2", "J2.18") and same("R51.2", "J2.20") and named("+3.3VD", "R50.1", "R51.1"),
        "J6/J7/J8 from U4 outputs": same("U4.18", "J6.2") and same("U4.15", "J6.5") and same("U4.14", "J7.2") and same("U4.13", "J7.3") and same("U4.12", "J8.2") and same("U4.11", "J8.3"),
        "Mux supply/INH": all(named("GNDD", u + ".6", u + ".7", u + ".8") and named("+3.3VD", u + ".16") for u in ("U6", "U9", "U10", "U11")),
        "Mux selects tied, pulled down": all(same("J2.2", u + ".9", u + ".10", u + ".11") for u in ("U6", "U9", "U10", "U11")) and same("J2.2", "R57.1") and named("GNDD", "R57.2"),
        "IDC0 mux path": same("U6.14", "R38.2") and same("R38.1", "J5.3") and same("U6.12", "U4.18"),
        "IDC11 mux path": same("U11.4", "R49.2") and same("R49.1", "J5.14") and same("U11.5", "J3.13"),
        "J5 power": named("+3.3VD", "J5.1") and named("GNDD", "J5.2", "J5.15", "J5.16"),
        "J9 power": named("+3.3VD", "J9.2") and named("GNDD", "J9.1", "J9.21", "J9.22"),
        "LCD_RD pulled high, no MCU": same("R52.2", "J9.14") and named("+3.3VD", "R52.1"),
        "Backlight low-side": same("J9.16", "R101.1") and same("R101.2", "Q2.3") and named("GNDD", "Q2.2") and same("Q2.1", "R100.2"),
        "Touch X+": same("R102.2", "C70.1", "J9.17"),
        "Touch Y-": same("R105.2", "C73.1", "J9.20"),
        "DDS input and bias": same("J12.1", "C27.1") and same("C27.2", "R64.1", "U12.3") and same("R64.2", "R62.2", "R63.1", "C29.1") and named("GNDA", "J12.2", "R63.2", "C29.2"),
        "DDS gain of 2": same("U12.4", "R60.1", "R61.2") and same("U12.1", "R60.2", "C32.1", "C33.1") and same("R61.1", "C28.1") and named("GNDA", "C28.2"),
        "DDS supply filtered": named("+5V", "FB3.1") and same("FB3.2", "U12.6", "U12.5", "R62.1", "C30.1", "C31.1") and named("GNDA", "U12.2", "C30.2", "C31.2"),
        "DDS output": same("C32.2", "C33.2", "R65.1", "R23.1") and same("R23.2", "TP6.1", "SMA8.1") and named("GNDA", "R65.2", "SMA8.2"),
        "Boost": named("+3.3V", "U7.1", "U7.6", "L1.1") and same("L1.2", "U7.5") and named("+5V", "U7.4", "R55.1", "C23.1") and same("U7.2", "R55.2", "R56.1") and named("GNDD", "U7.3", "R56.2"),
        "Rails": named("+3.3V", "FB1.1", "FB2.1", "J3.8") and named("+3.3VA", "FB1.2", "C20.1", "TP8.1") and named("+3.3VD", "FB2.2", "C21.1", "TP9.1"),
        "Star ground": named("GND", "R53.1", "R54.1", "J2.14", "J3.12", "J3.14", "J13.2") and named("GNDA", "R53.2") and named("GNDD", "R54.2"),
    }
    # FRDM mating table, retyped from SCH-90818 sheet 12 (independent of the generator).
    rules["LCD data on FlexIO D16-D23"] = all(same("J13.%d" % a, "J9.%d" % b) for a, b in
        ((13, 3), (14, 4), (15, 5), (16, 6), (17, 7), (18, 8), (19, 9), (20, 10)))
    rules["LCD control"] = same("J13.9", "J9.11") and same("J13.8", "J9.12") and same("J13.10", "J9.13") and same("J13.7", "J9.15") and same("J3.9", "R100.1")
    rules["Touch"] = same("J4.6", "R102.1") and same("J4.10", "R103.1") and same("J4.8", "R104.1") and same("J1.6", "R105.1")
    rules["DDS control and data"] = all(same(h, u + "." + p) for h, u, p in (
        ("J1.1", "U6", "13"), ("J1.11", "U6", "1"), ("J1.9", "U6", "3"), ("J1.13", "U9", "13"),
        ("J1.5", "U9", "1"), ("J1.15", "U9", "3"), ("J1.10", "U10", "13"), ("J1.16", "U10", "1"),
        ("J1.8", "U10", "3"), ("J2.13", "U11", "13"), ("J3.5", "U11", "1"), ("J13.6", "U11", "3")))
    rules["Pins with FRDM functions stay open"] = not any(p in v for v in actual.values() if len(v) > 1
        for p in ("J3.10", "J3.16", "J13.1", "J2.16", "J3.4", "J3.6", "J4.12", "J2.4", "J1.14", "J1.7", "J1.12", "J2.19"))
    for k, ok in rules.items():
        print(("ok   " if ok else "FAIL ") + k)
        bad += 0 if ok else 1
    print("nets:", len(actual), "components checked; problems:", bad)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
