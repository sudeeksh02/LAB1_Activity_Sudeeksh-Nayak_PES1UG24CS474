"""Line-coverage tests for the Lab 6 recycling rewards application."""

from recycling_rewards import collection_accepted, reward_points, slot_status


def test_reward_points_for_supported_materials_and_bonus():
    assert reward_points("paper", 8, False) == 18
    assert reward_points("plastic", 5, True) == 18
    assert reward_points("metal", 4, True) == 24


def test_reward_points_above_high_volume_threshold():
    assert reward_points("paper", 30, False) == 250
    assert reward_points("metal", 30, False) == 504


def test_reward_points_validation_and_zero_award():
    import pytest

    with pytest.raises(ValueError, match="unknown material"):
        reward_points("glass", 4, False)
    with pytest.raises(ValueError, match="invalid weight"):
        reward_points("paper", -1, False)
    assert reward_points("metal", 1, False) == 0


def test_collection_acceptance_paths():
    assert collection_accepted(4, 8, True) is True
    assert collection_accepted(40, 3, False) is True
    assert collection_accepted(55, 1, False) is False


def test_slot_statuses():
    assert slot_status(30, True, False) == "open"
    assert slot_status(9, False, False) == "late"
    assert slot_status(0, True, False) == "missed"
