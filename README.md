# fly_icarus

Does a live male P1 network (DA1 / ppk23 / motion still feeding it) treat a frozen grounded Icarus-from-male as a female?

The live net is an 11-cell published-sign schema. Condition 3 equals condition 1 because both present the same signed channels to a saturating P1 unit, not because MaleCNS decided that. `@1244f09` (`logs/p1_frozen_s1.json`) is that schema gate. It passed. It is not a connectome courtship result.

P1 pre-activation, weights from `data/templates/male_p1.json`:

`P1 <- 1.2 ORN_HD - 1.8 DA1 + 0.8 ppk23_f - 0.8 ppk23_m + 0.9 LC10a + 0.35 P1`

Icarus-from-male as encoded turns HD on and cVA/DA1 off. That removes the only strong brake and leaves two excitatory tags plus a 0.35 latch. `d31 = 0.0` is the same feature vector twice. Seeds 2 and 3 matching the sign is a near-deterministic schema, not independent biological replication. LC10a here is a frozen size/shape bit. Song bouts = 1 is a threshold crossing: at dt = 0.05 the latch turns on at step 36 (1.8 s) and stays on. That is not a pulse-song motif.

## Control 3b (this lock)

Copied from `logs/p1_terms_s1.json`. Seed 1, 2,000 steps, dt = 0.05.

Frozen Icarus-from-male, body fat and wingless, odor still male (cVA on, HD off): P1 mean -0.4496, orient 0.000, song 0.000. Driver: odor_rewrite. The fat/wingless flag does not overrule male chemical identity. The schema-gate match of 3 to 1 is the odor rewrite (delete cVA, write HD). Shape still raises LC10a (0.392 vs flying-male 0.1725) and does not clear P1.

Condition 6, frozen Icarus-from-female, same body+odor as 3: P1 0.9824, `p1_d36 = 0.0`. The object-sex tag did not leak.

| condition | object | P1 mean | orient | song | bouts | onset | ORN_HD | DA1 | ppk23_f | ppk23_m | LC10a | 0.35 P1 |
|-----------|--------|--------:|-------:|-----:|------:|------:|-------:|----:|--------:|--------:|------:|--------:|
| 1 | flying female | 0.9824 | 0.994 | 0.982 | 1 | 36 | 0.9089 | 0.0 | 0.614 | 0.0 | 0.646 | 0.3438 |
| 2 | flying male | -0.6487 | 0.000 | 0.000 | 0 | | 0.0 | -0.7193 | 0.0 | 0.0 | 0.1725 | -0.227 |
| 3 | Icarus-from-male, HD | 0.9824 | 0.994 | 0.982 | 1 | 36 | 0.9084 | 0.0 | 0.614 | 0.0 | 0.6458 | 0.3438 |
| 3b | Icarus body, male odor | -0.4496 | 0.000 | 0.000 | 0 | | 0.0 | -0.7193 | 0.0 | 0.0 | 0.392 | -0.1574 |
| 4 | Icarus, odor off | 0.7089 | 0.9925 | 0.9755 | 1 | 49 | 0.0 | 0.0 | 0.0 | 0.0 | 0.6394 | 0.2481 |
| 5 | Icarus, male shape, HD | 0.9667 | 0.993 | 0.979 | 1 | 42 | 0.8989 | 0.0 | 0.6109 | 0.0 | 0.326 | 0.3383 |
| 6 | Icarus-from-female, HD | 0.9824 | 0.994 | 0.982 | 1 | 36 | 0.9086 | 0.0 | 0.614 | 0.0 | 0.6459 | 0.3438 |

Gate on 1 vs 2 vs 3: passed, d31 = 0.0, d32 = 1.976. Term columns are mean `W[P1, cell] * r[cell]` over ticks. HD and cVA are never on together. Either excitatory channel with DA1 off still clears song (4 and 5). That is a property of these weights.

Seeds 2 and 3: `logs/p1_terms_s2.json`, `logs/p1_terms_s3.json`. Same 3b driver. Seed 3 3b P1 -0.4487.

`--n 1000`, `--unfreeze`, and `--female-brain-icarus` stay stubbed. Unfreeze is experiment 2a after a control that can actually break. 3b did not.

Female template count: FlyWire 139,255 (Dorkenwald et al., *Nature* 2024), whole brain, no VNC. Male template count: MaleCNS 166,691 (Berg et al., *Cell* 2026), brain plus ventral nerve cord. The live net is 11 cells.

## Schema gate museum (@1244f09)

Copied from `logs/p1_frozen_s1.json`. Do not overwrite. Five conditions, no term columns, no 3b.

| condition | object | P1 mean | orient frac | song frac | song bouts | attempts |
|----------:|--------|--------:|------------:|----------:|-----------:|---------:|
| 1 | flying female | 0.9824 | 0.994 | 0.982 | 1 | 1 |
| 2 | flying male | -0.6487 | 0.000 | 0.000 | 0 | 0 |
| 3 | frozen Icarus-from-male | 0.9824 | 0.994 | 0.982 | 1 | 1 |
| 4 | Icarus-from-male, odor off | 0.7089 | 0.992 | 0.975 | 1 | 1 |
| 5 | Icarus-from-male, female body off | 0.9667 | 0.993 | 0.979 | 1 | 1 |

## Conditions

Same subject every row. Object frozen.

1. Intact flying female: positive control.
2. Intact flying male: negative control.
3. Frozen Icarus-from-male, HD on: the house-rule bundle.
3b. Frozen Icarus-from-male, fat/wingless, odor still male.
4. Frozen Icarus-from-male, odor off: morphology without 7,11-HD.
5. Frozen Icarus-from-male, female body off: 7,11-HD without the fat female shape.
6. Frozen Icarus-from-female: same body+odor as 3, female wiring tag.

## How to run

```
.venv/bin/python -m pytest
.venv/bin/python -m fly_icarus assay --seed 1 --steps 2000 --out logs/p1_terms_s1.json
.venv/bin/python -m fly_icarus assay --seed 2 --steps 2000 --out logs/p1_terms_s2.json
.venv/bin/python -m fly_icarus assay --seed 3 --steps 2000 --out logs/p1_terms_s3.json
python3.12 viewer/scripts/viewport_sanity.py
```

Do not overwrite `logs/p1_frozen_s1.json`.

## Files

| Path | Role |
|------|------|
| `src/fly_icarus/` | Assay, P1 slice, Icarus flag, two-body physics |
| `data/templates/male_p1.json` | 11-cell published-sign schema |
| `logs/p1_frozen_s1.json` | Schema gate museum, @1244f09 |
| `logs/p1_terms_s1.json` | Live lock: 3b, 6, P1 term columns |
| `icarusforge/` | GraphForge pin: five refuse laws |
| `viewer/` | Two-body condition switcher. Not the finding. |
| `AGENTS.md` | Project rules and VBD |
| `THIRD_PARTY.md` | Connectome attribution |

[Fly research index](https://gist.github.com/martialsystems/12835f747d6360781f3cc7f91f243178)
