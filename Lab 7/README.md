# Lab 7: Fuzz Testing

This lab uses Hypothesis to fuzz the recycling rewards parsers with arbitrary text and `None`, as well as generated valid inputs. Malformed inputs are rejected with a clear `ValueError`; valid inputs preserve the documented return values.

## Files

| File | Purpose |
| --- | --- |
| `recycling_rewards.py` | Input parsers and reward calculations, with validation for malformed or non-finite input |
| `test_recycling_rewards.py` | Hypothesis fuzz and property-based tests |

## Run the tests

Install `pytest` and `hypothesis`, then run from this directory:

```sh
pytest -q
```

The tests fuzz all three public functions with 300 arbitrary text or `None` examples each, then check their behavior across generated valid inputs.
