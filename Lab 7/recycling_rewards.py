import math


def _require_text(value):
    if not isinstance(value, str):
        raise ValueError("input must be a string")


def parse_collection(text):
    _require_text(text)
    parts = text.split(":")
    if len(parts) != 2 or not parts[0].strip():
        raise ValueError("collection must use material:weight format")
    try:
        weight = float(parts[1])
    except ValueError as exc:
        raise ValueError("weight must be numeric") from exc
    if not math.isfinite(weight):
        raise ValueError("weight must be finite")
    return parts[0].strip().title(), weight

def weight_average(weights_csv):
    _require_text(weights_csv)
    parts = weights_csv.split(",")
    if not parts or any(not value.strip() for value in parts):
        raise ValueError("weights must be a non-empty comma-separated list")
    try:
        values = [int(value) for value in parts]
    except ValueError as exc:
        raise ValueError("weights must be integers") from exc
    return sum(values) // len(values)

def net_points(text):
    _require_text(text)
    parts = text.split("|")
    if len(parts) != 2:
        raise ValueError("points must use points|penalty format")
    try:
        points, penalty = (float(value) for value in parts)
    except ValueError as exc:
        raise ValueError("points and penalty must be numeric") from exc
    if not math.isfinite(points) or not math.isfinite(penalty):
        raise ValueError("points and penalty must be finite")
    total = points * 2 - penalty
    if not math.isfinite(total):
        raise ValueError("net points must be finite")
    return max(total, 0)

def main():
    print("==== Running parse_collection ====")
    user_input = input("Enter material:weight in kg (e.g. paper:12): ")
    result = parse_collection(user_input)
    print("Material and Weight:", result)

    print("\n==== Running weight_average ====")
    user_input = input("Enter weights in kg as CSV (e.g. 5,12,20): ")
    result = weight_average(user_input)
    print("Average Weight:", result)

    print("\n==== Running net_points ====")
    user_input = input("Enter points|penalty (e.g. 80|10): ")
    result = net_points(user_input)
    print("Net Points:", result)

if __name__ == "__main__":
    main()
