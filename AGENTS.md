# Agent notes: fly_icarus

MIT for original code. FlyWire and MaleCNS remain under their published licenses (typically CC BY 4.0).

Experiment 1 is a two-agent frozen-object assay. Subject: one male P1 slice (DA1 / ppk23 / LC10a live). Object: dummy body, frozen. Do not ask a population to answer this circuit question.

Default Icarus transform never changes `wiring_sex`. Unfreeze, female-brain Icarus, and n>2 refuse until `logs/p1_frozen_s1.json` gate.passed is true. Those later assays are stubbed even after the gate.

The subject slice is a published-sign schema on MaleCNS / FlyWire type names. It is not a hop-count extract and not a live 166,691-cell LIF. LC10a here is a frozen size/shape proxy, not a T4/T5 motion extract.

Do not restamp FlyWire 139,255 or MaleCNS 166,691. Do not copy the fly_vial locked F sentence. The lock is the JSON table. Viewer HUD may name P1.

Pin is `icarusforge/`. Five laws: claim bans, wiring frozen, shared engine, template identity, assay order. Engine checkout `~/graphforge`. No catalog/`surfaces.json` unless the operator asks. Verify-before-done is the finish gate.

Schema-gate museum: `logs/p1_frozen_s1.json` (@1244f09). Never overwrite it. The live lock with 3b, 6, and P1 term columns is `logs/p1_terms_s1.json`. Seeds 2 and 3 write `logs/p1_terms_s2.json` and `logs/p1_terms_s3.json`. Unfreeze stays stubbed. The schema gate is not a MaleCNS courtship result.

## Verify

`python3 ~/agent_laws_verify_before_done/vbd_gate.py check --app-root . --claim-done`

`vbd.runtime.json` runs pytest, a short five-condition fixture, `icarusforge/scripts/sanity_icarusforge.py`, and viewer viewport when HTML/CSS changed. Do not use stock `/usr/bin/python3 -m pytest`.
