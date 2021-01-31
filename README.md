# Wrath & Glory XP Optimizer

This repo contains a Mixed-Integer Non-Linear Programming (MI-NLP) optimization solution to spending the optimal amount of XP on selected attributes, skills & derived properties in the role-playing game [Wrath & Glory by Cubicle 7](https://www.cubicle7games.com/our-games/wrath-glory/).

For simple character management, I recommend using the [Character Forge @ Doctors of Doom](https://www.doctors-of-doom.com/forge/my-characters). The XP optimizer can then be used on a created character to minimized the spent XP.

If you encounter any errors/wrong numbers please post your input & the expected values so I can debug them. If you have any recommendations, feel free to leave some comments.

The optimizer is written for the core ruleset v2.1. It does not take into account any species/archetype based bonuses/prerequisites - but these should be fine given that they use the same XP cost tables.

## Installation

- Install Python (3.6 or better) if not already done.
- Switch to folder of this project, open terminal & install requirements
  
   ```Bash
   pip install -r requirements.txt
   ```

- Try, if it works (shows help content)

   ```Bash
   python xpOptimizer.py -h
   ```
  
## Usage

**NOTE**: You always have to specify the *tier* of your character!

The optimizer takes the tree-of-learning rule into account, but assigns the skill ratings randomly (within the min-xp constraint). Simply move the 1s around to your liking - the xp cost stay the same.

### Purely via command-line arguments

For few target properties it is best to use the command-line arguments, e.g. if you want to optimize your *tier* 1 character with *Strength* 3 and *Max Wounds* 5, type:

```Bash
python xpOptimizer.py --tier 1 --Strength 3 --MaxWounds 5
```

which will output the following markdown table:

```Markdown
## Tier
1

## Attributes
Name         | Total  | Target | Missed
------------ | ------ | ------ | ------
Agility      | 1      | -      | -     
Fellowship   | 1      | -      | -     
Initiative   | 1      | -      | -     
Intelligence | 1      | -      | -     
Strength     | 3      | 3      | NO    
Toughness    | 3      | -      | -     
Willpower    | 1      | -      | -     

## Skills
Name           | Rating | Total  | Target | Missed
-------------- | ------ | ------ | ------ | ------
Athletics      | 0      | 3      | -      | -     
Awareness      | 0      | 1      | -      | -     
BallisticSkill | 0      | 1      | -      | -     
Cunning        | 0      | 1      | -      | -     
Deception      | 0      | 1      | -      | -     
Insight        | 0      | 1      | -      | -     
Intimidation   | 0      | 1      | -      | -     
Investigation  | 0      | 1      | -      | -     
Leadership     | 0      | 1      | -      | -     
Medicae        | 0      | 1      | -      | -     
Persuasion     | 0      | 1      | -      | -     
Pilot          | 0      | 1      | -      | -     
PsychicMastery | 0      | 1      | -      | -     
Scholar        | 0      | 1      | -      | -     
Stealth        | 0      | 1      | -      | -     
Survival       | 0      | 1      | -      | -     
Tech           | 0      | 1      | -      | -     
WeaponSkill    | 0      | 1      | -      | -     

## DerivedProperties
Name          | Total  | Target | Missed
------------- | ------ | ------ | ------
Conviction    | 1      | -      | -     
Defence       | 0      | -      | -     
Determination | 3      | -      | -     
Influence     | 0      | -      | -     
MaxShock      | 2      | -      | -     
MaxWounds     | 5      | 5      | NO    
Resilience    | 4      | -      | -     
Resolve       | 0      | -      | -     

## XPCost
Name       | Cost
---------- | ----
Attributes | 20  
Skills     | 0   
Total      | 20
```

If you prefer json instead of markdown, use the `--return_json` flag:

```Bash
python xpOptimizer.py --tier 1 --Strength 3 --MaxWounds 5 --return_json
```

which will create:

```JSON
{
  "Tier": 1,
  "Attributes": {
    "Total": {
      "Agility": 1,
      "Fellowship": 1,
      "Initiative": 1,
      "Intelligence": 1,
      "Strength": 3,
      "Toughness": 3,
      "Willpower": 1
    },
    "Target": {
      "Strength": 3
    },
    "Missed": []
  },
  "Skills": {
    "Rating": {
      "Athletics": 0,
      "Awareness": 0,
      "BallisticSkill": 0,
      "Cunning": 0,
      "Deception": 0,
      "Insight": 0,
      "Intimidation": 0,
      "Investigation": 0,
      "Leadership": 0,
      "Medicae": 0,
      "Persuasion": 0,
      "Pilot": 0,
      "PsychicMastery": 0,
      "Scholar": 0,
      "Stealth": 0,
      "Survival": 0,
      "Tech": 0,
      "WeaponSkill": 0
    },
    "Total": {
      "Athletics": 3,
      "Awareness": 1,
      "BallisticSkill": 1,
      "Cunning": 1,
      "Deception": 1,
      "Insight": 1,
      "Intimidation": 1,
      "Investigation": 1,
      "Leadership": 1,
      "Medicae": 1,
      "Persuasion": 1,
      "Pilot": 1,
      "PsychicMastery": 1,
      "Scholar": 1,
      "Stealth": 1,
      "Survival": 1,
      "Tech": 1,
      "WeaponSkill": 1
    },
    "Target": {},
    "Missed": []
  },
  "DerivedProperties": {
    "Total": {
      "Conviction": 1,
      "Defence": 0,
      "Determination": 3,
      "Influence": 0,
      "MaxShock": 2,
      "MaxWounds": 5,
      "Resilience": 4,
      "Resolve": 0
    },
    "Target": {
      "MaxWounds": 5
    },
    "Missed": []
  },
  "XPCost": {
    "Attributes": 20,
    "Skills": 0,
    "Total": 20
  }
}
```

### File-based input via command-line

If you have several properties you want to set, or simple want to keep single file for your character, use the json-file with the `--file` command-line argument. The json file is a simple flat json with at least the *tier* field.  For example if you want to optimize your *tier* 3 character with *Agility* 5, *BallisticSkill* 11, *Cunning* 7, *Defence* 4 (note the British spelling!) and *Max Wounds* 10, create a file (e.g. `TestChar.json`) with the following content:

```JSON
{
  "Tier": 3,
  "Agility": 5,
  "BallisticSkill": 11,
  "Cunning": 7,
  "Deception": 8,
  "Stealth": 12,
  "Defence": 6,
  "MaxWounds": 10
}
```

then call (assuming the file is in the same folder as the optimizer script):

```Bash
python xpOptimizer.py --file TestChar.json
```

---

## Derivation of the optimization formulas

**NOTE**: *The following section is best view in a latex-capable markdown viewer, otherwise the formulas will not be rendered and be readable only to the Tex-fetishist*
### Definitions

Name                | Abbreviation | Related Attribute
------------------- | ------------ | -----------------
Tier                | Tier         | -
*Attributes*        |
Agility             | Agi          | -
Fellowship          | Fel          | -
Initiative          | Ini          | -
Intellect           | Int          | -
Strength            | Str          | -
Toughness           | Tou          | -
Willpower           | Wil          | -
*Skills*            |
Athletics           | Athl         | Str
Awareness           | Awar         | Int
Ballistic Skill     | BaSk         | Agi
Cunning             | Cunn         | Fel
Deception           | Dece         | Fel
Insight             | Insi         | Fel
Intimidation        | Inti         | Wil
Investigation       | Inve         | Int
Leadership          | Lead         | Wil
Medicae             | Medi         | Int
Persuasion          | Pers         | Fel
Pilot               | Pilo         | Agi
Psychic Mastery     | PsMa         | Wil
Scholar             | Scho         | Int
Stealth             | Stea         | Agi
Survival            | Surv         | Wil
Tech                | Tech         | Int
Weapon Skill        | WeSk         | Ini
*Derived Properties*|
Conviction          | Conv         | Wil
Defence             | Defe         | Ini - 1
Determination       | Dete         | Tou
Influence           | Infl         | Fel - 1
Max Shock           | MaSh         | Wil + Tier
Max Wounds          | MaWo         | Tou + 2 * Tier
Passive Awareness   | PaAw         | Awareness / 2
Resilience          | Resi         | Tou + 1
Resolve             | Reso         | Wil - 1
Wealth              | Weal         | Tier

Name             | Symbol
---------------- | ------
*Attribute*      |
Names            | $A = \left\{Agi, Fel, Ini, Int, Str, Tou, Wil\right\}, \|A\|=7$
Rating           | $r_a \in \left\{r \in \mathbb{N}: 1 \leq r \leq 12\right\}, a \in A$
Ratings (Set)    | $R_A = \left\{r_a : \forall a \in A\right\}$
Ratings (Vector) | $\vec{r}_A = \left(r_{Agi}, r_{Fel}, r_{Ini}, r_{Int}, r_{Str}, r_{Tou}, r_{Wil}\right)^T$
*Skill*          |
Names            | $S = \{Athl, Awar, BaSk, Cunn, Dece, Insi, Inti, Inve, Lead, Medi, Pers, Pilo, PsMa, Scho, Stea, Surv, Tech, WeSk\}, \|S\|=18$
Rating           | $r_s \in \left\{r \in \mathbb{N}: 0 \leq r \leq 8\right\}, s \in S$
Ratings (Set)    | $R_S = \left\{r_s : \forall s \in S\right\}$
Ratings (Vector) | $\vec{r}_S = \left(r_{Athl}, r_{Awar}, r_{BaSk}, r_{Cunn}, r_{Dece}, r_{Insi}, r_{Inti}, r_{Inve}, r_{Lead}, r_{Medi}, r_{Pers}, r_{Pilo}, r_{PsMa}, r_{Scho}, r_{Stea}, r_{Surv}, r_{Tech}, r_{WeSk}\right)^T$
*Overall*        |
Target values    | $\vec{b}, b_i \in \mathbb{N}_0, \|\vec{b}\|_0 \geq 0$, can be defined for skill & property values (except Wealth since Tier is fixed & passive awareness since it is derived from awareness)

### Cost functions

XP Cost                | Symbol                | Formula                                                                                          | Range                | Note
---------------------- | --------------------- | ------------------------------------------------------------------------------------------------ | -------------------- | --------------------------
Attribute (cumulative) | $c_A\left(r_a\right)$ | $(k - 1) \cdot (k + 2) + 2.5 \cdot (r_a - k) \cdot \left(r_a + k - 3 \right),~~k = \min(r_a, 3)$ | $\left[0,280\right]$ | See below
Skill (cumulative)     | $c_S\left(r_s\right)$ | $\sum^{r_s}_{i = 1} 2i \Leftrightarrow r_s^2 + r_s$                                              | $\left[0, 72\right]$ | Rule of Triangular Numbers

#### XP cost for attributes

The attribute cost is originally given as table:

$r_a$ | $c_A(r_a)$ | $\Delta c_A(r_a)$ |$\Delta^2 c_A(r_a)$
----- | ---------- | ----------------- | ------------------
 1    |   0        |  0                | 0
 2    |   4        |  4                | 4
 3    |  10        |  6                | 2
 4    |  20        | 10                | 4
 5    |  35        | 15                | 5
 6    |  55        | 20                | 5
 7    |  80        | 25                | 5
 8    | 110        | 30                | 5
 9    | 145        | 35                | 5
10    | 185        | 40                | 5
11    | 230        | 45                | 5
12    | 280        | 50                | 5

The incremental attribute cost in tabular form can be rewritten as:
$$
    \Delta c_A\left(r_a\right) =
        \begin{cases}
            0                   & \text{if } r_a = 1 \\
            2r_a                & \text{if } r_a \in \{2, 3\} \\
            5 \cdot (r_a - 2)   & \text{if } r_a \geq 4 \\
        \end{cases}
$$

In the following, we will use the rule for Triangular Numbers, which is given for the range $\left[1, b\right], b \in \mathbb{N}_1$ by:
$$
    \sum^{b}_{i = 1} i = \frac{b \cdot (b + 1)}{2}
$$

and can be extended to arbitrary ranges $\left[a + 1, m = a + b\right], a \in \mathbb{N}_0$ by:
$$
    \begin{aligned}
        \sum^{m}_{i = a + 1} i  &= \sum^{m}_{i = 1} i           &-  &\sum^{a}_{i = 1} i \\
                                &= \frac{m \cdot (m + 1)}{2}    &-  &\frac{a \cdot (a + 1)}{2} \\
    \end{aligned}
$$

which, when resolving $m = a + b$, is equal to:
$$
        \sum^{a + b}_{i = a + 1} i = \frac{b \cdot (b + 2a + 1)}{2}
$$

The switch criterion between the cases of the incremental attribute cost can be defined as:
$$
    k = \min({r_a, 3})
$$

The cumulative attribute cost is given by:
$$
    c_A\left(r_a\right) = \sum^{r_a}_{i = 1} \Delta c_A\left(r_a\right)\\
$$

which, using the switch criterion and the rule for Triangular Numbers, can be rewritten asy:
$$
    \begin{aligned}
        c_A\left(r_a\right) &= 0 + \sum^{k}_{i = 2} 2i                &+ &\sum^{r_a}_{i = k + 1} 5 \cdot (r_a - 2) \\
                            &= 0 + 2\sum^{1 + (k - 1)}_{i = 1 + 1} i  &+ &5 \cdot \left(\sum^{k + (r_a - k)}_{i = k + 1} r_a - \sum^{r_a}_{i = k + 1} 2 \right) \\
                            &= 2 \cdot \frac{(k - 1) \cdot ((k - 1) + 2 + 1)}{2} &+ &5 \cdot \left(\frac{(r_a - k) \cdot ((r_a - k) + 2k + 1)}{2} - 2 \cdot (r_a - k) \right) \\
                            &= (k - 1) \cdot (k + 2) &+ &2.5 \cdot (r_a - k) \cdot \left(r_a + k - 3 \right)
    \end{aligned}
$$

which, when resolving the switch criterion, results in the alternate form:
$$
    c_A\left(r_a\right) =
        \begin{cases}
            (r_a - 1) \cdot (r_a + 2)                           & \text{if } r_a \leq 2  \Rightarrow k = r_a \\
            2.5 \cdot \left( r_a \cdot (r_a - 3) + 4 \right)    & \text{if } r_a \geq 3 \Rightarrow k = 3 \\
        \end{cases}
$$

#### Total XP cost

The total cost is given by:
$$
    \begin{aligned}
        C\left(\vec{r}_A, \vec{r}_S\right) &= \sum^{\|A\|}_{a = 1} c_A\left(r_a\right) &+ &\sum^{\|S\|}_{s = 1} c_S\left(r_s\right) \\
                                &= \sum^{\|A\|}_{a = 1} \left( (k - 1) \cdot (k + 2) + 2.5 \cdot (r_a - k) \cdot \left(r_a + k - 3 \right) \right) &+ &\sum^{\|S\|}_{s = 1} r_s \cdot (r_s + 1)\\
    \end{aligned}
$$

### Problem statement

$$
    \begin{aligned}
        \text{minimize }    & C\left(\vec{r}_A, \vec{r}_S\right) \\
        \text{subject to }  & M_A \cdot \vec{r}_A + M_S \cdot \vec{r}_S + \vec{c}=\vec{b}                              & &\text{target values} \\
        \text{and }         & \| \vec{r}_S \|_0 \geq \| \vec{r}_S \|_\infty & &\text{"tree of learning"} \\
    \end{aligned}
$$

with the maximal set of constraints for the target values given by:
$$
    \begin{matrix}
        Athl \\
        Awar \\
        BaSk \\
        Cunn \\
        Dece \\
        Insi \\
        Inti \\
        Inve \\
        Lead \\
        Medi \\
        Pers \\
        Pilo \\
        PsMa \\
        Scho \\
        Stea \\
        Surv \\
        Tech \\
        WeSk \\
        \\
        Conv \\
        Defe \\
        Dete \\
        Infl \\
        MaSh \\
        MaWo \\
        Resi \\
        Reso \\
    \end{matrix}
    \left(
    \begin{matrix}
        0 & 0 & 0 & 0 & 1 & 0 & 0 \\
        0 & 0 & 0 & 1 & 0 & 0 & 0 \\
        1 & 0 & 0 & 0 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 0 & 1 \\
        0 & 0 & 0 & 1 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 0 & 1 \\
        0 & 0 & 0 & 1 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 & 0 & 0 & 0 \\
        1 & 0 & 0 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 0 & 1 \\
        0 & 0 & 0 & 1 & 0 & 0 & 0 \\
        1 & 0 & 0 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 0 & 1 \\
        0 & 0 & 0 & 1 & 0 & 0 & 0 \\
        0 & 0 & 1 & 0 & 0 & 0 & 0 \\
        \\
        0 & 0 & 0 & 0 & 0 & 0 & 1 \\
        0 & 0 & 1 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 1 & 0 \\
        0 & 1 & 0 & 0 & 0 & 0 & 0 \\
        0 & 0 & 0 & 0 & 0 & 0 & 1 \\
        0 & 0 & 0 & 0 & 0 & 1 & 0 \\
        0 & 0 & 0 & 0 & 0 & 1 & 0 \\
        0 & 0 & 0 & 0 & 0 & 0 & 1 \\
    \end{matrix}
    \right)
    \cdot
    \vec{r}_{A}
    +
    \left(
    \begin{matrix}
        \\
        \\
        \\
        \\
        \\
        \\
        \\
        \\
        \\
        \mathbf{I}_{\|S\|}\\
        \\
        \\
        \\
        \\
        \\
        \\
        \\
        \\
        \\
        \\
        \\
        \\
        \mathbf{0}\\
        \\
        \\
        \\
        \\
    \end{matrix}
    \right)
    \cdot
    \vec{r}_{S}
    +
    \left(
    \begin{matrix}
        \\
        \\
        \\
        \\
        \\
        \\
        \\
        \\
        \\
        \vec{0} \\
        \\
        \\
        \\
        \\
        \\
        \\
        \\
        \\
        \\
        0 \\
        -1 \\
        0 \\
        -1 \\
        Tier \\
        2 \cdot Tier \\
        1 \\
        -1 \\
    \end{matrix}
    \right)
    =
    \left(
    \begin{matrix}
        b_{Athl} \\
        b_{Awar} \\
        b_{BaSk} \\
        b_{Cunn} \\
        b_{Dece} \\
        b_{Insi} \\
        b_{Inti} \\
        b_{Inve} \\
        b_{Lead} \\
        b_{Medi} \\
        b_{Pers} \\
        b_{Pilo} \\
        b_{PsMa} \\
        b_{Scho} \\
        b_{Stea} \\
        b_{Surv} \\
        b_{Tech} \\
        b_{WeSk} \\
        \\
        b_{Conv} \\
        b_{Defe} \\
        b_{Dete} \\
        b_{Infl} \\
        b_{MaSh} \\
        b_{MaWo} \\
        b_{Resi} \\
        b_{Reso} \\
    \end{matrix}
    \right)
$$
