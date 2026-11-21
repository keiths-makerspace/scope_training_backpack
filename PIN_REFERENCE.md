# QUICK REFERENCE CARD
## FRDM-MCXN947 Oscilloscope Training Backpack
## Pin Assignments and Signal Reference

**Version:** 1.0 | **Date:** 2025-01-08

---

## 🔌 SMA CONNECTORS (All Edge-Mount)

| Connector | Signal | Source | Frequency Range | Amplitude | Notes |
|-----------|--------|--------|-----------------|-----------|-------|
| **SMA1** | DAC0 OUT | FRDM DAC0 (P4_30) | DC-500kHz | 0-3.3V | General waveforms |
| **SMA2** | DAC1 OUT | FRDM DAC1 (P4_31) | DC-2MHz | 0-3.3V / 0-330mV | Precision, optional 10:1 |
| **SMA3** | PWM FILT | FRDM PWM0 (P0_24) | DC-1kHz | 0-3.3V | RC filtered PWM |
| **SMA4** | RUNT GEN | FRDM PWM1 (P0_25) | Pulses | Partial swing | Signal integrity |
| **SMA5** | MIXED | FRDM PWM2 (P0_26) | Variable | 10mV-3.3V | Selectable paths |
| **SMA6** | AD9851 | Via IDC-16 | 0.01Hz-70MHz | 0-3.3V | DDS clean sine |
| **SMA7** | ADC IN | To FRDM ADC (P4_0) | DC-1MHz | 0-3.3V max | DSP input, protected |

---

## 📍 ARDUINO HEADER PINOUT

### J1 (Left Header) - 10 pins
```
Pin 1:  GND
Pin 2:  +3.3V IN (from FRDM)
Pin 3:  DAC0 (P4_30)       → To analog section
Pin 4:  DAC1 (P4_31)       → To analog section
Pin 5:  PWM0 (P0_24)       → To filtered output
Pin 6:  PWM1 (P0_25)       → To runt generator
Pin 7:  PWM2 (P0_26)       → To mixed output
Pin 8:  PWM3 (P0_27)       → Spare / future use
Pin 9:  GND
Pin 10: +3.3V IN
```

### J2 (Right Header) - 10 pins
```
Pin 1:  CAN_TX (P1_18)     → To MCP2562
Pin 2:  CAN_RX (P1_19)     → From MCP2562
Pin 3:  SPI_CLK (P1_0)     → To 74HC541
Pin 4:  SPI_MOSI (P1_1)    → To 74HC541
Pin 5:  SPI_MISO (P1_2)    → To 74HC541
Pin 6:  SPI_CS (P1_3)      → To 74HC541
Pin 7:  I2C_SDA (P1_8)     → To 74HC541 + 2.2kΩ pullup
Pin 8:  I2C_SCL (P1_9)     → To 74HC541 + 2.2kΩ pullup
Pin 9:  UART_TX (P1_24)    → To 74HC541
Pin 10: UART_RX (P1_25)    → To 74HC541
```

---

## 🖥️ DISPLAY INTERFACE (J4 - 20 pins, 2x10)

### Data Bus (8-bit parallel):
```
Pin 1:  LCD_D0 (P0_0)
Pin 2:  LCD_D1 (P0_1)
Pin 3:  LCD_D2 (P0_2)
Pin 4:  LCD_D3 (P0_3)
Pin 5:  LCD_D4 (P0_4)
Pin 6:  LCD_D5 (P0_5)
Pin 7:  LCD_D6 (P0_6)
Pin 8:  LCD_D7 (P0_7)
```

### Control Signals:
```
Pin 9:  LCD_RS  (P0_8)     → Register Select
Pin 10: LCD_WR  (P0_9)     → Write Strobe
Pin 11: LCD_CS  (P0_10)    → Chip Select (active low)
Pin 12: LCD_RST (P0_11)    → Reset (active low)
Pin 13: LCD_RD  (10kΩ pullup) → Read (not used)
Pin 14: LCD_BL  (P0_12 PWM) → Backlight control
```

### Touch Controller:
```
Pin 15: TOUCH_X+ (P4_1 ADC0_SE1) → X+ drive/measure
Pin 16: TOUCH_X- (P0_13 GPIO)    → X- ground
Pin 17: TOUCH_Y+ (P4_2 ADC0_SE2) → Y+ drive/measure
Pin 18: TOUCH_Y- (P0_14 GPIO)    → Y- ground
```

### Power:
```
Pin 19: +3.3VD
Pin 20: GND
```

---

## 🔢 16-PIN IDC HEADER (J5) - DUAL MODE

**Mode Select:** MUX_SEL (P0_15 GPIO)
- LOW  = Logic Analyzer mode
- HIGH = AD9851 DDS mode

### Pin Assignment:
```
Pin 1:  D0 / LA_CH0  (P0_16) → Switchable
Pin 2:  D1 / LA_CH1  (P0_17)
Pin 3:  D2 / LA_CH2  (P0_18)
Pin 4:  D3 / LA_CH3  (P0_19)
Pin 5:  D4 / LA_CH4  (P0_20)
Pin 6:  D5 / LA_CH5  (P0_21)
Pin 7:  D6 / LA_CH6  (P0_22)
Pin 8:  D7 / LA_CH7  (P0_23)
Pin 9:  W_CLK / LA_CH8 (P0_28) → AD9851 word clock
Pin 10: FQ_UD / LA_CH9 (P0_29) → AD9851 freq update
Pin 11: RESET / LA_CH10 (P0_30) → AD9851 reset
Pin 12: GND
Pin 13: +5V (optional for AD9851)
Pin 14: +3.3V
Pin 15: GND
Pin 16: GND
```

---

## 📡 PROTOCOL HEADERS (0.1" pin headers)

### SPI Header (J6 - 5 pins):
```
Pin 1: SPI_CLK  (buffered from 74HC541)
Pin 2: SPI_MOSI (buffered)
Pin 3: SPI_MISO (buffered)
Pin 4: SPI_CS   (buffered)
Pin 5: GND
```

### I2C Header (J7 - 3 pins):
```
Pin 1: I2C_SDA (buffered, 2.2kΩ pullup)
Pin 2: I2C_SCL (buffered, 2.2kΩ pullup)
Pin 3: GND
```

### UART Header (J8 - 3 pins):
```
Pin 1: UART_TX (buffered)
Pin 2: UART_RX (buffered)
Pin 3: GND
```

---

## 🚗 CAN BUS (J3 - Screw Terminal)

**Connector:** 3-pin screw terminal (3.5mm pitch)

```
Pin 1: CAN_H (yellow wire typical) → From MCP2562 Pin 6
Pin 2: CAN_L (green wire typical)  → From MCP2562 Pin 7
Pin 3: GND   (black wire)
```

**Termination:** 120Ω resistor via jumper JP1
- Shunt ON:  Termination enabled (end of bus)
- Shunt OFF: No termination (middle of bus)

---

## ⚡ POWER DISTRIBUTION

### Input (from FRDM):
```
+3.3V IN: J1 Pin 2, Pin 10
GND:      J1 Pin 1, Pin 9
```

### Internal Rails:
```
+3.3VA: Analog power (via ferrite bead)
  → MCP6002 op-amps (U1, U2, U3)
  → Analog circuits
  → Bypass: 0.1µF + 10µF per IC

+3.3VD: Digital power (via ferrite bead)
  → 74HC541 (U4)
  → 74HC4053 (U6)
  → MCP2562 (U5)
  → Display
  → Bypass: 0.1µF per IC

+5V: Optional (from boost converter or IDC-16)
  → AD9851 module (if used)

GNDA: Analog ground plane
GNDD: Digital ground plane
  → Joined at star point via 0Ω resistor
```

---

## 🎯 TEST POINTS

| TP | Signal | Purpose |
|----|--------|---------|
| TP1 | DAC0_OUT | Verify DAC0 output before SMA |
| TP2 | DAC1_OUT | Verify DAC1 output before SMA |
| TP3 | PWM_FILT | Verify filtered PWM output |
| TP4 | RUNT_OUT | Verify runt generator output |
| TP5 | MIXED_OUT | Verify mixed signal output |
| TP6 | DDS_OUT | Verify AD9851 output |
| TP7 | ADC_IN | Monitor ADC input signal |
| TP8 | +3.3VA | Analog power rail |
| TP9 | +3.3VD | Digital power rail |
| TP10 | GNDA | Analog ground reference |

---

## 🔧 COMPONENT REFERENCE

### Active ICs:
```
U1: MCP6002 (SOIC-8)  → DAC0/DAC1 buffers
U2: MCP6002 (SOIC-8)  → PWM/Runt buffers
U3: MCP6002 (SOIC-8)  → AD9851/ADC buffers
U4: 74HC541 (TSSOP-20) → Protocol buffer
U5: MCP2562 (SOIC-8)  → CAN transceiver
U6: 74HC4053 (TSSOP-16) → Analog mux (mode switch)
U7: TPS61220 (SOT-23-6) → Boost converter (optional)
Q1: 2N7002 (SOT-23)   → Backlight MOSFET
D1: BAT54S (SOT-23)   → Input protection diodes
```

### Connectors:
```
SMA1-7: Edge-mount SMA (Linx CONSMA003.062)
J1, J2: Arduino stackable headers (2.54mm)
J3:     Screw terminal 3-pin (3.5mm)
J4:     Pin header 2x10 female (2.54mm)
J5:     IDC-16 shrouded (2x8)
J6-J8:  Pin headers 1x5, 1x3, 1x3 (2.54mm)
JP1:    Jumper header 1x2 (CAN termination)
```

---

## 📊 SIGNAL SPECIFICATIONS

### DAC Outputs:
```
DAC0 (SMA1):
  Resolution: 12-bit
  Sample Rate: 1 MSPS max
  Bandwidth: DC-500kHz
  Output: 0-3.3V via unity gain buffer

DAC1 (SMA2):
  Resolution: 14-bit
  Sample Rate: 5 MSPS max
  Bandwidth: DC-2MHz
  Output: 0-3.3V (or 0-330mV with divider)
```

### PWM Outputs:
```
PWM Filtered (SMA3):
  Cutoff: ~1.6kHz (RC filter)
  Output: Smooth 0-3.3V
  Use: DC levels, slow ramps

Runt Generator (SMA4):
  Type: Partial voltage swings
  Use: Signal integrity training
  Adjustable via PWM timing

Mixed Output (SMA5):
  Selectable paths (0Ω resistors):
    Path A: Small signal (10mV-100mV)
    Path B: Glitch generator
    Path C: Direct PWM
```

### AD9851 Output:
```
DDS Output (SMA6):
  Frequency: 0.01 Hz to 70 MHz
  Resolution: 0.0291 Hz (32-bit tuning)
  Output: Clean sine wave, 0-3.3V
  Phase: 5-bit control
```

### ADC Input:
```
ADC Input (SMA7):
  Protection: Schottky diodes + series R
  Filter: RC anti-aliasing (1.6MHz cutoff)
  Range: 0-3.3V (protected to ±0.5V beyond)
  Bandwidth: DC-1MHz
```

---

## 🎓 TYPICAL SIGNAL LEVELS

**For Oscilloscope Probes:**
- Use 10X probe for best results
- 1X probe acceptable for low frequencies
- Keep ground lead short (<6 inches)
- Use BNC-to-probe adapter

**Expected Amplitudes:**
```
Maximum output: 3.3Vpp (into high-Z)
Typical: 3.0Vpp (with series damping)
Small signals: 10mV-100mV (SMA5 Path A)
Runts: Variable, 0.5V-2.5V typical
```

---

## ⚠️ IMPORTANT NOTES

**Power:**
- Total current: 100-300mA typical
- FRDM can supply up to 500mA on +3.3V rail
- Monitor current if adding external loads

**Grounding:**
- Always connect SMA shields to scope ground
- Use short ground connections
- Star-point ground architecture implemented

**Protection:**
- ADC input protected to ±0.5V beyond rails
- Do not exceed 3.6V on any signal
- CAN bus has internal protection

**Frequencies:**
- DAC practical limit: ~1MHz
- PWM effective range: 100Hz-100kHz
- AD9851 tested: 1Hz-70MHz

---

## 🔍 TROUBLESHOOTING QUICK GUIDE

| Problem | Check |
|---------|-------|
| No power | Arduino headers seated properly? |
| No DAC output | DAC pin configured in firmware? |
| Noisy signals | Proper grounding? Bypass caps installed? |
| Display blank | Backlight working? Connections OK? |
| CAN errors | Termination resistor? Correct baud rate? |
| Touch unresponsive | Calibration done? ADC pins configured? |

---

## 📏 MEASUREMENT TIPS

**Frequency Accuracy:**
- Use scope frequency counter
- DAC: ±50ppm typical
- PWM: Depends on MCU clock
- AD9851: ±50ppm (crystal dependent)

**Amplitude Accuracy:**
- Use scope Vpp measurement
- Account for series damping (47Ω)
- Verify with DMM for DC levels

**Rise Time:**
- Op-amp limited: ~10ns typical
- PWM edges: <5ns
- Measure at SMA connector, not test point

---

**QUICK REFERENCE CARD v1.0**  
**Print this page for bench use!**  
**Last Updated:** 2025-01-08

---

## 📞 NEED MORE INFO?

See complete documentation:
- **README.md** - Project overview
- **COMPLETE_DESIGN_SPEC.md** - Full circuit details (78 pages)
- **Datasheets** - Component specifications

**Project Status:** Design Complete, Implementation In Progress  
**Next Steps:** Complete KiCad schematic, layout PCB, manufacture prototype
