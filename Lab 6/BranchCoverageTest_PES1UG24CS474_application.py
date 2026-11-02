"""Branch-coverage tests for the Lab 6 recycling rewards application."""

import pytest

from recycling_rewards import collection_accepted, reward_points, slot_status


@pytest.mark.parametrize(
    ("material", "weight", "bonus", "expected"),
    [
        ("unknown", 1, False, ValueError),
        ("paper", -1, False, ValueError),
        ("paper", 5, False, 0),
        ("paper", 7, True, 18),
        ("metal", 2, True, 0),
        ("metal", 4, True, 24),
        ("plastic", 24, False, 210),
        ("metal", 23, False, 378),
    ],
)
def test_reward_points_branches(material, weight, bonus, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            reward_points(material, weight, bonus)
    else:
        assert reward_points(material, weight, bonus) == expected


@pytest.mark.parametrize(
    ("weight", "bags", "hazardous", "expected"),
    [
        (5, 4, True, True),
        (6, 1, True, False),
        (51, 1, False, False),
        (50, 3, False, True),
        (10, 4, False, False),
    ],
)
def test_collection_acceptance_branches(weight, bags, hazardous, expected):
    assert collection_accepted(weight, bags, hazardous) is expected


@pytest.mark.parametrize(
    ("minutes", "morning", "holiday", "expected"),
    [
        (20, True, False, "open"),
        (19, True, False, "late"),
        (4, True, False, "missed"),
        (25, False, True, "open"),
        (24, False, True, "late"),
        (9, False, False, "late"),
        (-6, False, True, "missed"),
    ],
)
def test_slot_status_branches(minutes, morning, holiday, expected):
    assert slot_status(minutes, morning, holiday) == expected
