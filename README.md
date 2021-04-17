# Wrath & Glory XP Optimizer

Evert wondered if it is better to choose *Agility* over separate points into *Ballistic Skill* & *Stealth*? Ever thought that your current character has only *Intellect* but no points left for anything else?

This repo contains a Mixed-Integer Non-Linear Programming (MI-NLP) optimization solution to spending the optimal amount of XP on selected attributes, skills & traits in the role-playing game [Wrath & Glory by Cubicle 7](https://www.cubicle7games.com/our-games/wrath-glory/).

For simple character management, I recommend using the [Character Forge @ Doctors of Doom](https://www.doctors-of-doom.com/forge/my-characters). The XP optimizer can then be used on a created character to minimized the spent XP. Just pass in your desired target values (e.g. total value for *Cunning*, *Tech* & *Deception* and your desired *Strength*) and the optimizer will figure out the best distribution to use with minimal XP.

If you encounter any errors/wrong numbers please post your input & the expected values so I can debug them. If you have any recommendations, feel free to leave some comments.

The optimizer is written for the core ruleset v2.1. It does not take into account any species/archetype based bonuses/prerequisites - but these should be fine given that they use the same XP cost tables.

## Installation

- Install Python (3.8 or better) if not already done.
- Switch to folder of this project, open terminal & install requirements
  
   ```Bash
   pip install -r requirements.txt
   ```

- Try, if it works (shows help content)

   ```Bash
   python3 optimize-xp --help
   ```
  
## Usage

### NOTES

- You always have to specify the *tier* of your character!
- The optimizer takes the tree-of-learning rule into account, but assigns the skill ratings randomly (within the min-xp constraint). Simply move the 1s around to your liking - the xp cost stay the same.

### Via command-line interface (CLI)

The CLI takes a JSON file as input with the your tier and the target values you want to optimize (see tests/example_file.json for an example).

Let's say you want to optimize your *Tier* 1 character with *Strength* 3 and *Max Wounds* 5, the create a file (e.g. `my_file.json`) with the following content:

```json
{
  "Tier": 1,
  "Strength": 3,
  "MaxWounds": 5
}
```

Then run the following command from the same folder as the file:

```Bash
python optimize-xp my_file.json
```

which will output a markdown table showing the different propreties and their (total) ratings and the spent XP.

#### A more complex example

If you have a higher-level character and want to optimize the following properties at *Tier* 3

- *Agility* 5
- *BallisticSkill* 11
- *Cunning* 7
- *Deception* 8
- *Stealth* 12
- *Defence* 6 (note the British spelling!)
- *Max Wounds* 10

then create a file (e.g. `my_file.json`) with the following content:

```json
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

This time you'd like to have a json file as output. Then call:

```Bash
python optimize-xp my_file.json --output-format json
```

For a list of available CLI parameters use:

```Bash
python optimize-xp --help
```

---

## Derivation of the optimization formulas

**NOTE**: *The following section is best view in a latex-capable markdown viewer, otherwise the formulas will not be rendered and be readable only to the Tex-fetishist*
### Definitions

Name                | Abbreviation | Related Attribute | #Affected Skills/Attributes
------------------- | ------------ | ----------------- | ---------------------------
Tier                | Tier         | -                 | 3
*Attributes*        |
Agility             | Agi          | -                 | 3
Fellowship          | Fel          | -                 | 3
Initiative          | Ini          | -                 | 3
Intellect           | Int          | -                 | 3
Strength            | Str          | -                 | 3
Toughness           | Tou          | -                 | 3
Willpower           | Wil          | -                 | 3
*Skills*            |
Athletics           | Athl         | Str               | -
Awareness           | Awar         | Int               | 1
Ballistic Skill     | BaSk         | Agi               | -
Cunning             | Cunn         | Fel               | -
Deception           | Dece         | Fel               | -
Insight             | Insi         | Fel               | -
Intimidation        | Inti         | Wil               | -
Investigation       | Inve         | Int               | -
Leadership          | Lead         | Wil               | -
Medicae             | Medi         | Int               | -
Persuasion          | Pers         | Fel               | -
Pilot               | Pilo         | Agi               | -
Psychic Mastery     | PsMa         | Wil               | -
Scholar             | Scho         | Int               | -
Stealth             | Stea         | Agi               | -
Survival            | Surv         | Wil               | -
Tech                | Tech         | Int               | -
Weapon Skill        | WeSk         | Ini               | -
*Traits*|
Conviction          | Conv         | Wil               | -
Defence             | Defe         | Ini - 1           | -
Determination       | Dete         | Tou               | -
Influence           | Infl         | Fel - 1           | -
Max Shock           | MaSh         | Wil + Tier        | -
Max Wounds          | MaWo         | Tou + 2 * Tier    | -
Passive Awareness   | PaAw         | Awareness / 2     | -
Resilience          | Resi         | Tou + 1           | -
Resolve             | Reso         | Wil - 1           | -
Wealth              | Weal         | Tier              | -

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

---

## Requirements

### User requirements

#### General (GEN)

1. As a user I want a tool to optimize the XP cost for a given set of attributes, skills and traits.
2. As a user I want the optimized distribution to meet or exceed the point values for the given set.
3. As a user I want the XP cost of the optimized point values to be equal or lower than my current cost.
4. As a user I want all skill ratings that have to be added due to the "Tree-of-Learning"-constraint to be selectable.
5. As a user I want all skill ratings that have to be added due to the "Tree-of-Learning"-constraint to be chosen such they result in the highest possible total rating for the added skill ratings.
6. As a simple user I want my species-/archetype-specific prerequisites to be automatically met.
7. As an advanced user I want to be able to specify either the attribute/skill rating or its according total value to be the target for optimization (e.g. Deception rating vs. Deception total rating = Deception rating + Fellowship rating).
8. As a user I want the optimization to be fully integrated into the workflow of Doctors-of-Doom, automatically suggesting an optimized distribution upon changing the point distribution.

#### Deployment (DEP)

1. As a simple user I don't want to install/use an extra tool, but want an integrated workflow with Doctors-of-Doom.
2. As an advanced user I'm able to install a tool using a simple installer on my current OS.
3. As an expert user I'm able to install a tool using the command line and standard Python workflows.

#### UI (UI)

1. As a simple user I want to use the web-UI of Doctors-of-Doom.
2. As an advanced user I'm willing to use a separate tool with a GUI.
3. As an expert user I'm willing to use a CLI.

### Non-functional requirements (NFR)

1. Unit-test coverage is 100%.
2. CI/CD pipeline builds unit-tests & uses code analyzers on each pushed commit.
3. Project structure should follow existing templates.
4. Environments should be managed with standard tools.
5. Project follows PEP8 conventions.
6. Project has 0 code analyzer errors.
7. Project treats analyzer warnings as errors.
8. CI/CD pipeline rejects PRs if coverage is too low or analyzer problems exists.
9. All functions are documented.
