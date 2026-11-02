# Lab 6: Code and Branch Coverage

The recycling rewards module is tested with two separate pytest suites, as required by the lab handout.

## Files

| File | Purpose |
| --- | --- |
| `recycling_rewards.py` | Application code supplied with the assignment |
| `CodeCoverageTest_PES1UG24CS474_application.py` | Tests for line coverage (97%) |
| `BranchCoverageTest_PES1UG24CS474_application.py` | Tests for branch coverage (100%, 26 of 26 branches) |
| `Screenshots/CodeCoverage_PES1UG24CS474.png` | Line coverage command output |
| `Screenshots/BranchCoverage_PES1UG24CS474.png` | Branch coverage command output |

## Run the reports

Install `pytest` and `coverage`, then run these commands from this directory:

```sh
coverage run --source=recycling_rewards -m pytest -q CodeCoverageTest_PES1UG24CS474_application.py
coverage report -m --include='recycling_rewards.py'

coverage erase
coverage run --branch --source=recycling_rewards -m pytest -q BranchCoverageTest_PES1UG24CS474_application.py
coverage report -m --include='recycling_rewards.py'
```

The line suite covers 97% of executable statements. The branch suite covers all 26 decision branches.
