# Quick Reference Guide
## Oscilloscope Training Platform - Oscillator Section

---

## Pin Connections

### Oscillator 1
| Pin | Connection | Function |
|-----|------------|----------|
| U1-1 | OSC1_EN (GPIO) | Enable input (3.3V=ON, 0V=OFF) |
| U1-2 | GND | Ground |
| U1-3 | Internal | Output (via R2 to TP1/J1A) |
| U1-4 | +3.3V | Power |

**Outputs:**
- **TP1:** Test point (direct probe access)
- **J1A Pin 1:** Signal output
- **J1A Pin 2:** Ground

**LED1:** Green = Oscillator enabled and running

### Oscillator 2
| Pin | Connection | Function |
|-----|------------|----------|
| U2-1 | OSC2_EN (GPIO) | Enable input (3.3V=ON, 0V=OFF) |
| U2-2 | GND | Ground |
| U2-3 | Internal | Output (via R5 to TP2/J1B) |
| U2-4 | +3.3V | Power |

**Outputs:**
- **TP2:** Test point (direct probe access)
- **J1B Pin 1:** Signal output
- **J1B Pin 2:** Ground

**LED2:** Green = Oscillator enabled and running

---

## Power Requirements

| Parameter | Value |
|-----------|-------|
| Voltage | 3.3V ±5% |
| Current (both OSC) | 20-60 mA typical |
| Current (idle) | <5 mA |

---

## Quick Start

### 1. Install Oscillators
1. Power OFF
2. Verify oscillator pinout (see datasheet)
3. Align Pin 1 (marked with dot) to socket Pin 1 (square pad)
4. Press firmly until seated
5. Label frequency on PCB

### 2. Apply Power
```
+3.3V → Any VCC pad
GND → Any GND pad
```

### 3. Enable Oscillator
```
OSC1: Drive U1 Pin 1 HIGH (3.3V)
OSC2: Drive U2 Pin 1 HIGH (3.3V)
```

LED should illuminate immediately.

### 4. Probe Output
```
Scope ground → J1A/J1B Pin 2 (GND)
Scope probe → J1A/J1B Pin 1 (Signal)
  OR
Scope probe → TP1/TP2 directly
```

**Use 10X probe for best signal quality!**

---

## Expected Signal Characteristics

### 25 MHz Oscillator
- **Frequency:** 25.000 MHz ±50 ppm
- **Amplitude:** 2.8-3.3 Vpp (into high-Z)
- **Rise time:** <5 ns (10%-90%)
- **Duty cycle:** 45-55%
- **Period:** 40 ns

### 50 MHz Oscillator
- **Frequency:** 50.000 MHz ±50 ppm
- **Amplitude:** 2.8-3.3 Vpp (into high-Z)
- **Rise time:** <3 ns (10%-90%)
- **Duty cycle:** 45-55%
- **Period:** 20 ns

---

## Scope Setup for Best Results

### Recommended Settings

**For 25 MHz:**
```
Timebase: 20 ns/div (5 cycles visible)
Voltage: 1 V/div
Coupling: DC
Bandwidth: Full (don't limit)
Probe: 10X
Trigger: Edge, rising, 1.5V level
```

**For 50 MHz:**
```
Timebase: 10 ns/div (5 cycles visible)
Voltage: 1 V/div
Coupling: DC
Bandwidth: Full
Probe: 10X
Trigger: Edge, rising, 1.5V level
```

**For simultaneous viewing:**
```
Ch1 → OSC1 (25 MHz)
Ch2 → OSC2 (50 MHz)
Timebase: 50 ns/div
Trigger: Ch1 rising edge
Math: Can show frequency mixing if overlaid
```

---

## Common Measurements

### Frequency
```
Scope: Use frequency counter function
Expected: ±50 ppm of marked frequency
Example: 25 MHz should read 24.9988 - 25.0013 MHz
```

### Period
```
Scope: Measure time between rising edges
25 MHz: 40.00 ns
50 MHz: 20.00 ns
```

### Rise Time
```
Scope: Measure 10% to 90% transition
Use bandwidth-limit OFF
Zoom timebase for detail
25 MHz: ~3-5 ns typical
50 MHz: ~2-3 ns typical
```

### Duty Cycle
```
Scope: High time / Period × 100%
Expected: 45-55% (most oscillators)
```

### Peak-to-Peak Amplitude
```
Scope: Measure Vpp
Expected: 2.8-3.3V with 10X probe into high-Z
```

### Jitter
```
Advanced scopes: RMS jitter measurement
Typical: <50 ps RMS for crystal oscillators
Use infinite persistence to see jitter envelope
```

---

## Troubleshooting Quick Reference

| Problem | Quick Fix |
|---------|-----------|
| No LED | Check enable pin = 3.3V |
| LED on, no output | Oscillator backwards or not seated |
| Wrong frequency | Check oscillator part number |
| Weak signal | Use 10X probe, check ground |
| Noisy signal | Shorten ground lead, check bypass caps |
| Won't disable | Check pulldown resistor, verify 0V on enable |
| Excessive ringing | R2/R5 = 47Ω? Add series RC if needed |

---

## Training Exercise Ideas

### Exercise 1: Basic Frequency Measurement
1. Enable OSC1 (25 MHz)
2. Measure frequency with scope
3. Calculate error in ppm
4. Document actual frequency

### Exercise 2: Rise Time Analysis
1. Zoom timebase to see edge detail
2. Measure 10%-90% rise time
3. Compare to oscillator datasheet
4. Calculate bandwidth: BW ≈ 0.35 / rise_time

### Exercise 3: Jitter Measurement
1. Set trigger to normal (not auto)
2. Enable infinite persistence
3. Observe edge spread over time
4. Measure jitter if scope has function

### Exercise 4: Dual-Oscillator Harmonics
1. Enable both oscillators (25 & 50 MHz)
2. Set scope to add Ch1 + Ch2
3. Observe harmonic relationship
4. Use FFT to see frequency components

### Exercise 5: Enable/Disable Timing
1. Set scope to single-shot
2. Trigger on enable rising edge
3. Capture oscillator startup
4. Measure time to stable output

### Exercise 6: Signal Integrity
1. Measure with 1X probe → note loading
2. Switch to 10X probe → see improvement
3. Try different ground lead lengths
4. Document effect on signal quality

### Exercise 7: Temperature Drift
1. Measure frequency at room temp
2. Heat board gently (hair dryer)
3. Re-measure frequency
4. Calculate temperature coefficient

### Exercise 8: Power Supply Rejection
1. Probe VCC with AC coupling
2. Add 100mV ripple to supply
3. Observe output for PSRR effects
4. Calculate supply rejection ratio

---

## Component Reference

### Resistors
- **R1, R4:** 10kΩ - Enable pulldown
- **R2, R5:** 47Ω - Series damping
- **R3, R6:** 330Ω - LED current limit

### Capacitors
- **C1, C2:** 0.1µF - Bypass (place <5mm from VCC)

### Semiconductors
- **LED1, LED2:** Green 0603 - Status indicators
- **U1, U2:** DIP-4 socket - Oscillator mounting

### Connectors
- **J1A, J1B:** 2-pin header - Signal output
- **TP1, TP2:** Test point - Direct probing

---

## Compatible Oscillators

### Verified Working
- **SG-8002DC** series (Epson) - 1-125 MHz
- **ASE** series (Abracon) - 1-125 MHz  
- **ECS-xxx** series - Various frequencies
- **KC series** (Kyocera) - 1-200 MHz

### Requirements
- **Package:** DIP-4 (7.0 x 5.0mm or 5.0 x 3.2mm)
- **Voltage:** 3.3V CMOS output
- **Enable:** Active HIGH or NC (not connected)
- **Output:** CMOS logic levels

### Popular Frequencies
- **10 MHz:** Universal reference
- **20 MHz:** General purpose
- **25 MHz:** Ethernet, common reference
- **32 MHz:** MCU external clock
- **50 MHz:** High-speed digital
- **100 MHz:** Fast digital, scope cal
- **125 MHz:** Networking applications

---

## Maintenance

### Daily
- Visual inspection before use
- Verify power supply voltage
- Check LED operation

### Weekly
- Clean test points with IPA
- Check for loose oscillators
- Verify ground connections

### Monthly
- Re-verify frequencies
- Check for corrosion
- Inspect solder joints

### Annually
- Full electrical test
- Replace any corroded components
- Update oscillators if needed

---

## Safety Reminders

⚠️ **Never exceed 3.6V on power supply**  
⚠️ **Always use ESD protection when handling**  
⚠️ **Verify oscillator pinout before installation**  
⚠️ **Power off before removing oscillators**  
⚠️ **Use 10X probe to avoid loading signal**

---

## Specifications Summary

| Parameter | Specification |
|-----------|--------------|
| Supply Voltage | 3.3V ±5% |
| Current Draw | 20-60 mA (both OSC) |
| Output Amplitude | 2.8-3.3 Vpp |
| Output Impedance | 47Ω series |
| Frequency Range | 1-200 MHz (depends on oscillator) |
| Frequency Accuracy | ±50 ppm typical |
| Rise Time | <5 ns @ 25 MHz |
| Jitter | <50 ps RMS typical |
| Enable Logic | 3.3V = ON, 0V = OFF |
| Enable Response | <10 ms typical |

---

## Contact and Support

**Project:** Oscilloscope Training Platform  
**Version:** 1.0  
**Documentation:** See README.md and ASSEMBLY_GUIDE.md  

**Need help?**
- Check ASSEMBLY_GUIDE.md troubleshooting section
- Review schematic in KiCad
- Post issue on project GitHub

---

**Quick Reference Card v1.0**  
**Print this page for bench reference!**

---

## Measurement Template

**Use this template to document your measurements:**

```
Date: _______________
Board S/N: _______________

Oscillator 1:
  Type: _______________
  Marked Freq: ___________ MHz
  Measured Freq: ___________ MHz
  Error: ___________ ppm
  Amplitude: ___________ Vpp
  Rise Time: ___________ ns
  
Oscillator 2:
  Type: _______________
  Marked Freq: ___________ MHz
  Measured Freq: ___________ MHz
  Error: ___________ ppm
  Amplitude: ___________ Vpp
  Rise Time: ___________ ns
  
Power Supply:
  Voltage: ___________ V
  Current (both): ___________ mA
  
Notes:
_________________________________
_________________________________
_________________________________
```

---

**Happy Testing! 📊🔬**
