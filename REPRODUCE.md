# Independent replica

Hash-check the locked logs, or rebuild them in a temp path and diff P1 means and W_crit. Never overwrite `logs/p1_contact_s1.json` or `logs/p1_da1_dose_s1.json`.

## Machine used for the lock

- Python 3.12.14
- numpy 2.5.3
- pytest 9.1.1
- macOS arm64

```
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python scripts/reproduce_lock.py
.venv/bin/python scripts/reproduce_lock.py --rerun
```

`--rerun` writes temp JSON for seed 1, 2,000 steps. It does not write under `logs/`.

## Expected sha256

| File | sha256 |
|------|--------|
| `logs/p1_contact_s1.json` | `117febfb78085c857f17c9bcc206113689c9a4c4b6dd5f081aa8befedfd897f4` |
| `logs/p1_da1_dose_s1.json` | `f0fabf87378319bedb5b66c434bb901f167867524b379067713a4603c3d1de57` |

Dynamics are saturating tanh units, dt = 0.05. Cells are type names, not MaleCNS body IDs.
