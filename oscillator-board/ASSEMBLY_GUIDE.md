# Assembly and Testing Guide
## Oscilloscope Training Platform - Oscillator Section

### Document Version: 1.0
### Last Updated: 2025-01-08

---

## Table of Contents

1. [Tools and Materials Required](#tools-and-materials-required)
2. [Pre-Assembly Inspection](#pre-assembly-inspection)
3. [SMD Component Assembly](#smd-component-assembly)
4. [Through-Hole Component Assembly](#through-hole-component-assembly)
5. [Visual Inspection](#visual-inspection)
6. [Power-On Testing](#power-on-testing)
7. [Oscillator Installation](#oscillator-installation)
8. [Function Testing](#function-testing)
9. [Calibration](#calibration)
10. [Troubleshooting](#troubleshooting)

---

## Tools and Materials Required

### Essential Tools
- [ ] Soldering iron (temperature controlled, 300-350°C)
- [ ] Fine-tip soldering iron tip (0.5mm chisel or conical)
- [ ] Solder (0.5mm, 63/37 or lead-free)
- [ ] Tweezers (fine-point, ESD-safe)
- [ ] Multimeter (DMM)
- [ ] Magnifying glass or microscope (5-10x)
- [ ] Flux pen (no-clean flux)
- [ ] Desoldering braid (for mistakes)
- [ ] Isopropyl alcohol (91-99%)
- [ ] Small brush for cleaning

### Recommended Tools
- [ ] Hot air rework station (for SMD repairs)
- [ ] Oscilloscope (for testing)
- [ ] Logic analyzer (for verification)
- [ ] ESD mat and wrist strap
- [ ] Component organizer
- [ ] Label maker or marker

### Materials
- [ ] Assembled PCB (manufactured)
- [ ] Components (see BOM in README)
- [ ] 2x Crystal oscillators (user choice)
- [ ] Wire for testing (24-26 AWG)
- [ ] Power supply (3.3V, 500mA minimum)

---

## Pre-Assembly Inspection

### Step 1: PCB Visual Inspection

**Check for:**
1. **No physical damage**
   - No cracks or broken traces
   - Clean board edges
   - No delamination

2. **Correct layer count**
   - Look at board edge - should see 4 copper layers
   - Green solder mask on both sides

3. **Silkscreen quality**
   - All markings readable
   - Reference designators clear
   - Pin 1 indicators visible

4. **Pad quality**
   - All pads present and intact
   - No solder mask on pads
   - Even copper color

5. **Through-holes clear**
   - All holes drilled completely
   - No burrs or rough edges
   - Correct sizes (1.0mm for sockets, headers)

### Step 2: Component Verification

**Create component groups:**

**Group 1: SMD Resistors**
```
R1, R4: 10kΩ (marking: 103)
R2, R5: 47Ω (marking: 47R0 or 470)  
R3, R6: 330Ω (marking: 331)
```

**Group 2: SMD Capacitors**
```
C1, C2: 0.1µF (marking: 104 or unmarked)
```

**Group 3: SMD LEDs**
```
LED1, LED2: Green 0603
Note: Observe cathode marking (line on one end)
```

**Group 4: Through-Hole**
```
U1, U2: DIP-4 IC sockets
J1A, J1B: 2-pin headers
TP1, TP2: Test points (if through-hole type)
```

**Verification checklist:**
- [ ] All components present
- [ ] Correct values confirmed
- [ ] Polarities identified (LEDs)
- [ ] No damaged components

---

## SMD Component Assembly

### Preparation

1. **Set soldering iron to 320°C** (lead-free: 350°C)
2. **Clean tip** with brass wool
3. **Prepare workspace:**
   - Good lighting (daylight LED recommended)
   - Magnification available
   - Components organized
   - Flux pen ready

### Order of Assembly

**Always install smallest components first!**

#### Phase 1: Resistors (R1-R6)

**For each resistor:**

1. **Apply flux** to both pads
2. **Tin one pad** (just a small amount of solder)
3. **Place component** with tweezers
4. **Tack one end** (heat tinned pad, slide component into solder)
5. **Solder other end** (add fresh solder)
6. **Re-solder first end** if needed (ensure good joint)

**Quality check:**
- Resistor centered on pads
- Solder forms smooth fillet
- No solder bridges
- Component sits flat

**Critical resistors:**
- **R2, R5 (47Ω):** These MUST be close to oscillator output
- **R1, R4 (10kΩ):** Orientation doesn't matter
- **R3, R6 (330Ω):** Orientation doesn't matter

#### Phase 2: Capacitors (C1-C2)

**Process same as resistors:**

1. Apply flux
2. Tin one pad
3. Place capacitor
4. Solder both ends

**CRITICAL PLACEMENT:**
- **C1 must be <5mm from U1 pin 4 location**
- **C2 must be <5mm from U2 pin 4 location**

These are bypass capacitors - proximity is critical!

**Quality check:**
- Capacitor flat and centered
- No tombstoning (one end lifted)
- Clean solder joints

#### Phase 3: LEDs (LED1-LED2)

**⚠️ POLARITY WARNING: LEDs have polarity!**

**Identifying LED polarity:**
- Green bar on package = **Cathode (negative)**
- Or: One pad may have more solder mask = cathode

**Correct orientation:**
```
     Oscillator Side        LED         Away from Oscillator
           ←───────────[─===|>─]────────→
                      Cathode  Anode
                       (K)      (A)
```

**Installation:**

1. **Double-check orientation** on PCB silkscreen
2. Apply flux to pads
3. Tin one pad
4. Place LED with **cathode toward oscillator**
5. Tack one end while verifying orientation
6. Solder other end
7. Re-verify before continuing!

**Quality check:**
- LED oriented correctly (cathode toward oscillator)
- Flat on board
- No solder bridges
- LED not damaged by heat

#### Phase 4: Post-SMD Inspection

**With magnification, check:**

1. **All components installed**
   - R1, R2, R3, C1, LED1 (Oscillator 1 section)
   - R4, R5, R6, C2, LED2 (Oscillator 2 section)

2. **All solder joints good**
   - Shiny (not dull/grainy)
   - Smooth fillet shape
   - Wets both pad and component

3. **No defects**
   - No solder bridges (especially between LED pads!)
   - No cold solder joints
   - No lifted components

4. **Clean board**
   - Remove excess flux with IPA and brush
   - Dry thoroughly

---

## Through-Hole Component Assembly

### Phase 1: IC Sockets (U1, U2)

**Why sockets?**
- User-replaceable oscillators
- No heat damage to expensive oscillators
- Easy frequency changes

**Installation:**

1. **Identify Pin 1**
   - Socket has notch or dot marking Pin 1
   - PCB has dot and square pad for Pin 1

2. **Insert socket**
   - Align Pin 1 marker with PCB marking
   - Press gently until flush
   - Check all pins through holes

3. **Tape in place**
   - Use kapton tape or regular tape
   - Tape across socket to hold it

4. **Flip board over**

5. **Solder one corner pin** (Pin 1 or Pin 4)

6. **Check alignment**
   - Socket should be flat
   - All pins visible in holes
   - If not aligned, reheat and adjust

7. **Solder remaining pins**
   - Add solder to each pin
   - Ensure solder flows into hole
   - Should see nice fillet on both sides

8. **Inspect joints**
   - All pins soldered
   - Good solder fill in holes
   - No bridges between adjacent pins

**Quality check:**
- [ ] Pin 1 correctly oriented
- [ ] Socket sits flush with board
- [ ] All 4 pins soldered properly
- [ ] No cold joints

### Phase 2: Headers (J1A, J1B)

**These are the output connectors**

**Installation:**

1. **Insert header**
   - 2-pin header, 2.54mm pitch
   - Orientation: doesn't matter for signal
   - But: align for mechanical strength

2. **Option A: Tape method**
   - Tape header in place
   - Flip and solder
   
3. **Option B: Tack method**
   - Insert header
   - Hold with finger (careful - hot!)
   - Solder one pin
   - Check alignment
   - Solder second pin

**Quality check:**
- Headers perpendicular to board
- Both pins soldered
- Good solder fill

### Phase 3: Test Points (TP1, TP2)

**If using SMD type:**
- Already installed (just copper pads)

**If using through-hole type:**

1. Insert test point from top
2. Solder from bottom
3. Trim leads if necessary

**Quality check:**
- Test points secure
- Easy to probe
- Not obstructing other components

### Phase 4: Post-Through-Hole Inspection

**Check:**
1. All through-hole components installed
2. All joints reflowed and shiny
3. No solder bridges
4. No cold joints (dull, grainy appearance)

**Clean board:**
- IPA and brush
- Remove flux residue
- Dry thoroughly

---

## Visual Inspection

### Final Pre-Power Checklist

Use magnification and bright light:

**Component checklist:**
- [ ] R1, R4 present (10kΩ)
- [ ] R2, R5 present (47Ω)  
- [ ] R3, R6 present (330Ω)
- [ ] C1, C2 present (0.1µF)
- [ ] LED1, LED2 present and correctly oriented
- [ ] U1, U2 sockets installed, Pin 1 correct
- [ ] J1A, J1B headers installed
- [ ] TP1, TP2 accessible

**Solder joint quality:**
- [ ] All joints shiny and smooth
- [ ] No cold joints (dull, grainy)
- [ ] No solder bridges
- [ ] No missing joints
- [ ] No excessive solder blobs

**PCB condition:**
- [ ] No damaged traces
- [ ] No scratches on solder mask
- [ ] Board clean (no flux residue)
- [ ] No foreign material or debris

---

## Power-On Testing

### ⚠️ DO NOT install oscillators yet!

### Setup

1. **Power supply preparation:**
   - Set to 3.3V
   - Current limit: 100mA
   - Verify with DMM before connecting

2. **Connection points:**
   - **+3.3V:** Connect to any VCC pad
   - **GND:** Connect to any GND pad
   
3. **Multimeter setup:**
   - Set to DC voltage mode
   - Black probe to GND
   - Red probe ready for testing

### Test Sequence

#### Test 1: Power Supply Check

1. **Connect power (no load)**
2. **Measure voltage: should be 3.30V ± 0.05V**
3. **Check current: should be < 5mA**
   (Only LEDs and IC socket pins drawing current)

**If current >50mA: STOP!**
- Short circuit present
- Disconnect power immediately
- Inspect for solder bridges

#### Test 2: Socket Pin Voltages

**For U1 (Oscillator 1 socket):**

| Pin | Expected Voltage | Notes |
|-----|------------------|-------|
| 1 (EN) | 0V | Should be LOW (R1 pulls down) |
| 2 (GND) | 0V | Must be ground |
| 3 (OUT) | 0V | No oscillator installed |
| 4 (VCC) | 3.3V | Power pin |

**For U2 (Oscillator 2 socket):**

| Pin | Expected Voltage | Notes |
|-----|------------------|-------|
| 1 (EN) | 0V | Should be LOW (R4 pulls down) |
| 2 (GND) | 0V | Must be ground |
| 3 (OUT) | 0V | No oscillator installed |
| 4 (VCC) | 3.3V | Power pin |

**Measurement procedure:**
1. Keep black probe on GND
2. Touch red probe to each socket pin
3. Record voltage
4. Compare to expected

#### Test 3: Enable Pin Function

**Test R1 pulldown:**

1. Measure U1 Pin 1: should be 0V
2. Apply 3.3V to U1 Pin 1 via wire
3. Measure: should now be 3.3V
4. Remove wire
5. Measure: should return to 0V

**Repeat for U2 Pin 1 (R4 pulldown)**

**This confirms:**
- Pulldown resistors working
- Enable control will function
- No shorts on enable line

#### Test 4: LED Test (Optional)

**Can manually test LEDs:**

1. **LED1 test:**
   - Apply 3.3V to test point TP1
   - LED1 should light dimly through R3
   
2. **LED2 test:**
   - Apply 3.3V to test point TP2
   - LED2 should light dimly through R6

**Expected behavior:**
- LED glows (may be dim - this is OK)
- Confirms LED orientation correct
- Confirms current limiting resistor working

#### Test 5: Bypass Capacitor Check

**Using oscilloscope (if available):**

1. Connect scope ground to PCB GND
2. Probe U1 Pin 4 (VCC)
3. Look for noise/ripple
4. Should be <50mV ripple
5. Repeat for U2 Pin 4

**If excessive noise:**
- Check C1/C2 installation
- Verify solder joints
- May need additional bulk capacitance

### Power-On Test Results

**✅ PASS criteria:**
- No excessive current draw
- Correct voltages at all socket pins
- Enable pins respond to applied voltage
- LEDs function when tested
- Low noise on VCC pins

**❌ FAIL - do not proceed if:**
- High current (>50mA)
- Wrong voltages
- Enable pins don't work
- LEDs wrong polarity
- Excessive noise

---

## Oscillator Installation

### Selecting Oscillators

**First-time recommendation:**
- **Oscillator 1:** 25 MHz
- **Oscillator 2:** 50 MHz

**Where to buy:**
- Mouser, Digikey, Arrow
- Search: "CMOS oscillator 3.3V DIP-4"
- Example: SG-8002DC series

### Oscillator Pinout Verification

**CRITICAL: Verify pinout before installation!**

**Standard pinout (most common):**
```
   ┌─────┐
 1 │● U  │ 4  VCC
   │     │
 2 │     │ 3  OUT
   └─────┘
   GND

Pin 1: Enable or NC (not connected)
Pin 2: GND
Pin 3: Output
Pin 4: VCC (+3.3V)
```

**Always check datasheet!**
- Some oscillators differ
- Incorrect installation = magic smoke

### Installation Procedure

**For Oscillator 1:**

1. **Power off** the board

2. **Check oscillator marking**
   - Frequency marked on top
   - Pin 1 indicated (dot, notch, or bevel)

3. **Align Pin 1**
   - Oscillator Pin 1 → Socket Pin 1
   - Socket Pin 1 marked with dot and square pad

4. **Insert carefully**
   - Hold oscillator level
   - All pins aligned with socket
   - Press gently and evenly
   - Don't rock side-to-side

5. **Verify seated**
   - Oscillator should be flush with socket
   - All pins fully inserted
   - No bent pins

6. **Label frequency**
   - Write frequency on PCB with marker
   - Use provided "Freq:____MHz" area
   - Example: "Freq: 25 MHz"

**Repeat for Oscillator 2**

**Quality check:**
- [ ] Oscillator seated fully
- [ ] No bent pins
- [ ] Pin 1 aligned correctly
- [ ] Frequency labeled on board

---

## Function Testing

### Test Setup

**Required equipment:**
- Power supply (3.3V)
- Oscilloscope or logic analyzer
- Multimeter
- Wire for enable control

**Test connections:**
```
Power Supply:
  +3.3V → Board VCC
  GND → Board GND

Oscillator Enable:
  U1 Pin 1 → Switch or wire to +3.3V
  U2 Pin 1 → Switch or wire to +3.3V

Outputs:
  TP1 → Oscilloscope Ch1
  TP2 → Oscilloscope Ch2
```

### Test 1: Oscillator 1 Enable

1. **Power on** (3.3V applied)
2. **U1 Pin 1 = 0V** (disabled)
3. **Check:**
   - LED1: OFF
   - TP1: No signal
   
4. **Apply 3.3V to U1 Pin 1** (enable)
5. **Check:**
   - LED1: ON (green)
   - Current: Increases by 10-30mA
   
6. **Verify:**
   - [ ] LED lights up
   - [ ] Current draw reasonable
   - [ ] No overheating

### Test 2: Oscillator 1 Output Signal

**With oscilloscope:**

1. **Enable Oscillator 1** (Pin 1 = 3.3V)

2. **Probe TP1** with oscilloscope
   - Use 10X probe (important!)
   - Ground clip to nearby GND

3. **Scope settings:**
   - DC coupling
   - Timebase: 5-10 cycles visible
   - Trigger: Rising edge
   - For 25 MHz: 10-20ns/div

4. **Verify signal:**
   - [ ] Square wave present
   - [ ] Correct frequency (±50ppm)
   - [ ] Amplitude: 2.5-3.3Vpp
   - [ ] Rise time: <5ns (for 25MHz)
   - [ ] Clean edges (minimal ringing)
   - [ ] 50% duty cycle (approximately)

**Signal quality indicators:**

**Good signal:**
```
    3.3V ┌──┐  ┌──┐  ┌──┐
         │  │  │  │  │  │
         │  │  │  │  │  │
      0V └──┘  └──┘  └──┘
```

**Bad signal (excessive ringing):**
```
    3.3V ┌─╱╲  ┌─╱╲  ┌─╱╲
         │    │    │
         │    │    │    
      0V └────└────└────
```

If excessive ringing:
- Check R2 (47Ω) installed
- Verify short ground path
- May need additional damping

### Test 3: Frequency Measurement

**Precise frequency check:**

1. **Use scope frequency counter**
   - Most scopes have this feature
   - Should read within ±50ppm

2. **Example for 25 MHz:**
   - Expected: 25.000 MHz
   - Tolerance: ±50ppm = ±1.25 kHz
   - Acceptable range: 24.99875 - 25.00125 MHz

3. **If frequency wrong:**
   - Double-check oscillator marking
   - Verify it's an oscillator (not crystal)
   - Check datasheet

### Test 4: Oscillator 2 Testing

**Repeat Tests 1-3 for Oscillator 2:**
- Enable via U2 Pin 1
- Monitor LED2
- Probe TP2
- Verify frequency

### Test 5: Dual Operation

**Both oscillators simultaneously:**

1. Enable both: U1 Pin 1 = 3.3V, U2 Pin 1 = 3.3V
2. Both LEDs should be ON
3. Current draw: 20-60mA total
4. Probe TP1 and TP2 simultaneously

**On dual-channel scope:**
- Ch1 → TP1 (25 MHz)
- Ch2 → TP2 (50 MHz)
- Should see both waveforms
- No interference between channels

### Test 6: Enable/Disable Function

**Test enable control:**

1. Both enabled (3.3V on Pin 1)
2. Disable Oscillator 1 (U1 Pin 1 = 0V)
   - LED1 goes OFF
   - TP1 signal stops
   - TP2 still running
3. Re-enable Oscillator 1
   - LED1 comes back ON
   - TP1 signal resumes
   - Frequency correct

**Startup time:**
- Most oscillators: <10ms
- Can observe with scope on single-shot

---

## Calibration

### Frequency Verification

**For precision applications:**

1. **Compare to known reference**
   - GPS-disciplined oscillator
   - Rubidium standard
   - Lab frequency counter

2. **Long-term stability test**
   - Run for 1 hour
   - Monitor frequency drift
   - Typical: <5ppm over temperature

3. **Document actual frequency**
   - Write measured frequency on PCB
   - Example: "Freq: 25.000124 MHz (measured)"

### Output Level Adjustment

**If needed (rarely):**

1. Signal too strong (>3.3V):
   - Add series resistor (10-47Ω)
   - Or use attenuator

2. Signal too weak (<2V):
   - Check R2/R5 value
   - Verify oscillator output drive
   - May be wrong oscillator type

### Rise Time Optimization

**For cleanest signals:**

1. Measure rise time at TP1/TP2
2. For 25 MHz: Should be <5ns
3. If slow:
   - Reduce R2/R5 value (try 33Ω)
   - Shorten traces if modified

4. If too fast (excessive ringing):
   - Increase R2/R5 value (try 100Ω)
   - Add parallel capacitor (10-22pF)

---

## Troubleshooting

### Problem: No LED illumination

**Possible causes:**

1. **LED orientation wrong**
   - Solution: Check cathode marking
   - Solution: Reflow and rotate 180°

2. **Enable pin not HIGH**
   - Solution: Verify 3.3V on socket Pin 1
   - Solution: Check connection to enable source

3. **LED damaged**
   - Solution: Test with external supply
   - Solution: Replace if necessary

4. **R3/R6 missing or wrong value**
   - Solution: Check resistor value (330Ω)
   - Solution: Reflow or replace

### Problem: No output signal

**Possible causes:**

1. **Oscillator not installed**
   - Solution: Install oscillator!

2. **Oscillator backwards**
   - Solution: Remove and rotate 180°
   - Solution: Verify Pin 1 alignment

3. **Oscillator not seated**
   - Solution: Press firmly to seat fully

4. **Wrong type installed (crystal vs oscillator)**
   - Solution: Need complete oscillator module
   - Solution: Crystal alone won't work

5. **Oscillator not enabled**
   - Solution: Apply 3.3V to socket Pin 1

6. **Oscillator dead**
   - Solution: Try different oscillator
   - Solution: Verify not ESD damaged

### Problem: Wrong frequency

**Possible causes:**

1. **Wrong oscillator installed**
   - Solution: Check part number marking
   - Solution: Verify frequency rating

2. **Reading harmonic instead of fundamental**
   - Solution: Check scope timebase
   - Solution: Use lower bandwidth limit

3. **Oscillator tolerance outside spec**
   - Solution: Acceptable if within ±50-100ppm
   - Solution: Replace if far off

### Problem: Distorted waveform

**Possible causes:**

1. **Scope probe loading**
   - Solution: Use 10X probe, not 1X
   - Solution: Reduce scope input capacitance

2. **Missing damping resistor (R2/R5)**
   - Solution: Install 47Ω resistor
   - Solution: Check solder joints

3. **Poor ground connection**
   - Solution: Use short ground clip on probe
   - Solution: Verify board ground connections

4. **Output overloaded**
   - Solution: Reduce load
   - Solution: Add buffer IC if driving multiple inputs

### Problem: Intermittent operation

**Possible causes:**

1. **Poor socket contact**
   - Solution: Remove and reinstall oscillator
   - Solution: Clean socket pins
   - Solution: Replace socket if damaged

2. **Cold solder joint**
   - Solution: Reflow all joints
   - Solution: Add fresh solder if necessary

3. **Loose connection**
   - Solution: Check headers, wires
   - Solution: Re-solder connections

### Problem: Excessive current draw

**Possible causes:**

1. **Short circuit**
   - Solution: Inspect for solder bridges
   - Solution: Check LED orientation
   - Solution: Verify no shorts between layers

2. **Wrong oscillator voltage**
   - Solution: Verify 3.3V oscillator (not 5V)
   - Solution: Check supply voltage

3. **Damaged component**
   - Solution: Remove oscillator and test
   - Solution: Check if component gets hot
   - Solution: Replace damaged part

---

## Final Acceptance Testing

### Complete Functionality Check

**Run through all tests:**

- [ ] Power supply voltage correct (3.3V)
- [ ] Current draw reasonable (<100mA)
- [ ] Oscillator 1 enables/disables correctly
- [ ] LED1 indicates status
- [ ] OSC1 output frequency correct
- [ ] OSC1 signal quality good
- [ ] Oscillator 2 enables/disables correctly
- [ ] LED2 indicates status
- [ ] OSC2 output frequency correct
- [ ] OSC2 signal quality good
- [ ] Both oscillators run simultaneously
- [ ] Test points accessible
- [ ] Output headers functional
- [ ] No excessive heat
- [ ] No unusual noises

### Performance Verification

**Document your board:**

```
Board Serial: ___________
Assembly Date: ___________

Oscillator 1:
  Type: ___________
  Frequency: ___________ MHz (measured)
  Amplitude: ___________ Vpp
  Rise time: ___________ ns

Oscillator 2:
  Type: ___________
  Frequency: ___________ MHz (measured)
  Amplitude: ___________ Vpp
  Rise time: ___________ ns

Current Draw:
  Idle: ___________ mA
  OSC1 only: ___________ mA
  OSC2 only: ___________ mA
  Both: ___________ mA

Tested by: ___________
Date: ___________
```

### Ready for Integration

**Your oscillator board is complete and tested!**

Next steps:
1. Label board with serial number
2. Store in ESD-safe container if not using immediately
3. Integrate with FRDM-MCXN947 development board
4. Run full system tests
5. Begin training exercises!

---

## Maintenance and Care

### Storage
- Store in anti-static bag
- Keep in dry environment
- Avoid extreme temperatures

### Cleaning
- Use IPA (91-99%) and soft brush
- Dry thoroughly before power-on
- Avoid water or harsh solvents

### Oscillator Changes
- Power off before removing oscillators
- Don't force - socket pins can bend
- Store removed oscillators in anti-static tubes

### Long-term Care
- Inspect solder joints annually
- Check for corrosion if humid environment
- Re-clean flux residue if necessary

---

## Safety Notes

### Electrical Safety
- Always verify power supply polarity
- Never exceed 3.6V (3.3V nominal)
- Use current limiting on power supply

### ESD Protection
- Use ESD wrist strap when handling
- Work on ESD-safe mat if available
- Store in anti-static bags

### Heat Safety
- Soldering iron is HOT (320°C+)
- Don't touch tip or work
- Let board cool before handling
- Use proper ventilation

---

## Congratulations!

**You've successfully assembled and tested the Oscilloscope Training Platform oscillator section!**

This board will provide clean, stable frequency references for:
- Oscilloscope bandwidth testing
- Logic analyzer training
- Signal quality analysis
- Timing measurements
- Digital design verification

**Enjoy your training platform!** 🎓⚡

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-08  
**Author:** DIY Scope Training Project  
**License:** CC BY-SA 4.0
