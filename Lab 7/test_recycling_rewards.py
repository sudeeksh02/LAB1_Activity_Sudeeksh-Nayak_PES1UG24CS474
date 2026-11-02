"""Property-based fuzz tests for the Lab 7 recycling rewards parsers."""

import math
import string

from hypothesis import given, settings, strategies as st

from recycling_rewards import net_points, parse_collection, weight_average


FUZZ_INPUTS = st.one_of(st.text(max_size=64), st.none())


@settings(max_examples=300, deadline=None)
@given(FUZZ_INPUTS)
def test_parse_collection_no_unexpected_crash(value):
    try:
        material, weight = parse_collection(value)
    except ValueError:
        return

    assert isinstance(value, str)
    assert material
    assert material == material.strip().title()
    assert math.isfinite(weight)


@settings(max_examples=300, deadline=None)
@given(FUZZ_INPUTS)
def test_weight_average_no_unexpected_crash(value):
    try:
        result = weight_average(value)
    except ValueError:
        return

    assert isinstance(value, str)
    values = [int(part) for part in value.split(",")]
    assert result == sum(values) // len(values)


@settings(max_examples=300, deadline=None)
@given(FUZZ_INPUTS)
def test_net_points_no_unexpected_crash(value):
    try:
        result = net_points(value)
    except ValueError:
        return

    assert isinstance(value, str)
    points, penalty = (float(part) for part in value.split("|"))
    assert math.isfinite(result)
    assert result == max(points * 2 - penalty, 0)


@given(
    st.text(alphabet=string.ascii_letters, min_size=1, max_size=20),
    st.floats(min_value=-1e100, max_value=1e100, allow_nan=False, allow_infinity=False),
)
def test_parse_collection_accepts_generated_valid_values(material, weight):
    result_material, result_weight = parse_collection(f"{material}:{weight!r}")
    assert result_material == material.title()
    assert result_weight == weight


@given(st.lists(st.integers(min_value=-10**6, max_value=10**6), min_size=1, max_size=30))
def test_weight_average_matches_integer_floor_average(values):
    csv = ",".join(map(str, values))
    assert weight_average(csv) == sum(values) // len(values)


@given(
    st.floats(min_value=-1e100, max_value=1e100, allow_nan=False, allow_infinity=False),
    st.floats(min_value=-1e100, max_value=1e100, allow_nan=False, allow_infinity=False),
)
def test_net_points_applies_double_points_then_floor_at_zero(points, penalty):
    expected = max(points * 2 - penalty, 0)
    assert net_points(f"{points!r}|{penalty!r}") == expected
