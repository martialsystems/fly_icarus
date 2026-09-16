# fly_icarus

Does a live male P1 network (DA1 / ppk23 / motion still feeding it) treat a frozen grounded Icarus-from-male as a female?

Seed 1, 2,000 steps: Icarus-from-male P1 mean 0.9824 matches flying female 0.9824. Flying male is -0.6487 with song frac 0.000. Gate passed (d31 = 0.0, d32 = 1.976). The 7,11-HD plus female-shape tag reached P1. Two agents. Object frozen. Wiring sex stayed male.

Body-only (no HD) P1 0.7089 still courts. Odor-only (male silhouette, HD on) P1 0.9667. Either channel is enough; odor carries more of the rate.

If 3 had tracked 2, a later 1,000-fly box would be a physics toy. It did not. Do not ask a population to answer this circuit question.

Female template count: FlyWire 139,255 (Dorkenwald et al., *Nature* 2024), whole brain, no VNC. Male template count: MaleCNS 166,691 (Berg et al., *Cell* 2026), brain plus ventral nerve cord. The live net is 11 cells. Schema, not a hop-count extract, not a live 166,691-cell LIF. LC10a here is a frozen size/shape proxy.

## Locked metrics

Copied from `logs/p1_frozen_s1.json`. Seed 1, 2,000 steps, dt = 0.05.

| condition | object | P1 mean | orient frac | song frac | song bouts | attempts |
|----------:|--------|--------:|------------:|----------:|-----------:|---------:|
| 1 | flying female | 0.9824 | 0.994 | 0.982 | 1 | 1 |
| 2 | flying male | -0.6487 | 0.000 | 0.000 | 0 | 0 |
| 3 | frozen Icarus-from-male | 0.9824 | 0.994 | 0.982 | 1 | 1 |
| 4 | Icarus-from-male, odor off | 0.7089 | 0.992 | 0.975 | 1 | 1 |
| 5 | Icarus-from-male, female body off | 0.9667 | 0.993 | 0.979 | 1 | 1 |

Seeds 2 and 3 write `logs/p1_frozen_s2.json` and `logs/p1_frozen_s3.json`. They do not replace seed 1. Both pass the gate with Icarus P1 0.9824 vs flying male -0.6487. Seed 3 body-only P1 is 0.7107.

## Conditions

Same subject every row.

1. Intact flying female: positive control.
2. Intact flying male: negative control.
3. Frozen Icarus-from-male: the rule.
4. Frozen Icarus-from-male, odor off: morphology without 7,11-HD.
5. Frozen Icarus-from-male, female body off: 7,11-HD without the fat female shape.

## How to run

```
.venv/bin/python -m pytest
.venv/bin/python -m fly_icarus assay --seed 1 --steps 2000 --out logs/p1_frozen_s1.json
.venv/bin/python -m fly_icarus assay --seed 2 --steps 2000 --out logs/p1_frozen_s2.json
.venv/bin/python -m fly_icarus assay --seed 3 --steps 2000 --out logs/p1_frozen_s3.json
python3.12 viewer/scripts/viewport_sanity.py
```

`--n 1000`, `--unfreeze`, and `--female-brain-icarus` refuse until the seed-1 gate passes, and stay stubbed in this tree.

## Files

| Path | Role |
|------|------|
| `src/fly_icarus/` | Assay, P1 slice, Icarus flag, two-body physics |
| `data/templates/male_p1.json` | 11-cell published-sign schema |
| `logs/p1_frozen_s1.json` | Locked seed-1 five-condition run |
| `icarusforge/` | GraphForge pin: five refuse laws |
| `viewer/` | Two-body condition switcher. Not the finding. |
| `AGENTS.md` | Project rules and VBD |
| `THIRD_PARTY.md` | Connectome attribution |

[Fly research index](https://gist.github.com/martialsystems/12835f747d6360781f3cc7f91f243178)
