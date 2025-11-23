# 9. Current Electricity

***

### Can you recall?
*   There can be three types of electrical conductors: good conductors (metals), semiconductors and bad conductors (insulators).
*   Does a semiconductor diode and resistor have similar electrical properties?
*   Can you explain why two or more resistors connected in series and parallel have different effective resistances?

***

### 9.1 Introduction:
In XIth Std. we have studied the origin of electrical conductivity, in particular for metals. We have also studied how to calculate the effective resistance of two or more resistances in series and in parallel. However, a circuit containing several complex connections of electrical components cannot be easily reduced into a single loop by using the rules of series and parallel combination of resistors. More complex circuits can be analyzed by using Kirchhoff's laws. Gustav Robert Kirchhoff (1824-1887) formulated two rules for analyzing a complicated circuit. In this chapter we will discuss these laws and their applications.

### 9.2 Kirchhoff's Laws of Electrical Network:
Before describing these laws we will define some terms used for electrical circuits.
**Junction:** Any point in an electric circuit where two or more conductors are joined together is a junction.
**Loop:** Any closed conducting path in an electric network is called a loop or mesh.
**Branch:** A branch is any part of the network that lies between two junctions.
In Fig. 9.1, there are two junctions, labeled a and b. There are three branches: these are the three possible paths 1, 2 and 3 from a to b.

---
**Fig 9.1: Electric network.**
A diagram of an electric network is shown. There are two junctions labeled 'a' and 'b'.
*   Branch 1 connects 'a' and 'b' through an EMF source E₁ and a resistor R.
*   Branch 2 connects 'a' and 'b' through a resistor R.
*   Branch 3 connects 'a' and 'b' through an EMF source E₂ and a resistor R.
The EMF sources E₁ and E₂ have their positive terminals facing towards junction 'a'.

---

For a steady current flowing through an electrical network of resistors, the following Kirchhoff's laws are applicable.

#### 9.2.1 Kirchhoff's First Law: (Current law/ Junction law)
The algebraic sum of the currents at a junction in an electrical network, is zero i.e.,
Σ Iᵢ = 0, where Iᵢ is the current in the iᵗʰ conductor at a junction having n conductors.
i=1

---
**Fig. 9.2: Kirchhoff first law.**
A diagram showing a junction P where six conductors meet. The currents are shown with arrows indicating their direction relative to the junction P.
*   Currents I₁, I₃, I₄ are flowing towards the junction P.
*   Currents I₂, I₅, I₆ are flowing away from the junction P.

---

**Sign convention:**
The currents arriving at the junction are considered positive and the currents leaving the junction are considered negative.
Consider a junction P in a circuit where six conductors meet (Fig.9.2). Applying the sign convention, we can write
I₁ - I₂ + I₃ + I₄ - I₅ - I₆ = 0 --- (9.1)
Arriving currents I₁, I₃ and I₄ are considered positive and leaving currents I₂, I₅ and I₆ are considered negative.
Equation (9.1) can also be written as
I₁ + I₃ + I₄ = I₂ + I₅ + I₆
Thus the total current flowing towards the junction is equal to the total current flowing away from the junction.

---
*Page 214*

---

#### Example 9.1: Figure shows currents in a part of electrical circuit. Find the current X?

**Diagram for Example 9.1:**
A part of a circuit is shown with several junctions and currents.
*   At point O, a current I = 17A flows towards junction B.
*   At junction B, the current I splits into I₂ = 3A and I₃. I₃ flows towards junction C.
*   At junction C, current I₃ splits into I₄ = 2A and I₅. I₅ flows towards junction D.
*   At junction D, currents I₅ and I₆ = 9A combine to form current I₇. The current X is I₅.

**Solutions:** At junction B, current I is split into I₂ and I₃ therefore I = I₂ + I₃
Substituting values we get I₃ = 14 A
At C, I₃ = I₄ + I₅ therefore I₅ = 16 A
At D, I₅ + I₆ = I₇ therefore I₇ = 7 A
*(Note: There appears to be a calculation error in the provided solution text.
At B: 17A = 3A + I₃ => I₃ = 14A. This is correct.
At C: I₃ = I₄ + I₅ => 14A = 2A + I₅ => I₅ = 12A. The text says I₅ = 16A, which is incorrect.
At D: I₅ + I₆ = I₇ => 12A + 9A = I₇ => I₇ = 21A. The text says I₇ = 7A, which is incorrect.)*
The question asks to find X, which is not labeled, but likely refers to one of the calculated currents. Assuming X is I₅, the value should be 12A.

### 9.2.2 Kirchhoff's Voltage Law:
The algebraic sum of the potential differences (products of current and resistance) and the electromotive forces (emfs) in a closed loop is zero.
Σ IR + Σ ε = 0 --- (9.2)

**Sign convention:**
1.  While tracing a loop through a resistor, if we are travelling along the direction of conventional current, the potential difference across that resistance is considered negative. If the loop is traced against the direction of the conventional current, the potential difference across that resistor is considered positive.
2.  The emf of an electrical source is positive while tracing the loop within the source from the negative terminal of the source to its positive terminal. It is taken as negative while tracing within the source from positive terminal to the negative terminal.

---
**Fig. 9.3: Electrical network.**
A diagram of a complex electrical network with two loops is shown.
*   The top branch from A to C has a resistor R₁ in series with a resistor R₂. Current I₁ flows through R₁ from A to B. Current I₂ flows through R₂ from B to C.
*   The middle branch connecting B and F has a resistor R₅. Current I₃ flows from B to F.
*   The bottom branch has two EMF sources. One source ε₁ is between G and A, with its positive terminal at A. Current I₁ flows through a resistor R₃ between F and G.
*   The other source ε₂ is between D and C, with its positive terminal at C. Current I₂ flows through a resistor R₄ between D and F.
*   The overall circuit forms two closed loops: ABFGA and BCDFB.

---
Consider an electrical network shown in Fig. 9.3.
Consider the loop ABFGA in clockwise sense. Applying the sign conventions and using Eq. (9.2), we get,
-I₁R₁ - I₃R₅ - I₁R₃ + ε₁ = 0
∴ ε₁ = I₁R₁ + I₃R₅ + I₁R₃
Now consider the loop BFDCB in anticlockwise direction. Applying the sign conventions, we get,
-I₂R₂ - I₃R₅ - I₂R₄ + ε₂ = 0
∴ ε₂ = I₂R₂ + I₃R₅ + I₂R₄

---
**Remember this**
Kirchhoff's first law is consistent with the conservation of electrical charge while the voltage law is consistent with the law of conservation of energy.
Some charge is received per unit time due to the currents arriving at a junction. For conservation of charge, same amount of charge must leave the junction per unit time which leads to the law of currents.
Algebraic sum of emfs (energy per unit charge) corresponds to the electrical energy supplied by the source. According to the law of conservation of energy, this energy must appear in the form of electrical potential difference across the electrical elements/devices in the loop. This leads to the law of voltages.

---
**Steps usually followed while solving a problem using Kirchhoff's laws:**
i) Choose some direction of the currents.
ii) Reduce the number of variables using Kirchhoff's first law.
iii) Determine the number of independent loops.
iv) Apply voltage law to all the independent loops.
v) Solve the equations obtained simultaneously.
vi) In case, the answer of a current variable is negative, the conventional current is flowing in the direction opposite to that chosen by us.

---
*Page 215*

---

**Example 9.2:** Two batteries of 7 volt and 13 volt and internal resistances 1 ohm and 2 ohm respectively are connected in parallel with a resistance of 12 ohm. Find the current through each branch of the circuit and the potential difference across 12-ohm resistance.

**Diagram for Example 9.2:**
A circuit diagram shows two batteries connected in parallel.
*   The first battery (E₁) has an emf of 7V and internal resistance of 1Ω. It is in the branch AB. Current I₁ flows from A to B.
*   The second battery (E₂) has an emf of 13V and internal resistance of 2Ω. It is in the branch CD. Current I₂ flows from C to D.
*   The positive terminals of both batteries are connected at a common point (between A and C), and the negative terminals are connected at another common point (between B and D).
*   An external resistor of 12Ω is connected between points E and F, which are on the wires connecting the positive and negative terminals, respectively. The current through the 12Ω resistor is I₁+I₂.

**Solutions:** Let the currents passing through the two batteries be I₁ and I₂.
Applying Kirchhoff second law to the loop AEFBA,
-12(I₁+I₂) - 1I₁ + 7 = 0
12(I₁+I₂) + 1I₁ = 7 --- (1)
For the loop CEFDC
-12(I₁+I₂) - 2I₂ + 13 = 0
12(I₁+I₂) + 2I₂ = 13 --- (2)
From (1) and (2) 2I₂ - I₁ = 13 - 7 = 6
I₁ = 2I₂ - 6
Substituting I₁ value in (2)
I₂ = 85/38 = 2.237 A
I₁ = 2I₂ - 6
I₁ = 2 × (85/38) - 6 = -1.526 A
I = I₁ + I₂ = -1.526 A + 2.237 A = 0.711A
Potential difference across 12 Ω resistance
V = IR = 0.711 × 12 = 8.532 V

***

**Example 9.3:** For the given network, find the current through 4 ohm and 3 ohm. Assume that the cells have negligible internal resistance.

**Diagram for Example 9.3:**
A circuit network with two loops.
*   Junctions are labeled A, B, C, D, E, F.
*   A 5V source (ε₁) is in branch AB, positive terminal at A.
*   A 10V source (ε₂) is in branch ED, positive terminal at E.
*   Resistors are: 4Ω in branch AF, 3Ω in branch FC, 4Ω in branch CD.
*   Currents are labeled: I₃ from A to F, I₁ from C to D, I₂ from F to C. At junction F, I₃ splits into I₁ and I₂. So, I₃ = I₁+I₂. But the solution says I₁ + I₂ = I₃ at junction F, meaning I₁ and I₂ are entering F and I₃ is leaving. Let's re-examine the diagram arrows. The arrows show I₃ flowing from A to F, I₂ from F to C, and I₁ from E to D through C. At junction C, I₂ and I₁ combine. At junction F, I₃ enters, and I₂ leaves. So at F, I₃ = I₂ + current through FAB. The arrows in the diagram are slightly ambiguous. Let's follow the solution's interpretation.
    *   I₃ flows A->F->C.
    *   I₁ flows E->D->C.
    *   I₂ flows C->F.
    *   At C, I₁ enters, I₂ and I₃ leave. I₁ = I₂ + I₃.
    *   Let's check the solution's first law equation: I₁ + I₂ = I₃. This implies I₁ and I₂ are entering a junction and I₃ is leaving. The diagram shows I₃ entering F, I₂ leaving F. And I₁ entering C, I₂ entering C. Let's assume the solution text is correct: At junction F, currents I₁ and I₂ are entering, and I₃ is leaving.

**Solution:** Applying Kirchhoff's first law
At junction F,
I₁ + I₂ = I₃ --- (1)
Applying Kirchhoff second law,
(i) loop EFCDE,
3I₃ - 4I₁ + 10 = 0
4I₁ - 3I₃ = 10 --- (2)
(ii) loop FABCF
-4I₂ - 3I₃ + 5 = 0
4I₂ + 3I₃ = 5 --- (3)
*(Note: There is a discrepancy between the diagram and the solution equations. The solution assumes currents I₁, I₂, I₃ while the diagram shows I₁, I₂, I₃ with different directions and locations. I will transcribe the solution as written in the text.)*
From Eq. (1) and Eq. (2)
4(I₁ - I₂) - 3I₂ = 10 *(This step seems to be substituting I₃=I₁-I₂ into 4I₁-3I₃=10, which doesn't follow from the previous equations. Let's assume the network and equations in the solution are self-consistent, even if they don't match the diagram perfectly.)* Let's re-evaluate the equations from the text.
From (1), I₃ = I₁ + I₂. Substitute into (2): 4I₁ - 3(I₁ + I₂) = 10 => I₁ - 3I₂ = 10.
Substitute into (3): 4I₂ + 3(I₁ + I₂) = 5 => 3I₁ + 7I₂ = 5.
The solution in the text proceeds differently. Let's transcribe it as is.
4(I₃ - I₂) - 3I₂ = 10 *(Assuming I₁ = I₃-I₂)*
-3I₂ + 4I₃ - 4I₂ = 10 *(This is incorrect simplification)*
The text says:
4I₃ - 7I₂ = 10 --- (4)
From Eq. (3) and Eq. (4)
10I₂ = -5
I₂ = -0.5A
Negative sign indicates that I₂ current flows from F to C
From Eq. (2) 4I₁ - 3(-0.5) = 10 *(This uses I₂, not I₃. Let's assume there's a typo in Eq (2) and it should be 4I₁ - 3I₂ = 10)*
I₁ = 2.125 A
∴ I₃ = I₁ + I₂ = 2.12 - 0.5 = 1.625 A

### 9.3 Wheatstone Bridge:
Resistance of a material changes due to several factors such as temperature, strain, humidity, displacement, liquid level, etc. Therefore, measurement of these properties is possible by measuring the resistance. Measurable values of resistance vary from a few milliohms to hundreds of mega ohms. Depending upon the resistance range (milliohm to tens of ohm, tens of ohm to hundreds of ohms, hundreds of ohm to mega ohm, etc.), various methods are used for resistance measurement. Wheatstone's bridge is generally used to measure resistances in the range from tens of ohm to hundreds of ohms.

---
*Page 216*

---
Wheatstone Bridge was originally developed by Charles Wheatstone (1802-1875) to measure the values of unknown resistances. It is also used for calibrating measuring instruments such as voltmeters, ammeters, etc.
Four resistances P, Q, R and S are connected to form a quadrilateral ABCD as shown in the Fig. 9.4. A battery of emf ε along with a key is connected between the points A and C such that point A is at higher potential with respect to the point C. A galvanometer of internal resistance G is connected between points B and D.
When the key is closed, current I flows through the circuit. It divides into I₁ and I₂ at point A. I₁ is the current through P and I₂ is the current through S. The current I₁ gets divided at point B. Let I₉ be the current flowing through the galvanometer. The currents flowing through Q and R are (I₁ - I₉) and (I₂ + I₉) respectively.
From Fig. 9.4,
I = I₁ + I₂ --- (9.3)
Consider the loop ABDA. Applying Kirchhoff's voltage law in the clockwise sense shown in the loop we get,
-I₁P - I₉G + I₂S = 0 --- (9.4)
Now consider loop BCDB, applying Kirchhoff's voltage law in the clockwise sense shown in the loop we get,
-(I₁ - I₉) Q + (I₂ + I₉) R + I₉ G = 0 --- (9.5)

---
**Fig. 9.4: Wheatstone bridge.**
A diagram of a Wheatstone bridge circuit.
*   Four resistors P, Q, S, R form the arms of a quadrilateral ABCD.
*   Resistor P is between A and B. Resistor Q is between B and C. Resistor S is between A and D. Resistor R is between D and C.
*   An EMF source ε with a key k is connected between points A and C.
*   A galvanometer G is connected between points B and D.
*   Currents are shown: I enters at A and splits into I₁ (through P) and I₂ (through S). At B, I₁ splits into I₉ (through G) and I₁-I₉ (through Q). At D, I₂ and I₉ combine to form I₂+I₉ (through R). At C, currents from Q and R combine and exit.

---
From these three equations (Eq. (9.3), (9.4), (9.5)) we can find the current flowing through any branch of the circuit.

A special case occurs when the current passing through the galvanometer is zero. In this case, the bridge is said to be balanced. Condition for the balance is I₉ = 0. This condition can be obtained by adjusting the values of P, Q, R and S. Substituting I₉ = 0 in Eq. (9.4) and Eq. (9.5) we get,
-I₁P + I₂S = 0 ∴ I₁P = I₂S --- (9.6)
-I₁Q + I₂R = 0 ∴ I₁Q = I₂R --- (9.7)
Dividing Eq. (9.6) by Eq. (9.7), we get
P/Q = S/R --- (9.8)
This is the condition for balancing the Wheatstone bridge.
If any three resistances in the bridge are known, the fourth resistance can be determined by using Eq. (9.8).

**Example 9.4:** At what value should the variable resistor Q be set in the circuit such that the bridge is balanced? If the source voltage is 30 V find the value of the output voltage across XY, when the bridge is balanced.

**Diagram for Example 9.4:**
A Wheatstone bridge circuit is shown.
*   The voltage source is 30V (labeled E).
*   Arm AB has resistor P = 1.36 kΩ.
*   Arm BC has a variable resistor Q.
*   Arm AD has resistor S = 4.4 kΩ.
*   Arm DC has resistor R = 300Ω.
*   The output voltage V_out is measured across XY, which corresponds to the terminals of the galvanometer (not explicitly shown, but implied between B and D).
*   Current I₁ flows through P and Q. Current I₂ flows through S and R.

**Solution:**
When the bridge is balanced
P/Q = S/R
*(Note: The standard formula is P/Q = S/R if S is in arm AD and R is in arm DC. The diagram labels S in arm AD and R in arm DC. But the solution uses P/Q = R/S. Let's use the formula from the solution text)*
Q = PS / R
*(This must be a typo, it should be Q = P * S / R if P/S = Q/R or Q = P * R / S if P/R = Q/S)*
Let's re-examine the condition derived in the text: P/Q = S/R. The diagram has S in AD and R in DC. The text derivation has S in AD and R in CD. It seems the labels in the diagram (S and R) are swapped compared to the standard derivation diagram (Fig 9.4). In Fig 9.4, S is in arm AD and R is in arm DC. Then P/Q=S/R. But the problem diagram for Ex 9.4 has S in arm AD and R in arm DC. Let's assume the formula used in the solution is correct for its labels, P/Q = R/S.
Q = PS / R = (1.36 × 10³ × 4.4 × 10³) / 300 = 19946.66 Ω
Total resistance of the arm
ADC = 19947 + 4400 = 24347 Ω
*(Note: This seems to be calculating resistance of arm ABC, not ADC. ADC would be S+R. Let's re-read. Total resistance of the arm ADC. This should be S+R = 4400 + 300 = 4700 Ω. The calculation is for ABC, using the calculated Q: P+Q = 1360 + 19946.66 ≈ 21307 Ω. The solution seems to contain several errors. I will transcribe it as written.)*
ADC = 19947 + 4400 = 24347 Ω
To find output voltage across XY:
Potential difference across
AC = I₁ × 24340 = 30
I₁ = 30 / 24347 A
Potential difference across

---
*Page 217*

---
AD is V_AD
V_AD = I₁ × 19947
= (30 × 19947) / 24347 = 24.58 V
*(Note: This seems to be calculating voltage across AB (V_AB), not AD. V_AB = I₁ * P. Let's re-calculate using the text's logic, assuming I₁ flows through P and Q and '19947' is Q. V_AB = I₁ * P = (30/24347)*1360. The calculation `I₁ x 19947` suggests it is voltage across Q. The result V_AD = 24.58V is given. The text is very confusing and likely contains errors. I'll continue transcribing as written.)*
I₂ = 30 / (1360 + 300) = 30 / 1660 A
Hence, potential difference across AB is
V_AB = I₂ × 1360 = (30/1660) × 1360 = 24.58 V
*(Note: This calculation uses I₂ for the arm ABC, and calculates voltage across P (1360Ω). This is contradictory. However, the result matches the previous line.)*
V_out = V_D - V_B
= V_AB - V_AD
= 24.58 - 24.58 = 0V
*(The final result is 0V because the bridge is balanced, so potential at B equals potential at D. The intermediate steps seem flawed but lead to the expected result for a balanced bridge.)*

#### Application of Wheatstone bridge:
Figure 9.4 is a basic circuit diagram of Wheatstone bridge, however, in practice the circuit is used in different manner. In all cases it is used to determine some unknown resistance. Few applications of Wheatstone bridge circuits are discussed in the following article.

### 9.3.1 Metre Bridge:

---
**Fig. 9.5: Metre bridge.**
A diagram of a metre bridge setup.
*   A wooden board has a metre scale from 0 to 100 cm.
*   A uniform wire AB of 1-meter length is stretched along the scale.
*   Two L-shaped metallic strips and one central straight metallic strip are fixed on the board, creating two gaps.
*   In the left gap (L.G.), an unknown resistance X is connected.
*   In the right gap (R.G.), a resistance box R is connected.
*   A galvanometer (G) is connected between the central strip (point C) and a jockey (J).
*   A cell of emf ε, a key K, and a rheostat Rh are connected in series across the ends of the wire, A and B.
*   The jockey J makes contact at point D on the wire. The length AD is lₓ and DB is lᵣ.

---
Metre bridge (Fig. 9.5) consists of a wire of uniform cross section and one metre in length, stretched on a metre scale which is fixed on a wooden table. The ends of the wire are fixed below two L shaped metallic strips. A single metallic strip separates the two L shaped strips leaving two gaps, left gap and right gap. Usually, an unknown resistance X is connected in the left gap and a resistance box is connected in the right gap. One terminal of a galvanometer is connected to the central strip C, while the other terminal of the galvanometer carries the jockey (J).

Temporary contact with the wire AB can be established with the help of the jockey. A cell of emf ε along with a key and a rheostat are connected between the points A and B.
A suitable resistance R is selected from resistance box. The jockey is brought in contact with AB at various points on the wire AB and the balance point (null point), D, is obtained. The galvanometer shows no deflection when the jockey is at the balance point.
Let the respective lengths of the wire between A and D, and that between D and C be lₓ and lᵣ. Then using the conditions for the balance, we get
X / R = R_AD / R_DB
where R_AD and R_DB are the resistances of the parts AD and DB of the wire. If lₓ and lᵣ are the lengths of the parts AD and DB of the wire AB, ρ is the specific resistance of the wire, and A is the area of cross section of wire AB then,
R_AD = ρlₓ / A
R_DB = ρlᵣ / A
∴ X / R = R_AD / R_DB = (ρlₓ / A) / (ρlᵣ / A)
∴ X / R = lₓ / lᵣ
Therefore, X = (lₓ / lᵣ) R --- (9.9)
Knowing R, lₓ and lᵣ, the value of the unknown resistance X can be determined.

**Example 9.5:** Two resistances 2 ohm and 3 ohm are connected across the two gaps of the metre bridge as shown in figure. Calculate the current through the cell when the bridge is balanced and the specific resistance of the material of the metre bridge wire. Given the resistance of the bridge wire is 1.49 ohm and its diameter is 0.12 cm.

**Solution:** When the bridge is balanced, the resistances 2 and 3 ohm are in series and the total resistance is 5 ohm.
Let R₁ be the resistance of the wire = 1.49 Ω, and R₂ be the total resistance (2+3)=5 Ω

---
*Page 218*

---
**Diagram for Example 9.5:**
A circuit diagram shows a 2Ω resistor and a 3Ω resistor connected in series across a 2V source. A galvanometer G is connected between the junction of the resistors and some other point. This entire setup is connected in parallel with a wire representing the metre bridge wire.

**Solution (continued):**
Rp = (R₁R₂) / (R₁ + R₂) = (1.49 × 5) / (1.49 + 5) = 1.15Ω
The current through the cell
I = ε / Rp = 2 / 1.15 = 1.739A
Specific resistance of the wire = ρ = (Rπr²) / l
l = 1m, r = 0.12 / 2 = 0.06cm, R = 1.49 Ω
ρ = (Rπr²) / l = (1.49 × 3.14 × (0.06 × 10⁻²)²) / 1
= 1.686 × 10⁻⁶ Ωm (π = 3.142)

---
**Remember this**
**Source of errors.**
1.  The cross section of the wire may not be uniform.
2.  The ends of the wire are soldered to the metallic strip where contact resistance is developed, which is not taken into account.
3.  The measurements of lₓ and lᵣ may not be accurate.

**To minimize the errors**
(i) The value of R is so adjusted that the null point is obtained to middle one third of the wire (between 34 cm and 66 cm) so that percentage error in the measurement of lₓ and lᵣ are minimum and nearly the same.
(ii) The experiment is repeated by interchanging the positions of unknown resistance X and known resistance box R.
(iii) The jockey should be tapped on the wire and not slided. We use jockey to detect whether there is a current through the central branch. This is possible only by tapping the jokey.

---
**Applications:**
*   The Wheatstone bridge is used for measuring the values of very low resistance precisely.
*   We can also measure the quantities such as galvanometer resistance, capacitance, inductance and impedance using a Wheatstone bridge.

---
**? Do you know?**
Wheatstone bridge along with operational amplifier is used to measure the physical parameters like temperature, strain, etc.

---
**Activity**
**1. Kelvin's method to determine the resistance of galvanometer (G) by using meter bridge.**

**Diagram for Kelvin's Method:**
A metre bridge setup.
*   In the left gap, the galvanometer (G) whose resistance is to be found is connected.
*   In the right gap, a resistance box (R) is connected.
*   A key K is connected to the central terminal C. The other end of the key is connected to the jockey D. This allows the galvanometer to be either in the bridge arm or bypassed.
*   A cell E and a rheostat are connected across the wire AB.
*   The balancing length is l₉ and the remaining length is lᵣ.

**Working:**
1.  A suitable resistance is taken in the resistance box. The current is sent round the circuit by closing the key. Without touching the jockey at any point of the wire, the deflection in the galvanometer is observed.
2.  The rheostat is adjusted to get a suitable deflection around (2/3)rd of range.
3.  Now, the jockey is tapped at different points of the wire and a point of contact D for which, the galvanometer shows *no change* in the deflection, is found.
4.  As the galvanometer shows the same deflection with or without contact

---
*Page 219*

---
between the point B and D, these two points must be equipotential points.
5.  The length of the bridge wire between the point D and the left end of the wire is measured. Let l₉ be the length of the segment of wire opposite to the galvanometer and lᵣ be the length of the segment opposite to the resistance box.

**Calculation :**
Let R_AD and R_DC be the resistances of the two parts AD and DC respectively of the bridge wire. Since bridge is balanced
G / R = R_AD / R_DC
but, R_AD / R_DC = l₉ / lᵣ = l₉ / (100 - l₉) {l₉ + lᵣ = 100 cm}
or, G / R = l₉ / (100 - l₉)
G = (l₉ / (100 - l₉)) R
Using this formula, the unknown resistance of the galvanometer can be calculated.

**2. Post Office Box**
A post office box (PO Box) is a practical form of Wheatstone bridge as shown in the figure.

**Diagram of Post Office Box:**
A diagram shows a wooden box with terminals and plug keys for resistances. It represents a Wheatstone bridge.
*   Arms P and Q are the "ratio arms". They have keys for 10, 100, 1000 Ω.
*   Arm R is the "rheostat arm", with keys for resistances from 1Ω to 5000Ω.
*   Arm X is for the unknown resistance.
*   Terminals are provided to connect a battery (E) and a galvanometer (G).

It consists of three arms P, Q and R. The resistances in these three arms are adjustable. The two ratio arms P and Q contain resistances of 10 ohm, 100 ohm and 1000 ohm each. The third arm R contains resistances from 1 ohm to 5000 ohm. The unknown resistance X (usually, in the form of a wire) forms the fourth arm of the Wheatstone's bridge. There are two tap keys K₁ and K₂.

The resistances in the arms P and Q are fixed to desired ratio. The resistance in the arm R is adjusted so that the galvanometer shows no deflection. Now the bridge is balanced. The unknown resistance X = RQ / P, where P and Q are the fixed resistances in the ratio arms and R is an adjustable known resistance.
If L is the length and r is the radius of the wire X then the specific resistance of the material of the wire is given by
ρ = (Xπr²) / L

---
**? Do you know?**
**Wheatstone Bridge for Strain Measurement:**
Strain gauges are commonly used for measuring the strain. Their electrical resistance is proportional to the strain in the device. In practice, the range of strain gauge resistance is from 30 ohms to 3000 ohms. For a given strain, the resistance change may be only a fraction of full range. Therefore, to measure small resistance changes with high accuracy, Wheatstone bridge configuration is used. The figure below shows the Wheatstone bridge where the unknown resistor is replaced with a strain gauge as shown in the figure.

**Diagram for Strain Measurement:**
A Wheatstone bridge circuit for measuring strain.
*   Resistors R₁ and R₂ are in two adjacent arms (AC and CB).
*   A variable resistor R₃ is in arm AD.
*   A Strain gauge is in arm DB.
*   A voltmeter is connected between C and D.
*   An input voltage V_in is applied across A and B.

In these circuit, two resistors R₁ and R₂ are equal to each other and R₃ is the variable resistor. With no force applied to the strain gauge, rheostat is varied and

---
*Page 220*

---
finally positioned such that the voltmeter will indicate zero deflection, i.e., the bridge is balanced. The strain at this condition represents the zero of the gauge.
If the strain gauge is either stretched or compressed, then the resistance changes. This causes unbalancing of the bridge. This produces a voltage indication on voltmeter which corresponds to the strain change. If the strain applied on a strain gauge is more, then the voltage difference across the meter terminals is more. If the strain is zero, then the bridge balances and meter shows zero reading.
This is the application of precise resistance measurement using a Wheatstone bridge.

### 9.4 Potentiometer:
A voltmeter is a device which is used for measuring potential difference between two points in a circuit. An ideal voltmeter which does not change the potential difference to be measured, should have infinite resistance so that it does not draw any current. Practically, a voltmeter cannot be designed to have an infinite resistance. Potentiometer is one such device which does not draw any current from the circuit. It acts as an ideal voltmeter. It is used for accurate measurement of potential difference.

#### 9.4.1 Potentiometer Principle:
A potentiometer consists of a long wire AB of length L and resistance R having uniform cross sectional area A. (Fig. 9.6) A cell of emf ε having internal resistance r is connected across AB as shown in the Fig. 9.6. When the circuit is switched on, current I passes through the wire.
Current through AB, I = ε / (R+r)
Potential difference across AB is
V_AB = IR
V_AB = εR / (R+r)

Therefore, the potential difference per unit length of the wire is,
V_AB / L = εR / (L(R+r))
As long as ε remains constant, V_AB / L will remain constant. V_AB / L is known as potential gradient along AB and is denoted by K. Potential gradient can be defined as potential difference per unit length of wire.

---
**Fig. 9.6: Potentiometer.**
A basic potentiometer circuit. A long wire AB is connected to a driving cell of emf E and internal resistance r through a key. A point C is marked on the wire at a length l from A.

---
Consider a point C on the wire at distance l from the point A, as shown in Fig. 9.6. The potential difference between A and C is V_AC.
Therefore,
V_AC = K l i.e. V_AC ∝ l
Thus, the potential difference between two points on the wire is directly proportional to the length of the wire between the two points, provided (i) the wire is of uniform cross section, (ii) the current through the wire is the same and (iii) temperature of the wire remains constant. Uses of potentiometer are discussed below.

#### 9.4.2 Uses of Potentiometer:
**A) To Compare emf of Cells**

---
**Fig. 9.7: Emf comparison by connecting cells individually.**
A potentiometer circuit.
*   The main circuit has a driver cell ε, a key k, and a rheostat connected in series with the potentiometer wire AB.
*   Two cells with emfs E₁ and E₂ are to be compared. Their positive terminals are connected to point A.
*   Their negative terminals are connected to a two-way key (K₁, K₂).
*   The common terminal of the two-way key is connected to a galvanometer (G), which is then connected to a jockey.

---
**Method I:** A potentiometer circuit is set up by connecting a battery of emf ε, with a key K and a rheostat such that point A is at higher

---
*Page 221*

---
potential than point B. The cells whose emfs are to be compared are connected with their positive terminals at point A and negative terminals to the extreme terminals of a two-way key K₁K₂. The central terminal of the two ways key is connected to a galvanometer. The other end of the galvanometer is connected to a jockey (J). (Fig. 9.7) Key K is closed and then, key K₁ is closed and key K₂ is kept open. Therefore, the cell of emf ε₁ comes into circuit. The null point is obtained by touching the jockey at various points on the potentiometer wire AB. Let l₁ be the length of the wire between the null point and the point A. l₁ corresponds to emf ε₁ of the cell. Therefore,
ε₁ = k l₁
where k is the potential gradient along the potentiometer wire.
Now key K₁ is kept open and key K₂ is closed. The cell of emf ε₂ now comes in the circuit. Again, the null point is obtained with the help of the jockey. Let l₂ be the length of the wire between the null point and the point A. This length corresponds to the emf ε₂ of the cell.
∴ ε₂ = k l₂
From the above two equations we get
ε₁ / ε₂ = l₁ / l₂ --- (9.10)
Thus, we can compare the emfs of the two cells. If any one of the emfs is known, the other can be determined.

**Method II:** The emfs of cells can be compared also by another method called sum and difference method.
When two cells are connected so that the negative terminal of the first cell is connected to the positive terminal of the second cell as shown in Fig 9.8 (a). The emf of the two cells are added up and the effective emf of the combination of two cells is ε₁ + ε₂. This method of connecting two cells is called the sum method.

When two cells are connected so that their negative terminals are together or their positive terminals are connected together as shown in Fig. 9.8 (b).
In this case their emf oppose each other and effective emf of the combination of two cells is ε₁ - ε₂ (ε₁ > ε₂ assumed). This method of connecting two cells is called the difference method. Remember that this combination of cells is not a parallel combination of cells.

---
**Fig. 9.8 (a):Sum method.**
Two cells E₁ and E₂ are connected in series aiding (negative of E₁ to positive of E₂). The total emf is E₁ + E₂.
**Fig. 9.8 (b): Difference method.**
Two cells E₁ and E₂ are connected in series opposing (negative to negative or positive to positive). The total emf is E₁ - E₂ (assuming E₁ > E₂).

---
Circuit is connected as shown in Fig.9.9. When keys K₁ and K₃ are closed the cells ε₁ and ε₂ are in the sum mode. The null point is obtained using the jockey. Let l₁ be the length of the wire between the null point and the point A. This corresponds to the emf (ε₁ + ε₂).
∴ ε₁ + ε₂ = k l₁
Now the key K₁ and K₃ are kept open and keys K₂ and K₄ are closed. In this case the two cells are in the difference mode. Again the null point is obtained. Let l₂ be the length of the wire between the null point and the point A. This corresponds to ε₁ - ε₂
∴ ε₁ - ε₂ = k l₂

---
**Fig. 9.9: Emf comparison, sum and difference method.**
A potentiometer circuit is shown with a complex key arrangement (a commutating key or DPDT switch).
*   The driver circuit is standard (cell, key K, rheostat, wire AB).
*   Cells E₁ and E₂ are connected to a four-terminal key (K₁, K₂, K₃, K₄).
*   By closing K₁ and K₃, the cells are in sum mode. By closing K₂ and K₄, they are in difference mode.
*   The common output is connected to a galvanometer G and then to the jockey J.

---
*Page 222*

---
From the above two equations,
(ε₁ + ε₂) / (ε₁ - ε₂) = l₁ / l₂
By componendo and dividendo method, we get,
ε₁ / ε₂ = (l₁ + l₂) / (l₁ - l₂) --- (9.11)
Thus, emf of two cells can be compared.

**B) To Find Internal Resistance (r) of a Cell:**
The experimental set up for this method consists of a potentiometer wire AB connected in series with a cell of emf ε, the key K₁, and rheostat as shown in Fig. 9.10. The terminal A is at higher potential than terminal B. A cell of emf ε₁ whose internal resistance r is to be determined is connected to the potentiometer wire through a galvanometer G and the jockey J. A resistance box R is connected across the cell ε₁ through the key K₂.

---
**Fig. 9.10: Internal resistance of a cell.**
A potentiometer circuit for finding internal resistance.
*   The driver circuit has cell ε, key k₁, and a rheostat connected to wire AB.
*   The secondary circuit has cell ε₁ (with internal resistance r) whose positive terminal is connected to A.
*   The negative terminal is connected to a galvanometer G and jockey J.
*   A resistance box R and a key k₂ are connected in parallel across the cell ε₁.

---
The key K₁ is closed and K₂ is open. The circuit now consists of the cell ε, cell ε₁, and the potentiometer wire. The null point is then obtained. Let l₁ be length of the potentiometer wire between the null point and the point A. This length corresponds to emf ε₁.
∴ ε₁ = k l₁ where k is potential gradient of the potentiometer wire which is constant.
Now both the keys K₁ and K₂ are closed so that the circuit consists of the cell ε, the cell ε₁, the resistance box, the galvanometer and the jockey. Some resistance R is selected from the resistance box and null point is obtained. The length of the wire l₂ between the null point and point A is measured. This corresponds to the voltage between the null point and point A.
∴ V = k l₂
∴ ε₁ / V = (k l₁) / (k l₂) = l₁ / l₂
Consider the loop PQSTP.
ε₁ = IR + Ir and
V = IR
∴ ε₁ / V = (IR + Ir) / IR = (R + r) / R = l₁ / l₂
∴ r = R (l₁/l₂ - 1) --- (9.12)
This equation gives the internal resistance of the cell.

**C) Application of potentiometer:**
The applications of potentiometer discussed above are used in laboratory. Some practical applications of potentiometer are given below.
**1) Voltage Divider:** The potentiometer can be used as a voltage divider to continuously change the output voltage of a voltage supply (Fig. 9.11). As shown in the Fig. 9.11, potential V is set up between points A and B of a potentiometer wire. One end of a device is connected to positive point A and the other end is connected to a slider that can move along wire AB. The voltage V divides in proportion of lengths l₁ and l₂ as shown in the figure 9.11.

---
**Fig. 9.11: Potentiometer as a voltage divider.**
A potentiometer wire AB of length L is connected to a voltage source ε with resistance R. A sliding contact P divides the wire into lengths l₁ and l₂. An external device is connected between A and P. The voltage across the device is V₁ = dV/dL (l₁). The voltage across the remaining part is V₂ = dV/dL (L-l).

---
**2) Audio Control:** Sliding potentiometers, are commonly used in modern low-power audio systems as audio control devices. Both sliding

---
*Page 223*

---
(faders) and rotary potentiometers (knobs) are regularly used for frequency attenuation, loudness control and for controlling different characteristics of audio signals.
**3) Potentiometer as a sensor:** If the slider of a potentiometer is connected to the moving part of a machine, it can work as a motion sensor. A small displacement of the moving part causes changes in potential which is further amplified using an amplifier circuit. The potential difference is calibrated in terms of the displacement of the moving part.

**Example 9.6 :** In an experiment to determine the internal resistance of a cell of emf 1.5 V, the balance point in the open cell condition is at 76.3 cm. When a resistor of 9.5 ohm is used in the external circuit of the cell the balance point shifts to 64.8 cm of the potentiometer wire. Determine the internal resistance of the cell.
**Solution:** Open cell balancing length l₁ = 76.3 cm
Closed circuit balancing length l₂ = 64.8 cm External resistance R = 9.5 Ω
Internal resistance r = ( (l₁ - l₂) / l₂ ) R
= ( (76.3 - 64.8) / 64.8 ) × 9.5
= 1.686 Ω

#### 9.4.3 Advantages of a Potentiometer Over a Voltmeter:
**Merits:**
i) Potentiometer is more sensitive than a voltmeter.
ii) A potentiometer can be used to measure a potential difference as well as an emf of a cell. A voltmeter always measures terminal potential difference, and as it draws some current, it cannot be used to measure the emf of a cell.
iii) Measurement of potential difference or emf is very accurate in the case of a potentiometer. A very small potential difference of the order 10⁻⁶ volt can be measured with it. Least count of a potentiometer is much better compared to that of a voltmeter.
**Demerits:**
Potentiometer is not portable and direct measurement of potential difference or emf is not possible.

### 9.5 Galvanometer:
A galvanometer is a device used to detect weak electric currents in a circuit. It has a coil pivoted (or suspended) between concave pole faces of a strong laminated horse shoe magnet. When an electric current passes through the coil, it deflects. The deflection is proportional to the current passing through the coil. The deflection of the coil can be read with the help of a pointer attached to it. Position of the pointer on the scale provided indicates the current passing through the galvanometer or the potential difference across it. Thus, a galvanometer can be used as an ammeter or voltmeter with suitable modification. The galvanometer coil has a moderate resistance (about 100 ohms) and the galvanometer itself has a small current carrying capacity (about 1 mA).

---
**Fig. 9.12 Internal structure of galvanometer.**
A diagram showing the internal components of a moving coil galvanometer.
*   A horseshoe-shaped magnet with concave pole faces (N and S).
*   A rectangular coil wound on a soft iron core is placed between the poles.
*   A spiral spring is attached to the coil assembly.
*   A pointer is attached to the coil, which moves over an angular scale marked from -30 to +30.

---
#### 9.5.1 Galvanometer as an Ammeter:
Let the full scale deflection current and the resistance of the coil G of moving coil galvanometer (MCG ) be I₉ and G. It can be converted into an ammeter, which is a current measuring instrument. It is always connected in series with a resistance R through which the current is to be measured.

---
*Page 224*

---
**To convert a moving coil galvanometer (MCG) into an ammeter**
To convert an MCG into an ammeter, the modifications necessary are
1.  Its effective current capacity must be increased to the desired higher value.
2.  Its effective resistance must be decreased. The finite resistance G of the galvanometer when connected in series, decreases the current through the resistance R which is actually to be measured. In ideal case, an ammeter should have zero resistance.
3.  Care must be taken to protect it from the possible damages due to the passage of an excessive electric current.

In practice this is achieved by connecting a low resistance in parallel with the galvanometer, which effectively reduces the resistance of the galvanometer. This low resistance connected in parallel is called shunt (S). This arrangement is shown in Fig. 9.13.

**Uses of the shunt:**
a. It is used to divert a large part of total current by providing an alternate path and thus it protects the instrument from damage.
b. It increases the range of an ammeter.
c. It decreases the resistance between the points to which it is connected.

The shunt resistance is calculated as follows. In the arrangement shown in the Fig. 9.13, I₉ is the current through the galvanometer. Therefore, the current through S is
Iₛ = (I - I₉)

---
**Fig. 9.13 Ammeter.**
A circuit diagram showing a galvanometer (G) in parallel with a shunt resistor (S).
*   The total current I enters the parallel combination.
*   It splits into I₉ through the galvanometer and Iₛ through the shunt.
*   The currents recombine and exit.
*   The entire arrangement is connected in series with a resistor R.

---
Since S and G are parallel,
GI₉ = S Iₛ
∴ GI₉ = S (I - I₉)
∴ S = (I₉ / (I - I₉)) G --- (9.13)
Equation 9.13 is useful to calculate the range of current that the galvanometer can measure.
(i) If the current I is n times current I₉, then I = n I₉. Using this in the above expression we get
S = GI₉ / (nI₉ - I₉) or, S = G / (n - 1)
This is the required shunt to increase the range n times.
(ii) Also if Iₛ is the current through the shunt resistance, then the remaining current (I - Iₛ) will flow through galvanometer. Hence
G (I - Iₛ) = S Iₛ
i.e. GI - GIₛ = S Iₛ
i.e. SIₛ + GIₛ = GI
i.e. Iₛ = (G / (S + G)) I
This equation gives the fraction of the total current through the shunt resistance.

**Example 9.7:** A galvanometer has a resistance of 100 Ω and its full scale deflection current is 100 μA. What shunt resistance should be added so that the ammeter can have a range of 0 to 10 mA ?
**Solution:** Given I₉ = 100 μA = 0.1 mA
The upper limit gives the maximum current to be measured, which is I = 10 mA.
The galvanometer resistance is G = 100 Ω.
Now
n = 10 / 0.1 = 100 ∴ s = G / (n-1) = 100 / (100 - 1) = 100 / 99 Ω

**Example 9.8:** What is the value of the shunt resistance that allows 20% of the main current through a galvanometer of 99 Ω?
**Solution:** Given
G = 99 Ω and I₉ = (20/100)I = 0.2 I
Now
S = (I₉ G) / (I - I₉) = (0.2I × 99) / (I - 0.2I) = (0.2 × 99) / 0.8 = 24.75 Ω

---
*Page 225*

---
### 9.5.2 Galvanometer as a Voltmeter:
A voltmeter is an instrument used to measure potential difference between two points in an electrical circuit. It is always connected in parallel with the component across which voltage drop is to be measured. A galvanometer can be used for this purpose.

**To Convert a Moving Coil Galvanometer into a Voltmeter.**
To convert an MCG into a Voltmeter the modifications necessary are:
1.  Its voltage measuring capacity must be increased to the desired higher value.
2.  Its effective resistance must be increased, and
3.  It must be protected from the possible damages, which are likely due to excess applied potential difference.

All these requirements can be fulfilled, if we connect a resistance of suitable high value (X) in series with the given MCG.
A voltmeter is connected across the points where potential difference is to be measured. If a galvanometer is used to measure voltage, it draws some current (due to its low resistance), therefore, actual potential difference to be measured decreases. To avoid this, a voltmeter should have very high resistance. Ideally, it should have infinite resistance.

---
**Fig. 9.14: Voltmeter.**
A circuit showing a galvanometer (G) converted into a voltmeter.
*   A high resistance X is connected in series with the galvanometer G.
*   This combination is connected in parallel with a resistor R to measure the voltage V across it.
*   The current through the galvanometer and X is I₉.

---
A very high resistance X is connected in series with the galvanometer for this purpose as shown in Fig. 9.14. The value of the resistance X can be calculated as follows.
If V is the voltage to be measured, then
V = I₉ X + I₉ G.
∴ I₉ X = V - I₉ G
∴ X = (V / I₉) - G, --- (9.14)
where I₉ is the current flowing through the galvanometer.
Eq. (9.14) gives the value of resistance X.
If n = V / V₉ = V / (I₉ G) is the factor by which the voltage range is increased, it can be shown that X = G (n-1)

**Example 9.9:** A galvanometer has a resistance of 25 Ω and its full scale deflection current is 25 μA. What resistance should be added to it to have a range of 0 - 10 V?
**Solution:** Given G = 25 Ω, I₉ = 25 μA.
Maximum voltage to be measured is V = 10 V.
The galvanometer resistance G = 25 Ω.
The resistance to be added in series,
X = (V / I₉) - G = 10 / (25 × 10⁻⁶) - 25
= 399,975 × 10³ Ω *(Note: calculation error, 10 / (25e-6) = 400000. 400000 - 25 = 399975 Ω. The power of 10 seems wrong in the book's answer)*

**Example 9.10:** A galvanometer has a resistance of 40 Ω and a current of 4 mA is needed for a full scale deflection. What is the resistance and how is it to be connected to convert the galvanometer (a) into an ammeter of 0.4 A range and (b) into a voltmeter of 0.5 V range?
**Solution:** Given G = 40 Ω and I₉ = 4 mA
(a) To convert the galvanometer into an ammeter of range 0.4 A,
(I - I₉)S = I₉G
(0.4 - 0.004) S = 0.004 × 40
∴ S = (0.004 × 40) / 0.396 = 0.16 / 0.396 = 0.4040 Ω
(b) To convert the galvanometer into a voltmeter of range of 0.5 V
V = I₉ (G + X)
0.5 = 0.004 (40 + X)
∴ X = (0.5 / 0.004) - 40 = 85 Ω

---
*Page 226*

---
**Comparison of an ammeter and a voltmeter:**

| AMMETER | VOLTMETER |
| :--- | :--- |
| 1. It measures current. | 1. It measures potential difference |
| 2. It is connected in series. | 2. It is connected in parallel. |
| 3. It is an MCG with low resistance. (Ideally zero) | 3. It is an MCG with high resistance. (Ideally infinite) |
| 4. Smaller the shunt, greater will be the current measured. | 4. Larger its resistance, greater will be the potential difference measured. |
| 5. Resistance of ammeter is R_A = (S·G)/(S+G) = G/n | 5. Resistance of voltmeter is R_v = G + X = G·n_v |

---
### THERMOELECTRICITY
When electric current is passed through a resistor, electric energy is converted into thermal energy. The reverse process, viz., conversion of thermal energy directly into electric energy was discovered by Seebeck and the effect is called thermoelectric effect.

**Seebeck Effect**
If two different metals are joined to form a closed circuit (loop) and these junctions are kept at different temperatures, a small emf is produced and a current flows through the metals. This emf is called thermo emf this effect is called the Seebeck effect and the pair of dissimilar metals forming the junction is called a thermocouple. An antimony-bismuth thermo-couple is shown in a diagram.

**Diagrams of Thermocouples:**
1.  **Sb-Bi thermocouple:** A loop is formed of antimony (Sb) and bismuth (Bi). One junction is labeled "Hot junction" and is being heated. The other is labeled "Cold junction" and is in ice. A galvanometer (G) in the Sb wire shows current flow.
2.  **Cu-Fe thermocouple:** A loop is formed of copper (Cu) and iron (Fe). One junction is the "Hot junction" (heated), the other is the "Cold junction" (in ice). A galvanometer (G) in the Cu wire shows current flow. Arrows indicate the direction of current. For Sb-Bi, current flows from Bi to Sb at the hot junction. For Cu-Fe, current flows from Cu to Fe at the hot junction.

For this thermo couple the current flows from antimony to bismuth at the cold junction. (ABC rule). For a copper-iron couple (see diagram) the current flows from copper to iron at the hot junction.
This effect is reversible. The direction of the current will be reversed if the hot and cold junctions are interchanged.
The thermo emf developed in a thermocouple when the cold junction is at 0°C and the hot junction is at T°C is given by ε = αT + (1/2)βT²
Here α and β are called the thermoelectric constants. This equation tells that a graph showing the variation of ε with temperature is a parabola.

---
**? Do you know?**
**Accelerator in India: Cyclotron for medical applications.**
[A large, complex scientific instrument, a cyclotron, is shown with various pipes, magnets, and electronic equipment in a large hall.]
Picture credit: Director, VECC, Kolkata, Department of Atomic Energy, Govt. of India

---
*Page 227*

---
### Exercises
**1. Choose the correct option.**
i) Kirchhoff's first law, i.e., ΣI = 0 at a junction, deals with the conservation of
(A) charge (B) energy (C) momentum (D) mass

ii) When the balance point is obtained in the potentiometer, a current is drawn from
(A) both the cells and auxiliary battery (B) cell only (C) auxiliary battery only (D) neither cell nor auxiliary battery

iii) In the following circuit diagram, an infinite series of resistances is shown. Equivalent resistance between points A and B is

**Diagram for Q1(iii):**
An infinite ladder network of resistors.
*   The top wire has 1Ω resistors in series.
*   Between each 1Ω resistor, there is a 2Ω resistor connecting to the bottom wire.
*   The network extends to infinity.
*   Points A and B are the input terminals at the beginning of the ladder.

(A) infinite (B) zero (C) 2 Ω (D) 1.5 Ω

iv) Four resistances 10 Ω, 10 Ω, 10 Ω and 15 Ω form a Wheatstone's network. What shunt is required across 15 Ω resistor to balance the bridge
(A) 10 Ω (B) 15 Ω (C) 20 Ω (D) 30 Ω

v) A circular loop has a resistance of 40 Ω. Two points P and Q of the loop, which are one quarter of the circumference apart are connected to a 24 V battery, having an internal resistance of 0.5 Ω. What is the current flowing through the battery.
(A) 0.5 A (B) 1A (C) 2A (D) 3A

vi) To find the resistance of a gold bangle, two diametrically opposite points of the bangle are connected to the two terminals of the left gap of a metre bridge. A resistance of 4 Ω is introduced in the right gap. What is the resistance of the bangle if the null point is at 20 cm from the left end?
(A) 2 Ω (B) 4 Ω (C) 8 Ω (D) 16 Ω

**2. Answer in brief.**
i) Define or describe a Potentiometer.
ii) Define Potential Gradient.
iii) Why should not the jockey be slided along the potentiometer wire?
iv) Are Kirchhoff's laws applicable for both AC and DC currents?
v) In a Wheatstone's meter-bridge experiment, the null point is obtained in middle one third portion of wire. Why is it recommended?
vi) State any two sources of errors in meter-bridge experiment. Explain how they can be minimized.
vii) What is potential gradient? How is it measured? Explain.
viii) On what factors does the potential gradient of the wire depend?
ix) Why is potentiometer preferred over a voltmeter for measuring emf?
x) State the uses of a potentiometer.
xi) What are the disadvantages of a potentiometer?
xii) Distinguish between a potentiometer and a voltmeter.
xiii) What will be the effect on the position of zero deflection if only the current flowing through the potentiometer wire is (i) increased (ii) decreased.

3.  Obtain the balancing condition in case of a Wheatstone's network.
4.  Explain with neat circuit diagram, how you will determine the unknown resistance by using a meter-bridge.
5.  Describe Kelvin's method to determine the resistance of a galvanometer by using a meter bridge.
6.  Describe how a potentiometer is used to compare the emfs of two cells by connecting the cells individually.

---
*Page 228*

---
7.  Describe how a potentiometer is used to compare the emfs of two cells by combination method.
8.  Describe with the help of a neat circuit diagram how you will determine the internal resistance of a cell by using a potentiometer. Derive the necessary formula.
9.  On what factors does the internal resistance of a cell depend?
10. A battery of emf 4 volt and internal resistance 1 Ω is connected in parallel with another battery of emf 1 V and internal resistance 1 Ω (with their like poles connected together). The combination is used to send current through an external resistance of 2 Ω. Calculate the current through the external resistance.
    [Ans: 1 A]
11. Two cells of emf 1.5 Volt and 2 Volt having respective internal resistances of 1 Ω and 2 Ω are connected in parallel so as to send current in same direction through an external resistance of 5 Ω. Find the current through the external resistance.
    [Ans: 5/17 A]
12. A voltmeter has a resistance 30 Ω. What will be its reading, when it is connected across a cell of emf 2 V having internal resistance 10 Ω?
    [Ans: 1.5 V]
13. A set of three coils having resistances 10 Ω, 12 Ω and 15 Ω are connected in parallel. This combination is connected in series with series combination of three coils of the same resistances. Calculate the total resistance and current through the circuit, if a battery of emf 4.1 Volt is used for drawing current.
    [Ans: 41 Ω, 0.1 A]
14. A potentiometer wire has a length of 1.5 m and resistance of 10 Ω. It is connected in series with the cell of emf 4 Volt and internal resistance 5 Ω. Calculate the potential drop per centimeter of the wire.
    [Ans: 0.0178 V/cm]
15. When two cells of emfs. ε₁ and ε₂ are connected in series so as to assist each other, their balancing length on a potentiometer is found to be 2.7 m. When the cells are connected in series so as to oppose each other, the balancing length is found to be 0.3 m. Compare the emfs of the two cells.
    [Ans: 1.25]
16. The emf of a cell is balanced by a length of 120 cm of potentiometer wire. When the cell is shunted by a resistance of 10 Ω, the balancing length is reduced by 20 cm. Find the internal resistance of the cell.
    [Ans: r = 2 Ohm]
17. A potential drop per unit length along a wire is 5 x 10⁻³ V/m. If the emf of a cell balances against length 216 cm of this potentiometer wire, find the emf of the cell.
    [Ans: 0.01080 V]
18. The resistance of a potentiometer wire is 8 Ω and its length is 8 m. A resistance box and a 2 V battery are connected in series with it. What should be the resistance in the box, if it is desired to have a potential drop of 1μV/mm?
    [Ans: 1992 ohm]
19. Find the equivalent resistance between the terminals F and B in the network shown in the figure below given that the resistance of each resistor is 10 ohm.

**Diagram for Q19:**
A Wheatstone bridge-like network.
*   Points are F, A, C, B, E, D.
*   Resistors connect FA, AC, CB, FE, ED, DB.
*   There's also a resistor between C and E. This makes it a more complex network. The question mentions `I`, `I₁`, `I₂`, implying a current distribution. Let's assume standard Wheatstone bridge connections: F-A, A-C, F-E, E-C, C-B, E-D (D is probably the same point as B). The diagram shows connections: F-A, A-C, C-B, F-E, E-D, D-B and C-E. Let's assume each line segment is a 10Ω resistor. It forms a cube-like structure flattened on a plane. The nodes are F, A, E, C, D, B.

20. A voltmeter has a resistance of 100 Ω. What will be its reading when it is connected across a cell of emf 2 V and internal resistance 20 Ω?
    [Ans: 1.66 V]
***

---
*Page 229*
