# COMPLETE DESIGN SPECIFICATION
## Oscilloscope Training Backpack for FRDM-MCXN947

**Project Status:** Design Specification Complete - Ready for Schematic Implementation  
**Version:** 1.0  
**Date:** 2025-01-08

---

## 🎯 DESIGN SUMMARY

**Board Type:** FRDM-MCXN947 Arduino-compatible backpack  
**Dimensions:** 90mm x 65mm (matches FRDM footprint)  
**Layers:** 4-layer PCB (Top Signal / GND / +3.3V / Bottom Signal)  
**Assembly:** All SMD components except Arduino stackable headers  
**Estimated Cost:** $35-40 per board (PCB + components, excluding display)

### Key Features:
- ✅ 6x SMA analog outputs (DAC0, DAC1, PWM, Runt, Mixed, AD9851)
- ✅ 1x SMA analog input (ADC for DSP processing)
- ✅ CAN bus with MCP2562 transceiver + screw terminal
- ✅ 16-pin IDC (software-switched AD9851 or Logic Analyzer mode)
- ✅ Protocol headers (SPI, I2C, UART)
- ✅ ILI9488 3.5" display interface (20-pin)
- ✅ All signals buffered/protected
- ✅ Separate analog/digital power domains

---

## 📐 COMPLETE CIRCUIT ARCHITECTURE

### SECTION 1: ANALOG OUTPUT STAGE

#### 1.1 DAC0 Output Chain → SMA1
```
FRDM DAC0 (P4_30, 12-bit, 1MSPS)
  ↓
  0.1µF AC coupling cap (optional, 0Ω bypass)
  ↓
  MCP6002A Pin 1 (Non-inverting input)
  ↓
  MCP6002A Pin 2 (Unity gain buffer)
  ↓
  47Ω series resistor (damping)
  ↓
  Test Point (TP1)
  ↓
  SMA1 Output Connector (edge-mount)
  ↓
  Signal range: 0-3.3V, DC-500kHz
```

**Component Values:**
- C1: 0.1µF (0603) - AC coupling (optional)
- R1: 0Ω (0603) - Bypass jumper
- R2: 47Ω (0603) - Series damping
- U1: MCP6002 (SOIC-8) - Dual op-amp

#### 1.2 DAC1 Output Chain → SMA2
```
FRDM DAC1 (P4_31, 14-bit, 5MSPS)
  ↓
  0.1µF AC coupling cap (optional, 0Ω bypass)
  ↓
  MCP6002A Pin 5 (Non-inverting input)
  ↓
  MCP6002A Pin 7 (Unity gain buffer)
  ↓
  47Ω series resistor (damping)
  ↓
  Voltage divider (selectable):
    Option A: 0Ω (full 3.3V output)
    Option B: 10:1 divider (330mV output for small signal training)
      R=10kΩ to output, R=1kΩ to GND
  ↓
  Test Point (TP2)
  ↓
  SMA2 Output Connector
  ↓
  Signal range: 0-3.3V or 0-330mV, DC-2MHz
```

**Component Values:**
- C2: 0.1µF (0603) - AC coupling
- R3: 0Ω (0603) - Bypass jumper
- R4: 47Ω (0603) - Series damping
- R5: 10kΩ (0603) - Divider top (optional)
- R6: 1kΩ (0603) - Divider bottom (optional)
- R7: 0Ω (0603) - Bypass divider

#### 1.3 PWM Filtered Output → SMA3
```
FRDM PWM0 (P0_24, up to 200kHz)
  ↓
  RC Low-pass filter:
    R = 1kΩ (0603)
    C = 100nF (0603)
    Cutoff = 1.6kHz
  ↓
  MCP6002B Pin 3 (Non-inverting input)
  ↓
  MCP6002B Pin 1 (Unity gain buffer)
  ↓
  47Ω series resistor
  ↓
  Test Point (TP3)
  ↓
  SMA3 Output Connector
  ↓
  Use: DC levels, slow ramps, filtered square waves
```

**Component Values:**
- R8: 1kΩ (0603) - Filter resistor
- C3: 100nF (0603) - Filter capacitor
- R9: 47Ω (0603) - Series damping
- U2: MCP6002 (SOIC-8) - Dual op-amp

#### 1.4 Runt/Glitch Generator → SMA4
```
FRDM PWM1 (P0_25)
  ↓
  Runt generator network:
    Path 1: Direct → Fast edge
    Path 2: R-C (100Ω + 10pF) → Slowed edge
    Combine at summing point
  ↓
  Creates incomplete voltage swing (runt pulse)
  ↓
  MCP6002B Pin 5 (Non-inverting input)
  ↓
  MCP6002B Pin 7 (Buffer)
  ↓
  47Ω series resistor
  ↓
  Test Point (TP4)
  ↓
  SMA4 Output Connector
```

**Component Values:**
- R10: 100Ω (0603) - Runt path resistor
- C4: 10pF (0603) - Runt path capacitor
- R11: 100Ω (0603) - Combining resistor
- R12: 47Ω (0603) - Series damping

#### 1.5 Mixed/Glitch Output → SMA5
```
FRDM PWM2 (P0_26)
  ↓
  Selectable paths (via 0Ω resistor placement):
  
  Path A: Small signal generator
    100:1 voltage divider
    R = 99kΩ, R = 1kΩ
    Output: 10-33mV range
  
  Path B: Glitch generator
    Fast edge network
    R-C differentiator
  
  Path C: Direct PWM
    Straight through, 0Ω
  ↓
  47Ω series resistor
  ↓
  Test Point (TP5)
  ↓
  SMA5 Output Connector
```

**Component Values:**
- R13: 99kΩ (0603) - Small signal divider (Path A)
- R14: 1kΩ (0603) - Small signal divider (Path A)
- R15: 0Ω (0603) - Path A select
- R16: 100Ω (0603) - Glitch network (Path B)
- C5: 22pF (0603) - Glitch network (Path B)
- R17: 0Ω (0603) - Path B select
- R18: 0Ω (0603) - Path C select (direct)
- R19: 47Ω (0603) - Series damping

#### 1.6 AD9851 DDS Output → SMA6
```
16-pin IDC Header (shared with Logic Analyzer)
  ↓
  AD9851 Module (external)
    IOUT pin (current output, 10mA typical)
  ↓
  I-to-V Converter:
    MCP6002C Pin 1 (Transimpedance amp)
    Feedback R = 390Ω
    Converts 10mA → 3.9V signal
  ↓
  Voltage divider (if needed):
    Adjust to 0-3.3V range
  ↓
  47Ω series resistor
  ↓
  Test Point (TP6)
  ↓
  SMA6 Output Connector
  ↓
  Signal: Clean sine wave, 0.01Hz to 70MHz
```

**Component Values:**
- R20: 390Ω (0603) - Transimpedance feedback
- R21: 10kΩ (0603) - Optional divider
- R22: 3.3kΩ (0603) - Optional divider
- R23: 47Ω (0603) - Series damping
- U3: MCP6002 (SOIC-8) - Third dual op-amp (one half used)

#### 1.7 ADC Input for DSP → SMA7
```
SMA7 Input Connector (edge-mount)
  ↓
  Input protection:
    Schottky diodes to +3.3V and GND
    BAT54S (SOT-23)
  ↓
  Series resistor (current limiting):
    R = 1kΩ (0603)
  ↓
  RC filter (anti-aliasing):
    R = 1kΩ (0603)
    C = 100pF (0603)
    Cutoff ≈ 1.6MHz
  ↓
  MCP6002C Pin 5 (Buffer)
  ↓
  MCP6002C Pin 7 (Unity gain output)
  ↓
  Test Point (TP7)
  ↓
  FRDM ADC Input (ADC0_SE0, P4_0)
  ↓
  Voltage range: 0-3.3V (protected)
  Bandwidth: DC-1MHz (filtered)
```

**Component Values:**
- D1: BAT54S (SOT-23) - Dual Schottky protection diodes
- R24: 1kΩ (0603) - Input current limit
- R25: 1kΩ (0603) - Filter resistor
- C6: 100pF (0603) - Anti-aliasing filter
- R26: 10kΩ (0603) - Pull-down to define floating input

### Op-Amp Power Supply Decoupling:
```
Each MCP6002:
  Pin 4 (VDD): +3.3VA via ferrite bead
  Pin 8 (VSS): GNDA
  
  Local bypass capacitors:
    C7, C10, C13: 0.1µF (0603) ceramic, close to VDD pin
    C8, C11, C14: 10µF (0805) tantalum, nearby
```

---

### SECTION 2: DIGITAL PROTOCOL INTERFACE

#### 2.1 74HC541 Octal Buffer
```
Purpose: Protect MCU pins from logic analyzer loading

Input Side (MCU):
  SPI_CLK    → 74HC541 Pin 2  → Buffered → Pin 18
  SPI_MOSI   → Pin 3  → Buffered → Pin 17
  SPI_MISO   → Pin 5  → Buffered → Pin 15
  SPI_CS     → Pin 6  → Buffered → Pin 14
  I2C_SDA    → Pin 8  → Buffered → Pin 12
  I2C_SCL    → Pin 9  → Buffered → Pin 11
  UART_TX    → Pin 11 → Buffered → Pin 9
  UART_RX    → Pin 12 → Buffered → Pin 8

Control:
  Pin 1 (OE1#): Tied to GND (always enabled)
  Pin 19 (OE2#): Tied to GND (always enabled)
  Pin 10 (GND): Ground
  Pin 20 (VCC): +3.3VD
```

**Component Values:**
- U4: 74HC541 (TSSOP-20)
- C15: 0.1µF (0603) - VCC bypass
- R27-R34: 22Ω (0603) - Series resistors on outputs (optional)

#### 2.2 Protocol Pin Headers (0.1" pitch)

**SPI Header (5-pin):**
```
Pin 1: SPI_CLK  (buffered from 74HC541)
Pin 2: SPI_MOSI (buffered)
Pin 3: SPI_MISO (buffered)
Pin 4: SPI_CS   (buffered)
Pin 5: GND
```

**I2C Header (3-pin):**
```
Pin 1: I2C_SDA (buffered, with 2.2kΩ pull-up to +3.3V)
Pin 2: I2C_SCL (buffered, with 2.2kΩ pull-up to +3.3V)
Pin 3: GND
```

**Pull-up Resistors:**
- R35: 2.2kΩ (0603) - SDA pull-up
- R36: 2.2kΩ (0603) - SCL pull-up

**UART Header (3-pin):**
```
Pin 1: UART_TX (buffered)
Pin 2: UART_RX (buffered)
Pin 3: GND
```

#### 2.3 CAN Bus Interface

**MCP2562 CAN Transceiver:**
```
MCU Side:
  FRDM CAN_TX (P1_18) → MCP2562 Pin 1 (TXD)
  FRDM CAN_RX (P1_19) ← MCP2562 Pin 4 (RXD)

Bus Side:
  MCP2562 Pin 6 (CANH) → Screw Terminal Pin 1
  MCP2562 Pin 7 (CANL) → Screw Terminal Pin 2
  
Power:
  Pin 3 (VDD): +3.3VD via ferrite bead
  Pin 2 (VSS): GND
  Pin 5 (Vio): +3.3VD (logic level reference)
  Pin 8 (STBY): Tied to GND (normal mode)

Termination:
  120Ω resistor between CANH and CANL
  Selectable via jumper (2-pin header + shunt)
```

**Component Values:**
- U5: MCP2562 (SOIC-8)
- C16: 0.1µF (0603) - VDD bypass
- C17: 0.1µF (0603) - Vio bypass
- R37: 120Ω (0603) - CAN termination
- J3: 3-pin screw terminal (3.5mm pitch)
- JP1: 2-pin header (termination select)

**Screw Terminal Pinout:**
```
Pin 1: CAN_H (yellow wire typical)
Pin 2: CAN_L (green wire typical)
Pin 3: GND (black wire)
```

#### 2.4 16-Pin IDC Dual-Mode Interface

**Software-Controlled Mode Selection using 74HC4053:**
```
74HC4053 Triple 2-channel analog multiplexer

Mode Select Signal from MCU:
  MUX_SEL (GPIO) → 74HC4053 Pin 9 (A, B, C control)
  
  LOW  = Logic Analyzer mode (all 12 signals to IDC)
  HIGH = AD9851 mode (12 parallel data/control signals)

Channel Routing:
  Each signal has two paths:
    Path 0: To 74HC541 output (LA mode)
    Path 1: To AD9851 interface (DDS mode)
```

**IDC-16 Pin Assignment:**
```
Pin 1:  D0/LA_CH0   (switchable)
Pin 2:  D1/LA_CH1
Pin 3:  D2/LA_CH2
Pin 4:  D3/LA_CH3
Pin 5:  D4/LA_CH4
Pin 6:  D5/LA_CH5
Pin 7:  D6/LA_CH6
Pin 8:  D7/LA_CH7
Pin 9:  W_CLK/LA_CH8
Pin 10: FQ_UD/LA_CH9
Pin 11: RESET/LA_CH10
Pin 12: GND
Pin 13: +5V (for AD9851, if needed)
Pin 14: +3.3V
Pin 15: GND
Pin 16: GND
```

**Component Values:**
- U6: 74HC4053 (TSSOP-16) - Triple analog mux
- C18: 0.1µF (0603) - VCC bypass
- R38-R49: 100Ω (0603) - Series resistors on mux outputs

---

### SECTION 3: DISPLAY INTERFACE

#### 3.1 ILI9488 3.5" TFT Connection (20-pin header)

**8-bit Parallel Data Bus:**
```
Pin 1:  LCD_D0 (FRDM P0_0)
Pin 2:  LCD_D1 (FRDM P0_1)
Pin 3:  LCD_D2 (FRDM P0_2)
Pin 4:  LCD_D3 (FRDM P0_3)
Pin 5:  LCD_D4 (FRDM P0_4)
Pin 6:  LCD_D5 (FRDM P0_5)
Pin 7:  LCD_D6 (FRDM P0_6)
Pin 8:  LCD_D7 (FRDM P0_7)
```

**Control Signals:**
```
Pin 9:  LCD_RS  (Register Select, FRDM P0_8)
Pin 10: LCD_WR  (Write Strobe, FRDM P0_9)
Pin 11: LCD_CS  (Chip Select, FRDM P0_10)
Pin 12: LCD_RST (Reset, FRDM P0_11)
Pin 13: LCD_RD  (Read, tied HIGH via 10kΩ - write-only mode)
```

**Backlight Control:**
```
Pin 14: LCD_BL (Backlight control)
  ↓
  Current limiting resistor: R50 = 10Ω (0603)
  ↓
  2N7002 MOSFET Gate (SOT-23)
    Source: GND
    Drain: LED cathode
    Gate: PWM signal via 1kΩ resistor
  ↓
  LED Anode: +3.3V via current limit
  
Backlight PWM from FRDM (P0_12)
  → R51 = 1kΩ (0603) gate resistor
  → 2N7002 Gate
```

**Component Values:**
- Q1: 2N7002 (SOT-23) - N-channel MOSFET
- R50: 10Ω (0603) - LED current limit
- R51: 1kΩ (0603) - Gate resistor
- R52: 10kΩ (0603) - LCD_RD pull-up

#### 3.2 Resistive Touch Controller

**4-Wire Resistive Touch Interface:**
```
Touch signals connected to FRDM ADC:

Pin 15: TOUCH_X+ (FRDM ADC0_SE1, P4_1) - Drive/Measure
Pin 16: TOUCH_X- (FRDM GPIO P0_13)    - GND when measuring
Pin 17: TOUCH_Y+ (FRDM ADC0_SE2, P4_2) - Drive/Measure
Pin 18: TOUCH_Y- (FRDM GPIO P0_14)    - GND when measuring
```

**Measurement Sequence:**
1. X-axis: Drive X+, GND X-, measure Y+
2. Y-axis: Drive Y+, GND Y-, measure X+

**Power Pins:**
```
Pin 19: +3.3VD
Pin 20: GND
```

**Component Values:**
- J4: 20-pin female header (2x10, 2.54mm pitch)
- C19: 0.1µF (0603) - Power bypass near header

---

### SECTION 4: POWER DISTRIBUTION

#### 4.1 Power Input from FRDM

**Arduino Headers:**
```
J1 (Left Header):
  Pin 1:  GND
  Pin 2:  +3.3V (from FRDM)
  Pin 3:  DAC0 signal
  Pin 4:  DAC1 signal
  Pin 5:  PWM0 signal
  Pin 6:  PWM1 signal
  Pin 7:  PWM2 signal
  Pin 8:  PWM3 signal (spare)
  Pin 9:  GND
  Pin 10: +3.3V

J2 (Right Header):
  Pin 1:  CAN_TX
  Pin 2:  CAN_RX
  Pin 3:  SPI_CLK
  Pin 4:  SPI_MOSI
  Pin 5:  SPI_MISO
  Pin 6:  SPI_CS
  Pin 7:  I2C_SDA
  Pin 8:  I2C_SCL
  Pin 9:  UART_TX
  Pin 10: UART_RX
```

#### 4.2 Power Splitting and Filtering

**Analog Power Domain:**
```
+3.3V_IN (from FRDM)
  ↓
  Ferrite Bead: BLM18PG221SN1D (220Ω @100MHz)
  ↓
  Bulk capacitor: C20 = 10µF (0805) tantalum
  ↓
  +3.3VA (Analog power rail)
  ↓
  Distributed to: MCP6002 op-amps, analog circuits
  
  Local bypass caps at each IC:
    0.1µF ceramic + 10µF tantalum
```

**Digital Power Domain:**
```
+3.3V_IN (from FRDM)
  ↓
  Ferrite Bead: BLM18PG221SN1D (220Ω @100MHz)
  ↓
  Bulk capacitor: C21 = 10µF (0805) tantalum
  ↓
  +3.3VD (Digital power rail)
  ↓
  Distributed to: 74HC541, 74HC4053, MCP2562, display
  
  Local bypass caps at each IC:
    0.1µF ceramic
```

**+5V Generation (for AD9851 if needed):**
```
+3.3V_IN
  ↓
  Optional: TPS61220 boost converter (SOT-23-6)
    Boost to +5V @ 200mA
  ↓
  OR: External +5V input from IDC connector
  ↓
  +5V rail (available on IDC-16 Pin 13)
```

**Component Values:**
- FB1, FB2: BLM18PG221SN1D (0603) - Ferrite beads
- C20, C21: 10µF (0805) - Bulk tantalum capacitors
- C22-C40: 0.1µF (0603) - Bypass capacitors (one per IC)
- U7: TPS61220 (SOT-23-6) - Optional boost converter

#### 4.3 Ground Architecture

**Star-Point Ground Strategy:**
```
Single ground connection point on Arduino header
  ↓
  Split into two domains on PCB:
  
  GNDA (Analog Ground):
    - MCP6002 op-amps
    - SMA connector shields
    - Analog signal returns
    - Layer 2 copper pour (analog section)
  
  GNDD (Digital Ground):
    - Digital ICs (74HC541, 74HC4053, MCP2562)
    - Display ground
    - Protocol header grounds
    - Layer 2 copper pour (digital section)
  
  Connection:
    GNDA and GNDD joined at star point via 0Ω resistor
    Allows measurement of ground current if needed
```

---

## 📊 COMPLETE BILL OF MATERIALS

### Active Components:

| Ref | Value | Package | Qty | Part Number | Cost | Description |
|-----|-------|---------|-----|-------------|------|-------------|
| U1, U2, U3 | MCP6002 | SOIC-8 | 3 | MCP6002-I/SN | $3.00 | Dual op-amp, rail-to-rail |
| U4 | 74HC541 | TSSOP-20 | 1 | 74HC541PW | $0.40 | Octal buffer |
| U5 | MCP2562 | SOIC-8 | 1 | MCP2562-E/SN | $0.80 | CAN transceiver |
| U6 | 74HC4053 | TSSOP-16 | 1 | 74HC4053PW | $0.60 | Triple analog mux |
| U7 | TPS61220 | SOT-23-6 | 1 | TPS61220DCKR | $1.50 | Boost converter (optional) |
| Q1 | 2N7002 | SOT-23 | 1 | 2N7002K | $0.20 | N-channel MOSFET |
| D1 | BAT54S | SOT-23 | 1 | BAT54S | $0.30 | Dual Schottky diode |

**Active Components Total: $6.80** (or $8.30 with boost converter)

### Passive Components (0603 unless noted):

**Resistors:**
| Value | Qty | Purpose |
|-------|-----|---------|
| 47Ω | 7 | SMA series damping |
| 100Ω | 12 | Runt circuits, mux outputs |
| 390Ω | 1 | AD9851 I-to-V feedback |
| 1kΩ | 10 | Filters, dividers, gate resistor |
| 2.2kΩ | 2 | I2C pull-ups |
| 3.3kΩ | 1 | Voltage divider (optional) |
| 10kΩ | 5 | Dividers, pull-ups, pull-downs |
| 99kΩ | 1 | Small signal divider |
| 0Ω | 10 | Jumpers for path selection |

**Total Resistors: ~50 pcs, Cost: ~$2.50**

**Capacitors:**
| Value | Package | Qty | Purpose |
|-------|---------|-----|---------|
| 10pF | 0603 | 2 | Runt circuits, filters |
| 22pF | 0603 | 1 | Glitch circuit |
| 100pF | 0603 | 3 | Anti-aliasing filters |
| 0.1µF | 0603 | 20 | Bypass capacitors, coupling |
| 10µF | 0805 | 6 | Bulk capacitors (tantalum) |

**Total Capacitors: ~32 pcs, Cost: ~$3.00**

**Ferrite Beads:**
| Value | Qty | Purpose |
|-------|-----|---------|
| 220Ω @100MHz | 2 | Power domain separation |

**Cost: ~$0.50**

### Connectors:

| Ref | Type | Qty | Part Number | Cost | Notes |
|-----|------|-----|-------------|------|-------|
| SMA1-7 | SMA edge-mount | 7 | CONSMA003.062 | $14.00 | Signal I/O |
| J1, J2 | Arduino headers | 2 | Stackable female | $4.00 | To FRDM |
| J3 | Screw terminal 3-pin | 1 | Generic 3.5mm | $0.40 | CAN bus |
| J4 | Pin header 2x10 | 1 | Female 2.54mm | $1.50 | Display |
| J5 | IDC-16 shrouded | 1 | 2x8 box header | $1.20 | AD9851/LA |
| J6-J8 | Pin header 1x5, 1x3, 1x3 | 3 | Male 2.54mm | $0.90 | Protocols |
| JP1 | Pin header 1x2 | 1 | Male 2.54mm | $0.10 | CAN term select |
| TP1-7 | Test points | 7 | SMD pad or pin | $0.00 | 0603 pads |

**Connectors Total: $22.10**

### Hardware:

| Item | Qty | Cost | Notes |
|------|-----|------|-------|
| Jumper shunts | 10 | $1.00 | For 0Ω resistor positions |
| Jumper shunt | 1 | $0.10 | CAN termination select |

**Hardware Total: $1.10**

---

## 💰 TOTAL COST BREAKDOWN

| Category | Cost |
|----------|------|
| Active ICs | $6.80 |
| Passive Components | $6.00 |
| Connectors | $22.10 |
| Hardware | $1.10 |
| **Subtotal (components)** | **$36.00** |
| PCB (4-layer, 5 pcs from JLCPCB) | $25.00 |
| **Cost per board** | **$41.00** |

**Not included:**
- ILI9488 display module: ~$15
- AD9851 DDS module: ~$10 (optional)
- Assembly labor (if outsourcing)

---

## 📍 FRDM-MCXN947 PIN ASSIGNMENTS

### Analog Signals:
| Function | FRDM Pin | Arduino Pin | Notes |
|----------|----------|-------------|-------|
| DAC0 | P4_30 | J1-3 | 12-bit DAC output |
| DAC1 | P4_31 | J1-4 | 14-bit DAC output |
| ADC_IN | P4_0 (ADC0_SE0) | J2-11 | DSP input, 0-3.3V |

### PWM Signals:
| Function | FRDM Pin | Arduino Pin | Notes |
|----------|----------|-------------|-------|
| PWM0 | P0_24 | J1-5 | Filtered output |
| PWM1 | P0_25 | J1-6 | Runt generator |
| PWM2 | P0_26 | J1-7 | Mixed/glitch |
| PWM3 | P0_27 | J1-8 | Spare/future |

### Digital Protocols:
| Function | FRDM Pin | Arduino Pin | Notes |
|----------|----------|-------------|-------|
| SPI_CLK | P1_0 | J2-3 | SPI clock |
| SPI_MOSI | P1_1 | J2-4 | SPI data out |
| SPI_MISO | P1_2 | J2-5 | SPI data in |
| SPI_CS | P1_3 | J2-6 | SPI chip select |
| I2C_SDA | P1_8 | J2-7 | I2C data (bidirectional) |
| I2C_SCL | P1_9 | J2-8 | I2C clock |
| UART_TX | P1_24 | J2-9 | UART transmit |
| UART_RX | P1_25 | J2-10 | UART receive |
| CAN_TX | P1_18 | J2-1 | CAN transmit |
| CAN_RX | P1_19 | J2-2 | CAN receive |

### Display Interface:
| Function | FRDM Pin | Notes |
|----------|----------|-------|
| LCD_D0-D7 | P0_0 - P0_7 | 8-bit data bus |
| LCD_RS | P0_8 | Register select |
| LCD_WR | P0_9 | Write strobe |
| LCD_CS | P0_10 | Chip select |
| LCD_RST | P0_11 | Reset |
| LCD_BL | P0_12 | Backlight PWM |

### Touch Interface:
| Function | FRDM Pin | Notes |
|----------|----------|-------|
| TOUCH_X+ | P4_1 (ADC0_SE1) | X+ drive/measure |
| TOUCH_X- | P0_13 (GPIO) | X- ground |
| TOUCH_Y+ | P4_2 (ADC0_SE2) | Y+ drive/measure |
| TOUCH_Y- | P0_14 (GPIO) | Y- ground |

### Control Signals:
| Function | FRDM Pin | Notes |
|----------|----------|-------|
| MUX_SEL | P0_15 (GPIO) | AD9851/LA mode select |

### AD9851/Logic Analyzer (16-pin IDC):
| Function | FRDM Pin | IDC Pin | Notes |
|----------|----------|---------|-------|
| D0 | P0_16 | 1 | Parallel data bit 0 |
| D1 | P0_17 | 2 | Parallel data bit 1 |
| D2 | P0_18 | 3 | Parallel data bit 2 |
| D3 | P0_19 | 4 | Parallel data bit 3 |
| D4 | P0_20 | 5 | Parallel data bit 4 |
| D5 | P0_21 | 6 | Parallel data bit 5 |
| D6 | P0_22 | 7 | Parallel data bit 6 |
| D7 | P0_23 | 8 | Parallel data bit 7 |
| W_CLK | P0_28 | 9 | AD9851 word clock |
| FQ_UD | P0_29 | 10 | AD9851 frequency update |
| RESET | P0_30 | 11 | AD9851 reset |

**Total GPIO used: 42 pins**  
**MCXN947 has 100+ GPIO, plenty available for expansion**

---

## 🎨 PCB LAYOUT GUIDELINES

### Board Dimensions:
- **Size:** 90mm x 65mm
- **Mounting holes:** 4x M3 at corners (3mm diameter)
- **Corner radius:** 3mm
- **Edge clearance:** 5mm from components to edge

### Layer Stackup (4-layer):
```
Layer 1 (Top):     Signal + Components
                   Thickness: 35µm copper (1 oz)
                   
Prepreg:           FR-4 dielectric
                   
Layer 2 (Inner 1): Ground Plane (GNDA + GNDD)
                   Thickness: 35µm copper (1 oz)
                   Split into analog/digital zones
                   
Core:              FR-4 dielectric
                   
Layer 3 (Inner 2): Power Plane (+3.3VA + +3.3VD + +5V)
                   Thickness: 35µm copper (1 oz)
                   Split into power domains
                   
Prepreg:           FR-4 dielectric
                   
Layer 4 (Bottom):  Signal + Ground returns
                   Thickness: 35µm copper (1 oz)

Total thickness: 1.6mm standard
```

### Component Placement Strategy:

**Front Edge (SMA Connectors):**
```
Left to Right:
[SMA7-IN] [SMA1] [SMA2] [SMA3] [SMA4] [SMA5] [SMA6]
  ADC     DAC0   DAC1    PWM    RUNT   MIX    DDS
  
Spacing: 15mm centers (standard for edge-mount SMA)
Total width: ~105mm edge connector zone
```

**Top Surface Layout:**
```
┌─────────────────────────────────────────────┐
│ [SMA connectors across front edge]         │
│                                             │
│  U1        U2       U3      Display Header │
│ MCP6002  MCP6002  MCP6002    (J4 2x10)     │
│ (DACs)   (PWM)    (AD9851)                 │
│                                             │
│  U4        U5       U6       IDC-16        │
│ 74HC541  MCP2562  74HC4053   (J5)          │
│ (Buffer)  (CAN)    (Mux)                   │
│                                             │
│  Protocol Headers:    CAN Terminal         │
│  [SPI] [I2C] [UART]   [J3]                 │
│                                             │
│  Passive components distributed around ICs │
│  Test points near each SMA output          │
│                                             │
│ ○○○○○○○○○○  Arduino Headers  ○○○○○○○○○○     │
│    J1                            J2        │
└─────────────────────────────────────────────┘
```

### Critical Routing Rules:

**Analog Signals (DAC, ADC):**
- Trace width: 0.3mm minimum
- Keep traces short (<50mm)
- Route on top layer when possible
- Guard with GND traces on either side
- Avoid crossing digital signals
- Reference to GNDA plane only

**PWM Signals:**
- Trace width: 0.25mm
- Can cross layers via stitching vias
- Reference to GNDD plane

**SMA Output Traces:**
- Trace width: 1.2mm (50Ω controlled impedance)
- Keep length <25mm from IC to SMA center pin
- Solid GND plane underneath (no voids)
- GND via stitching around trace (0.5mm spacing)

**CAN Bus (Differential):**
- Trace width: 0.35mm each trace
- Spacing: 0.2mm between traces
- Keep parallel and length-matched
- Route as differential pair
- Reference to GNDD plane
- Total length <150mm

**Display Parallel Bus:**
- Trace width: 0.2mm
- Length matching not critical (low speed)
- Can route on both layers
- Group by function

**Power Traces:**
- +3.3VA: 0.5mm width minimum
- +3.3VD: 0.5mm width minimum
- GND: Pour entire plane
- Use thermal relief pads for hand soldering

### Via Specifications:
- Standard via: 0.6mm diameter, 0.3mm drill
- Power via: 0.8mm diameter, 0.4mm drill
- Via in pad: Avoid if possible (or filled/tented)

### Ground Plane Strategy:
```
Layer 2 Ground Plane:

┌─────────────────────────────────────────────┐
│ GNDA (Analog Ground)                        │
│ ┌─────────────────────┐                     │
│ │ Op-amps, SMA shields│                     │
│ │ Analog circuits     │    Separation       │
│ │                     │    (0.5mm gap)      │
│ │                     │                     │
│ └─────────────────────┘  ╱╲  Star Point     │
│                          ╱  ╲               │
│ GNDD (Digital Ground)   ╱    ╲              │
│ ┌─────────────────────────────────────────┐ │
│ │ Digital ICs, protocols, display         │ │
│ │                                         │ │
│ │                                         │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘

Star point at Arduino header ground pin
```

### Silkscreen Guidelines:
- Component references: 0.8mm height
- Values: Optional (reference BOM)
- Pin 1 indicators: Dot + square pad
- SMA labels: Large, clear (2mm height)
- Signal names at connectors
- Company/project name on bottom
- "Freq:___ MHz" write-in areas near AD9851

### Solder Mask:
- Color: Green (standard)
- Finish: Matte
- Clearance: 0.1mm from pads
- Tenting: Via tenting on top and bottom

### Surface Finish:
- **Recommended:** ENIG (Electroless Nickel Immersion Gold)
  - Best for SMD assembly
  - Flat surface
  - Long shelf life
- **Alternative:** HASL lead-free (cheaper, less flat)

---

## 🔧 ASSEMBLY SEQUENCE

### Phase 1: SMD Components (Smallest First)
1. Passive components (0603): Resistors, capacitors
2. SOT-23 devices: Q1, D1
3. SOIC-8 devices: U1, U2, U3, U5
4. TSSOP devices: U4, U6
5. SOT-23-6: U7 (if using boost converter)

### Phase 2: Through-Hole Components
1. SMA connectors (7x) - Edge mount, solder from top
2. Arduino stackable headers (2x) - Bottom side
3. Protocol pin headers (J6, J7, J8)
4. Display header (J4)
5. IDC-16 header (J5)
6. Screw terminal (J3)
7. Jumper headers (JP1, path selectors)

### Phase 3: Inspection and Testing
1. Visual inspection with magnification
2. Continuity testing (adjacent pins)
3. Power supply test (no shorts)
4. Power-on with current limiting
5. Voltage measurements at test points

### Phase 4: Functional Testing
1. Analog outputs (oscilloscope verification)
2. Digital protocols (logic analyzer verification)
3. Display interface (test pattern)
4. Touch calibration
5. Full system integration test

---

## 📖 NEXT STEPS TO COMPLETE DESIGN

### Option A: Complete in KiCad Yourself
1. Use this specification document
2. Open the root schematic I created
3. Create the four sub-sheets with detailed circuits
4. Place components on PCB following layout guidelines
5. Route according to critical routing rules
6. Generate Gerbers and order

**Estimated time:** 8-12 hours for experienced user

### Option B: Have Me Complete Specific Sections
In follow-up sessions, I can create:
- Detailed analog output schematic (Section 1)
- Digital protocols schematic (Section 2)
- Display interface schematic (Section 3)
- Power distribution schematic (Section 4)
- Complete PCB layout

**Each section:** 30-45 minutes

### Option C: Professional Completion
- Send this specification to PCB design service
- They can complete in 20-40 hours
- Cost: $500-1500 depending on service
- Receive tested, verified design

---

## 📚 REFERENCE DOCUMENTS

### Datasheets Required:
1. **MCP6002** - Microchip dual op-amp
2. **74HC541** - NXP octal buffer
3. **MCP2562** - Microchip CAN transceiver
4. **74HC4053** - NXP triple analog mux
5. **TPS61220** - TI boost converter
6. **ILI9488** - Display controller
7. **FRDM-MCXN947** - NXP dev board schematic

### Application Notes:
- AN1679: PCB Layout for High-Speed Digital
- AN2934: CAN Bus Physical Layer Design
- AN1259: Analog Signal Integrity
- AN3005: Display Interface Design

---

## ✅ DESIGN VERIFICATION CHECKLIST

Before manufacturing:
- [ ] All component values verified
- [ ] Pin assignments match FRDM-MCXN947
- [ ] Power calculations done (current draw <500mA)
- [ ] Thermal analysis (no components >70°C)
- [ ] Signal integrity simulation (critical paths)
- [ ] DRC (Design Rule Check) passes
- [ ] ERC (Electrical Rule Check) passes
- [ ] BOM complete with part numbers
- [ ] Manufacturing files generated (Gerbers, drill, BOM)
- [ ] Assembly drawings created
- [ ] Test procedures documented

---

**END OF DESIGN SPECIFICATION**

This document provides complete circuit design details for implementing the KiCad schematic and PCB layout. All component values, connections, and layout guidelines are specified.

**Version:** 1.0  
**Date:** 2025-01-08  
**Status:** Ready for Implementation
