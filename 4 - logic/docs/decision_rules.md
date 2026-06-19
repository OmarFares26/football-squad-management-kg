# Decision Rules

## Purpose

This file explains the rule-based reasoning used to create
squad-management decisions.

The decision rules are designed to be simple, explainable, and directly
connected to the Knowledge Graph.

The final decisions are:

```text
Keep
Give More Chances
Loan
Sell
Monitor
```

These decisions are not meant to be professional scouting
recommendations. They are explainable project outputs based on the
available dataset.

## Input Data

The rule engine uses the scored player dataset:

```text
2 - construction/data/processed/player_scores.csv
```

This file already contains:

- cleaned player information
- role groups
- role-based performance scores
- performance percentiles
- performance levels

The rule engine then adds extra inferred context.

## Inferred Context

The rule engine creates the following inferred columns:

```text
age_group
minutes_group
same_role_team_average
competition_status
main_same_role_player
main_same_role_minutes
main_same_role_performance_percentile
main_same_role_performance_level
is_main_same_role_player
is_blocked_by_main_player
main_player_underperforming
decision
explanation
```

These columns are important because they turn raw statistics into
explainable Knowledge Graph reasoning.

## Age Groups

Players are assigned to age groups:

```text
age < 23       -> Young
age <= 29      -> Prime
age <= 32      -> Senior
age > 32       -> CriticalAge
```

Age is not used to block a Keep decision. A player can still be kept
if they play many minutes and perform well.

Age is mainly used in Sell and Loan reasoning.

## Minutes Groups

Players are assigned to minutes groups:

```text
minutes < 900        -> LowMinutes
minutes <= 1800      -> MediumMinutes
minutes > 1800       -> HighMinutes
```

Minutes help decide whether a player is a regular starter, rotation
player, or barely used player.

## Same-Role Competition

The main reasoning idea is:

```text
same team + same role group = squad competition
```

For each team and role group, the rule engine finds the main same-role
player.

The main same-role player is defined as:

```text
the player with the most minutes in the same team and role group
```

Other players in the same team and role group are compared with this
main player.

This creates the following context:

```text
main_same_role_player
is_main_same_role_player
is_blocked_by_main_player
main_player_underperforming
```

## Blocked by Main Player

A player is marked as blocked by the main same-role player if:

```text
the player is not the main same-role player
AND the player has fewer minutes than the main same-role player
AND the player has a lower performance score than the main same-role
    player
```

This creates the Knowledge Graph relationship:

```text
Player -> BLOCKED_BY_MAIN_PLAYER -> Main same-role player
```

This relationship is important because it makes the squad-competition
reasoning explicit in the graph.

## Main Player Underperforming

The main same-role player is marked as underperforming if:

```text
main_same_role_player performance percentile < 40
```

This is used to detect cases where a backup player may deserve more
minutes.

## Decision Rule Priority

Rules are applied in priority order.

This matters because the first matching rule becomes the final decision.

The priority order is:

```text
1. Keep regular contributor
2. Sell veteran underperformer
3. Give More Chances because main same-role player is underperforming
4. Give More Chances because player is competitive
5. Loan because young player is blocked
6. Sell low-used older player
7. Monitor
```

## Rule 1: Keep Regular Contributor

```text
IF minutes > 1800
AND performance_percentile >= 50
THEN Keep
```

A player with high minutes and at least promising role-based performance
is important for the squad.

Age is not used as a condition here. If a player is older but still
plays a lot and performs well, the system keeps them.

Example:

```text
Mohamed Salah -> Keep
Virgil van Dijk -> Keep
Alisson -> Keep
```

## Rule 2: Sell Veteran Underperformer

```text
IF minutes > 1800
AND performance_percentile < 40
AND age > 29
THEN Sell
```

An older player who plays regularly but performs poorly is a possible
sell candidate.

Example:

```text
Andrew Robertson -> Sell
```

This rule closes the gap where older high-minute underperformers would
otherwise only be monitored.

## Rule 3: Give More Chances Because Main Same-Role Player Is
Underperforming

```text
IF player is not the main same-role player
AND minutes < 1800
AND performance_percentile >= 50
AND main_player_underperforming = True
THEN Give More Chances
```

A backup or rotation player performs well while the main same-role
player is underperforming.

This is one of the most important project rules because it uses
same-role competition context.

Example:

```text
Wataru Endo -> Give More Chances
```

Explanation:

```text
Wataru Endo has low minutes and good performance.
The main same-role player is Curtis Jones.
Curtis Jones is underperforming at the 17th percentile.
Therefore, Wataru Endo should get more chances.
```

## Rule 4: Give More Chances Because Player Is Competitive

```text
IF minutes < 1800
AND performance_percentile >= 50
AND performance_score >= same_role_team_average
THEN Give More Chances
```

An underused player performs well compared with same-role teammates.

Example:

```text
Jarell Quansah -> Give More Chances
Harvey Elliott -> Give More Chances
Diogo Jota -> Give More Chances
```

This rule catches players who may deserve more minutes even if the
main same-role player is not underperforming.

## Rule 5: Loan Because Young Player Is Blocked

```text
IF age < 23
AND minutes < 900
AND is_blocked_by_main_player = True
THEN Loan
```

A young player has low minutes and is blocked by a stronger main
same-role player.

The purpose of a loan is development and regular game time.

The performance threshold was intentionally removed from the Loan rule.
A young blocked player with low minutes should be considered for loan
regardless of current performance level, because the purpose of a loan
is development, not current output.

Example:

```text
Conor Bradley -> Loan
Jayden Danns -> Loan
```

Explanation:

```text
Conor Bradley is young and has low minutes.
He is blocked by Virgil van Dijk in the same role group.
Therefore, the system recommends Loan.
```

## Rule 6: Sell Low-Used Older Player

```text
IF minutes < 900
AND performance_percentile < 40
AND age > 29
THEN Sell
```

An older player with low minutes and poor performance has limited
future value for the squad.

This rule captures players who are not regular contributors and are
not performing well.

## Rule 7: Monitor

```text
IF no stronger rule applies
THEN Monitor
```

The player does not clearly fit Keep, Sell, Loan, or Give More Chances.

Monitor is the neutral fallback decision.

This is important because not every player should receive a strong
action recommendation.

Example:

```text
Darwin Núñez -> Monitor
```

Darwin Núñez has good performance but is blocked by Mohamed Salah and
does not match the other action rules strongly enough. Monitor is the
honest recommendation for a player in a genuinely ambiguous situation.

## Liverpool Examples

Selected Liverpool examples from the final output:

```text
Mohamed Salah -> Keep
Wataru Endo -> Give More Chances
Conor Bradley -> Loan
Jayden Danns -> Loan
Andrew Robertson -> Sell
Darwin Núñez -> Monitor
```

Selected blocked-player examples:

```text
Conor Bradley -> blocked by Virgil van Dijk -> Loan
Jayden Danns -> blocked by Ryan Gravenberch -> Loan
Darwin Núñez -> blocked by Mohamed Salah -> Monitor
Andrew Robertson -> blocked by Virgil van Dijk -> Sell
```

## Why These Rules Are Useful for the Portfolio

The rules show that the project does not only create a graph from data.

It also adds inferred knowledge:

```text
age groups
minutes groups
performance levels
same-role competition context
blocked-by-main-player relationships
squad decisions
```

The reasoning follows a multi-step inference chain:

```text
raw statistics
-> performance score
-> competition status
-> blocked-by-main-player
-> final decision
```

Each step infers new knowledge from the previous one. This supports
Knowledge Graph reasoning because new facts are inferred from the
original data.

## Limitations

The decision rules are intentionally simple.

They do not use:

```text
contracts
salary
market value
injury history
coach preference
future potential
tactical instructions
```

Therefore, the decisions should be understood as educational,
explainable project outputs.

The correct way to present the system is:

```text
competition-aware rule-based squad decision support
```

not:

```text
professional football transfer recommendation system
```