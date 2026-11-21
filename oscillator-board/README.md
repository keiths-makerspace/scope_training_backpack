# Oscilloscope Training Platform - Header Board

## KiCad Project Files

This directory contains a complete KiCad 6.0+ project for the oscillator section of the Scope Training Platform header board.

### Project Overview

**Board Name:** Oscilloscope Training Platform - Oscillator Section  
**Revision:** 1.0  
**Date:** 2025-01-08  
**Layers:** 4-layer PCB (Signal/GND/+3.3V/Signal)  
**Dimensions:** 70mm x 60mm  
**Purpose:** Socket-based crystal oscillator outputs for scope/logic analyzer training

### Features Implemented

✅ **Dual Socket Crystal Oscillators**
- 2x DIP-4 sockets for user-selectable frequencies (1-200 MHz)
- Enable/disable control via GPIO
- Status LEDs for each oscillator
- Bypass capacitors for clean power

✅ **Signal Conditioning**
- Series damping resistors (47Ω) for clean edges
- Test points for easy probing
- 2-pin headers for signal output
- Provisions for SMA connectors (footprints ready)

✅ **Power Distribution**
- Dedicated +3.3V supply with filtering
- Solid GND plane (Layer 2)
- Power plane (Layer 3)
- Star-point grounding strategy

### File Structure

```
scope_training_header/
├── scope_training_header.kicad_pro    # KiCad project file
├── scope_training_header.kicad_sch    # Schematic
├── scope_training_header.kicad_pcb    # PCB layout
└── README.md                          # This file
```

## Opening the Project

### Requirements
- **KiCad 6.0 or later** (tested with 6.0.11)
- Download from: https://www.kicad.org/download/

### Steps

1. **Clone or download** this directory to your computer

2. **Open KiCad** and select "File → Open Project"

3. **Navigate** to `scope_training_header.kicad_pro` and open it

4. **View the schematic:**
   - Click "Schematic Editor" icon
   - You'll see the complete circuit with both oscillators

5. **View the PCB layout:**
   - Click "PCB Editor" icon
   - Press `3` for 3D view to see the board in 3D

## Schematic Details

### Oscillator 1 Circuit
```
GPIO_EN → R1 (10k pulldown) → U1 Pin 1 (Enable)
                              U1 Pin 4 (VCC) ← +3.3V via C1 (0.1µF)
                              U1 Pin 2 (GND) → GND
                              U1 Pin 3 (OUT) → R2 (47Ω) → TP1 → J1A → OSC1_OUT
                                             → R3 (330Ω) → LED1 → GND
```

### Oscillator 2 Circuit
```
GPIO_EN → R4 (10k pulldown) → U2 Pin 1 (Enable)
                              U2 Pin 4 (VCC) ← +3.3V via C2 (0.1µF)
                              U2 Pin 2 (GND) → GND
                              U2 Pin 3 (OUT) → R5 (47Ω) → TP2 → J1B → OSC2_OUT
                                             → R6 (330Ω) → LED2 → GND
```

### Net List
- **Net 1:** GND (ground plane)
- **Net 2:** +3.3V (power plane)
- **Net 3:** OSC1_EN (enable input from MCU)
- **Net 4:** OSC2_EN (enable input from MCU)
- **Net 5:** OSC1_OUT (output signal 1)
- **Net 6:** OSC2_OUT (output signal 2)

## PCB Layout Details

### Component Placement

**Oscillator 1 Section** (Top half)
- U1 (Socket): 100mm, 80mm
- R1 (10k): 90mm, 78.73mm
- C1 (0.1µF): 104.19mm, 73mm
- R2 (47Ω): 108mm, 81.27mm
- R3 (330Ω): 112mm, 81.27mm
- LED1: 112mm, 85mm
- TP1: 112mm, 73mm
- J1A: 120mm, 75mm

**Oscillator 2 Section** (Bottom half)
- U2 (Socket): 100mm, 105mm
- R4 (10k): 90mm, 103.73mm
- C2 (0.1µF): 104.19mm, 98mm
- R5 (47Ω): 108mm, 106.27mm
- R6 (330Ω): 112mm, 106.27mm
- LED2: 112mm, 110mm
- TP2: 112mm, 98mm
- J1B: 120mm, 100mm

### Layer Stackup
```
Layer 1 (F.Cu):    Top copper - Signal routing, components
Layer 2 (In1.Cu):  Inner layer 1 - Solid GND plane
Layer 3 (In2.Cu):  Inner layer 2 - +3.3V power plane
Layer 4 (B.Cu):    Bottom copper - Signal routing, ground
```

### Design Rules
- **Minimum trace width:** 0.2mm (0.008")
- **Minimum clearance:** 0.2mm (0.008")
- **Via size:** 0.8mm diameter, 0.4mm drill
- **RF traces (50Ω):** 1.2mm width
- **Power traces:** 0.5mm width

### Critical Routing
- **C1, C2 to oscillator VCC:** < 5mm trace length
- **R2, R5 to oscillator OUT:** < 5mm trace length
- **Output signals:** 1.2mm width (50Ω controlled impedance)
- **Test points:** Direct connection via copper pours

## Bill of Materials (BOM)

| Ref | Value | Package | Qty | Description |
|-----|-------|---------|-----|-------------|
| U1, U2 | SOCKET | DIP-4 | 2 | IC socket for oscillator |
| R1, R4 | 10k | 0603 | 2 | Pull-down resistor |
| R2, R5 | 47 | 0603 | 2 | Series damping resistor |
| R3, R6 | 330 | 0603 | 2 | LED current limiting |
| C1, C2 | 0.1µF | 0603 | 2 | Bypass capacitor |
| LED1, LED2 | Green | 0603 | 2 | Status indicator |
| TP1, TP2 | Test Point | 2mm pad | 2 | Oscilloscope probe point |
| J1A, J1B | 2-pin | Header 2.54mm | 2 | Output connector |

**Total component cost: ~$5** (excluding oscillators)

### Compatible Oscillators (User-Supplied)
- **Type:** 3.3V CMOS output, DIP-4 package
- **Frequency range:** 1-200 MHz
- **Examples:** 
  - SG-8002DC series (Epson)
  - ASE series (Abracon)
  - ECS-xxxx series
- **Cost:** $2-3 each

## Manufacturing

### Gerber Generation

1. Open PCB in KiCad
2. File → Plot
3. Select layers:
   - F.Cu, B.Cu, In1.Cu, In2.Cu
   - F.SilkS, B.SilkS
   - F.Mask, B.Mask
   - Edge.Cuts
4. Click "Plot"
5. Click "Generate Drill Files"
6. Zip all files and submit to manufacturer

### Recommended Manufacturers
- **JLCPCB** - $20 for 5 boards (4-layer)
- **PCBWay** - $25 for 5 boards (4-layer)
- **OSH Park** - $5/sq in (slower, high quality)

### Specifications to Provide
- **Layers:** 4
- **Dimensions:** 70mm x 60mm
- **Thickness:** 1.6mm
- **Copper weight:** 1 oz (35µm)
- **Surface finish:** ENIG or HASL lead-free
- **Silkscreen:** White on green solder mask
- **Min trace/space:** 6/6 mil (0.15mm)

## Assembly Instructions

### Step 1: Solder SMD Components First
Order (smallest to largest):
1. Resistors (R1-R6)
2. Capacitors (C1-C2)
3. LEDs (LED1-LED2) - **Watch polarity!**

**LED Polarity:**
- Cathode (marked) faces LEFT (toward oscillator)
- Use silkscreen marking as guide

### Step 2: Install Through-Hole Components
1. IC sockets (U1, U2) - **Pin 1 to marked corner!**
2. Headers (J1A, J1B)
3. Test points (TP1, TP2) if using through-hole type

### Step 3: Testing Before Oscillator Installation
1. Apply +3.3V to board
2. Verify voltage at socket pin 4: should be ~3.3V
3. Verify socket pin 2 is GND: 0V
4. Check enable pins default LOW: 0V

### Step 4: Install Oscillators
1. Check oscillator pinout in datasheet
2. Align Pin 1 (marked with dot) to socket Pin 1
3. Insert gently - don't bend pins
4. Write frequency on PCB with marker

### Step 5: Function Test
1. Enable oscillator (drive EN pin HIGH)
2. LED should illuminate
3. Measure output on test point with scope
4. Verify frequency matches oscillator marking

## Usage

### Connection to FRDM-MCXN947

| Signal | FRDM Pin | Header Pin |
|--------|----------|-----------|
| OSC1_EN | P1_20 | J1A Pin 1 |
| OSC2_EN | P1_21 | J1B Pin 1 |
| OSC1_OUT | Input | J1A Pin 1 |
| OSC2_OUT | Input | J1B Pin 1 |
| +3.3V | +3.3V | Multiple |
| GND | GND | Multiple |

### Software Control Example

```c
// Enable oscillator 1
GPIO_PinWrite(GPIO, 1, 20, 1);  // OSC1_EN = HIGH
delay_ms(10);  // Allow startup time

// Measure output frequency
// Connect OSC1_OUT to scope/LA
```

### Frequency Selection Guide

**For General Training:**
- OSC1: 25 MHz (reference frequency)
- OSC2: 50 MHz (high-speed digital)

**For Harmonic Analysis:**
- OSC1: 25 MHz
- OSC2: 50 MHz (shows 2x harmonic relationship)

**For Vintage CPU Emulation:**
- OSC1: 4 MHz (Commodore 64, Apple II)
- OSC2: 8 MHz (PC XT, Z80 systems)

**For Maximum Range:**
- OSC1: 10 MHz (low-mid frequency)
- OSC2: 100-200 MHz (high-speed testing)

## Modifications and Customization

### Adding SMA Connectors

1. **Footprints are ready** at J2A and J2B positions
2. **Part:** Linx CONSMA003.062 or equivalent
3. **Mounting:** Edge-mount female SMA
4. **Connect:** Parallel with 2-pin headers

### Adding Buffer IC

1. **Footprint ready** for 74HC541 (U3)
2. **Purpose:** Drive multiple outputs
3. **Placement:** Between R2/R5 and output
4. **Benefit:** No load degradation

### Higher Frequency Support

Current design supports up to **200 MHz** with:
- 50Ω controlled impedance traces
- Proper bypass capacitors
- Series damping resistors

For **>200 MHz**, consider:
- Shorter traces (<10mm to output)
- Better ground stitching
- RF-rated components

## Troubleshooting

### LED doesn't light
- Check enable signal (should be 3.3V when ON)
- Verify LED polarity (cathode to GND)
- Check R3/R6 value (should be 330Ω)

### No output signal
- Oscillator installed backwards?
- Check oscillator datasheet pinout
- Verify +3.3V at socket pin 4
- Measure at socket pin 3 directly

### Weak/distorted signal
- Use 10X scope probe (not 1X)
- Check damping resistor (R2/R5 = 47Ω)
- Reduce trace length
- Check ground connection quality

### Wrong frequency
- Verify oscillator part number
- Check if using crystal (need oscillator module)
- Some oscillators have tolerance marking

## Future Enhancements

Planned for v2.0:
- [ ] Si5351 clock generator IC footprint
- [ ] Avalanche pulse generator circuit
- [ ] Additional power filtering options
- [ ] SMA connectors as standard
- [ ] Frequency mixing demo circuit

## License

This is an open-source hardware project for educational purposes.

**License:** CC BY-SA 4.0 (Creative Commons Attribution-ShareAlike)

You are free to:
- **Share** — copy and redistribute
- **Adapt** — remix, transform, and build upon
- **Commercial use** — yes, allowed

Under the terms:
- **Attribution** — give appropriate credit
- **ShareAlike** — distribute under same license

## Support and Community

### Resources
- **Project GitHub:** [Link to be added]
- **Hackaday Project:** [Link to be added]
- **Discussion Forum:** [Link to be added]

### Contributing
Pull requests welcome! Areas needing help:
- Additional training examples
- Software drivers
- 3D printed enclosure design
- Testing with different oscillators

### Author
Created for the DIY Oscilloscope Training Platform project.

**Contact:** [Your contact info]

## Changelog

### v1.0 (2025-01-08)
- Initial release
- Dual socket oscillator design
- Status LEDs and test points
- 4-layer PCB with power planes
- Ready for manufacturing

---

**Happy Building! 🎓🔬**

For questions or issues, please open a GitHub issue or contact the project maintainer.
