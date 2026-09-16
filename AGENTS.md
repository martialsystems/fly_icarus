# Agent notes: fly_icarus

MIT for original code. FlyWire and MaleCNS remain under their published licenses (typically CC BY 4.0).

Experiment 1 is a two-agent frozen-object assay. Subject: one male P1 slice (DA1 / ppk23 / LC10a live). Object: dummy body, frozen. Do not ask a population to answer this circuit question.

The frozen P1 question is closed for this slice. Do not unfreeze. Do not add `--female-brain-icarus` or `--n 1000` runs. Default Icarus transform never changes `wiring_sex`. Those flags stay stubbed.

The subject slice is a published-sign schema on MaleCNS / FlyWire type names. It is not a hop-count extract and not a live 166,691-cell LIF. LC10a here is a frozen size/shape proxy, not a T4/T5 motion extract.

Do not restamp FlyWire 139,255 or MaleCNS 166,691. Do not copy the fly_vial locked F sentence. The lock is the JSON table. Viewer HUD may name P1.

Pin is `icarusforge/`. Five laws: claim bans, wiring frozen, shared engine, template identity, assay order. Engine checkout `~/graphforge`. No catalog/`surfaces.json` unless the operator asks. Verify-before-done is the finish gate.

Schema-gate museum: `logs/p1_frozen_s1.json` (@1244f09). 3b museum: `logs/p1_terms_s1.json`. Contact lock: `logs/p1_contact_s1.json`. Never overwrite those three. DA1 dose lock: `logs/p1_da1_dose_s1.json` (W_crit = -1.5262 on the 3d pin). Allowed public sentence: In this 11-cell published-sign slice, rewriting odor to 7,11-HD with cVA off is necessary and sufficient for the 3≈1 gate. Icarus morphology, pinned contact, and feminized cuticle are not. That is a finding about these weights, not about MaleCNS.

## Verify

`python3 ~/agent_laws_verify_before_done/vbd_gate.py check --app-root . --claim-done`

`vbd.runtime.json` runs pytest, a short five-condition fixture, `icarusforge/scripts/sanity_icarusforge.py`, and viewer viewport when HTML/CSS changed. Do not use stock `/usr/bin/python3 -m pytest`.
