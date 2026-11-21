# Schematic notes (rev 2.0, 2026-11-04)

The project documents disagree with each other and, in places, with the part
datasheets. This file records what the schematic actually does and why.

**Files:** `scope_training_backpack.kicad_sch` (root), `Schematics/*.kicad_sch`
(4 sub-sheets), `scope_training_backpack.kicad_sym` + `sym-lib-table` (adds the
`+3.3VD` power symbol). The previous files are in `archive_pre_schematic/`.

`tools/generate_schematic.py` created these files. Re-running it against the
project folder overwrites anything edited by hand in KiCad.

## Decide before PCB layout

1. **Board fit.** J1-J4 and J13 follow the FRDM schematic, but the schematic does
   not give connector positions. Before layout, check the spacing and pin-1
   orientation of all five against the real board or its drawing. In particular,
   check that FRDM J8 lies under the 90 x 65 mm outline. J13's mating part needs
   to clear the FRDM's other parts when stacked.
2. **Which SMA plan?** The schematic follows the newest document (Nov 2025):
   SMA6/SMA7 = CAN-H/CAN-L. The ADC input is on header J10, and the amplified
   DDS output has its own SMA8. The Jan 2025 spec and PIN_REFERENCE.md have
   SMA6 = DDS, SMA7 = ADC, and a CAN screw terminal.
3. **Display pinout.** J9 follows the Nov 2025 IDC-24 pin list. Check it against
   the module you will buy. The backlight assumes the module ties the LED anode
   to +3.3V and exposes the cathode on J9-16.

## FRDM pin map (use this for firmware)

From `Schematics/90818-MCXN947SH.pdf` (SCH-90818 rev C), sheet 12, with the solder
jumpers as drawn by default (SJ side A). This replaces the J1/J2 tables and every
MCU pin listed in PIN_REFERENCE.md, COMPLETE_DESIGN_SPEC.md and the archived sheets.
Backpack J1-J4 mate with FRDM J1-J4; backpack J13 mates with FRDM J8.

| Signal | MCU pin | Header | Function |
|---|---|---|---|
| DAC0 | P4_2 | J1.4 | DAC0_OUT |
| DAC1 | P4_3 | J1.2 | DAC1_OUT |
| ADC_IN | ADC0_A0 | J4.2 | ADC0 channel A0 |
| PWM0 | P2_6 | J3.15 | PWM1_A0 |
| PWM1 | P2_4 | J3.11 | PWM1_A1 |
| PWM2 | P2_2 | J3.7 | PWM1_A2 |
| PWM3 | P2_7 | J3.13 | PWM1_B0 (shares a submodule with PWM0) |
| CAN_TX | P4_16 | J4.5 | CAN1_TXD |
| CAN_RX | P1_12 | J2.11 | CAN1_RXD |
| SPI_CLK | P0_25 | J2.12 | FC1 |
| SPI_MOSI | P0_24 | J2.8 | FC1 |
| SPI_MISO | P0_26 | J2.10 | FC1 |
| SPI_CS | P0_27 | J2.6 | FC1 (also drives the green LED) |
| I2C_SDA | P4_0 | J2.18 | FC2 |
| I2C_SCL | P4_1 | J2.20 | FC2 |
| UART_TX | P1_1 | J2.15 | FC3_P1 |
| UART_RX | P1_0 | J2.17 | FC3_P0 |
| MUX_SEL | P0_28 | J2.2 | GPIO |
| LCD_D0-D3 | P2_8-P2_11 | J13.13-16 | FLEXIO0_D16-D19 |
| LCD_D4-D7 | P4_12-P4_15 | J13.17-20 | FLEXIO0_D20-D23 |
| LCD_RS | P0_7 | J13.8 | GPIO |
| LCD_WR | P0_9 | J13.10 | FLEXIO0_D1 |
| LCD_CS | P0_12 | J13.9 | GPIO |
| LCD_RST | P4_7 | J13.7 | GPIO |
| LCD_BL | P2_5 | J3.9 | PWM1_B1 |
| TOUCH_X+ | P0_14 | J4.6 | ADC0_B14 |
| TOUCH_Y+ | P0_22 | J4.8 | ADC0_A14 |
| TOUCH_X- | P0_15 | J4.10 | GPIO |
| TOUCH_Y- | P0_29 | J1.6 | GPIO |
| DDS_D0-D5 | P3_16-P3_21 | J1.1, 11, 9, 13, 5, 15 | GPIO |
| DDS_D6, D7 | P0_30, P0_31 | J1.10, J1.16 | GPIO |
| DDS_W_CLK | P1_23 | J1.8 | GPIO |
| DDS_FQ_UD | P0_19 | J2.13 | GPIO |
| DDS_RESET | P2_3 | J3.5 | GPIO |
| DDS_AUX | P4_5 | J13.6 | GPIO |
| +3.3V | P3V3 | J3.8 | FRDM LDO, 700 mA maximum |
| GND | - | J2.14, J3.12, J3.14, J13.2 | |

Why these pins:

- **CAN1, not CAN0.** The FRDM's own TJA1057 sits on CAN0, so the backpack's
  MCP2562 uses CAN1 and the two can't conflict.
- **FlexIO LCD.** J8 is NXP's LCD header, and D16-D23 are consecutive, so the
  display can use FlexIO instead of bit-banging.
- **Shared pins checked.** P4_2/P4_3 (MCU-Link UART), P1_0/P1_1 (MCU-Link SPI),
  P4_0/P4_1 (USB CC controller) and P4_16 (USB power switch) link to those
  circuits through parts marked DNP on the schematic.
- **Avoided.** P1_21 (Ethernet MDIO), P1_2 and P0_10 (LEDs), P0_23 (wake button)
  and P4_17 (USB fault output).
- **Assumptions to check in the MCX N94x reference manual.** FC3_P0 = RXD and
  FC3_P1 = TXD is inferred from how the FRDM uses FC4. FC1 pin roles come from
  the FRDM net names.
- **SD card and mikroBUS.** P2_2-P2_7 are shared with the unpopulated SD socket,
  and P3_19-P3_21 with mikroBUS, so those can't be used at the same time.

**+5 V source.** J3.10 (P5V0) is left open and U7 still makes +5V. P5V0 comes
through a Schottky diode, so it sits below 5 V; that leaves little margin above
the MCP2562's 4.5 V minimum. It also has no boost ripple, so it's an option if
U7 proves noisy or short of current. Never connect J3.10 to +5V with U7 fitted.

## Changes from the documents

| Item | Documents say | Schematic does | Why |
|---|---|---|---|
| MCP2562 VDD | +3.3VD | **+5V** from U7; Vio stays +3.3VD | VDD needs 4.5-5.5 V; the documented 2.5 V recessive level also implies 5 V |
| MCP2562 CANH/CANL | Spec: pins 6/7 | Pin 7 = CANH, pin 6 = CANL | Library symbol pinout; sheet text agrees |
| MCP6002 supply | Pin 4 VDD, pin 8 VSS | Pin 8 V+, pin 4 V- | Library symbol pinout |
| 74HC541 pins | Non-sequential list | A0-A7 (2-9) to Y0-Y7 (18-11) | Listed pins are not all inputs |
| 74HC4053 count | 1 chip, 11-12 signals | **4 chips** (U6, U9, U10, U11) | Each chip has only 3 channels |
| LA channels 8-11 | Not defined | PWM0-PWM3 | Sheet text calls for PWM on the LA port |
| J5 pin 14 | Not defined | Mux channel 12 (DDS_AUX / PWM3) | Uses the 12th channel and R49 |
| J5 +5V | Spec has it; Nov list does not | Not present | Follows Nov list; AD9851 module gets 3.3 V, so check it runs at your clock |
| U7 parts | No inductor or divider listed | L1 4.7 uH, C22, C23, R55, R56 | Required by the part; 5.05 V output |
| R13 (99k) | Single 99k | R13 + R58 + R59 = 98.99k | Matches the 95.3k, 3.3k and 390R on the Mouser BOM (inferred) |
| DAC1 divider | "10:1" | 10k/1k, really about 11:1 (300 mV) | Values kept |
| PWM filter | Sheet: 10k + 10 uF "1 kHz" | 1k + 100 nF (1.6 kHz) | 10k + 10 uF is 1.6 Hz |
| CAN termination | Drawing shows JP1 across R82 | R82 in series with JP1 | Drawn version could not switch termination |
| Backlight | Sheet: drain to LED anode | Low side, drain to LED cathode | Sheet version reverses the LED |
| LCD_RD | Sheet: MCU pin; spec: pull-up | R52 pull-up | Root sheet has no RD signal |
| DDS amplifier | MCP6002 I-to-V, 0.01 Hz-70 MHz | OPA355 (U12) voltage gain of 2, 10 Hz-20 MHz, SMA8; U3A tied off | 1 MHz op-amp cannot do this; range and 1 V level set by the project owner |
| Added | - | R57 pull-down on MUX_SEL | Defaults to logic-analyzer mode at reset |
| Omitted | R27-R34 22R (optional) | Not fitted | Optional; not on the BOM |

## Known limitations (kept as documented)

- **U4 is one-way.** J6 MISO, J8 RX and J7 SDA/SCL only monitor. An external
  device on those headers cannot drive the MCU. Say if they should be real ports.
- **Op-amp bandwidth.** MCP6002 is 1 MHz, so the "DC-2 MHz" DAC1 claim will not
  be met, and fast edges on the runt and PWM buffers are slew-limited.
- **DAC AC coupling.** C1/C2 do nothing while R1/R3 are fitted. With those
  removed, the buffer input has no DC bias.
- **Touch series resistors.** R102-R105 (1k) are in the drive path and will
  reduce measurement span.
- **Footprints to check.** SMA uses a Samtec edge-mount footprint as a stand-in
  for CONSMA003.062-G. U4 uses the library's 74LS541 symbol (same pinout) with
  the SSOP-20 footprint for the purchased SN74HC541DBR, not the TSSOP in the spec.
  Confirm the D13/D15 package against the PESD5V0S1BL variant you buy.
- **Boost current.** U7 now feeds U12 as well as the MCP2562. Its 200 mA minimum
  switch limit works out to very roughly 110 mA at 5 V from 3.3 V (estimate).
  Check this against the datasheet's maximum-output-current graph and the
  MCP2562 dominant-state current, and measure the +5V ripple at SMA8.
- **DDS amplifier.** Assumes about 1 Vpp from the module, which varies with
  module and load, so measure yours; above about 1 Vpp the output runs out of
  headroom. Firmware must limit the range to 10 Hz-20 MHz. R60/R61 = 1k is a
  starting value not taken from the OPA355 datasheet. Confirm OPA355 limits
  (supply, input range, output swing) in TI's PDF: only secondary listings were
  available. C28's 47 uF assumes about 33 uF after DC-bias derating.

## MouserBOM.xls compared with the schematic

| Part | On BOM | Needed | Action |
|---|---|---|---|
| 0603ZC103 "0.1 uF" | 20 | 18 (+2 DNP) | **Wrong value: this part is 10 nF.** Replace with 100 nF |
| CD74HC4053PWR | 1 | 4 | Add 3 |
| 100R | 12 | 15 | Add 3 |
| 1k | 10 | 12 (+1 DNP) | Add 3 |
| 10k | 5 | 7 (+1 DNP) | Add 3 |
| 10 uF tantalum | 6 | 10 | Add 4 |
| BAT54S | 1 | 3 | Add 2 |
| Ferrite bead | 2 | 3 | Add 1 |
| SMA edge-mount | 7 | 8 | Add 1 |
| OPA355 (SOT-23-6) | 0 | 1 | Add |
| 10 uF ceramic 0805 (C27) | 0 | 1 | Add |
| 47 uF ceramic 1206 (C28) | 0 | 1 | Add |
| 220 uF 6.3 V tantalum (C32) | 0 | 1 | Add |
| PESD5V0S1BL | 0 | 2 | Add |
| 49.9R | 0 | 2 | Add |
| 120R 1% | 0 | 1 | Add |
| 10R | 0 | 1 | Add |
| 90.9k 1% | 0 | 1 | Add |
| 4.7 uH inductor | 0 | 1 | Add |
| Connectors and headers (except SMA) | 0 | J1-J10, J12, J13, JP1 | Add. J1-J4 are stacking 2x8, 2x10, 2x8, 2x6 pin headers; J13 is a 2x14 socket |
| 4.7k | 1 | 0 | Not used |

## Verification

- KiCad 9.0.6 ERC with all severities: 0 violations.
- `tools/verify_schematic.py`: KiCad's netlist matches the generator's intended
  nets, and the signal-path and power rules pass.
- KiCad 10.0.6: the netlist is identical to KiCad 9's. Its command-line ERC gave
  only library warnings (428, "configuration does not include the symbol library"),
  because no global library tables were set up for 10.0 here; a control project
  showed the same warning types. A clean KiCad 10 ERC has not been seen yet.
- Not done: comparison with a physical FRDM board or display, simulation, or PCB
  layout. MCP2562 and MCP6002 pin data comes from the KiCad libraries. TPS61220
  pinout and feedback voltage were checked against TI's datasheet.
