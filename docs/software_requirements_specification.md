# Software Requirements

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
