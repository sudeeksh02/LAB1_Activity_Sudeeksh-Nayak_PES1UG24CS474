MIN_KG = {"paper": 5, "plastic": 3, "metal": 2}


def reward_points(material, weight_kg, has_bonus):
    if material not in MIN_KG:
        raise ValueError("unknown material")
    if weight_kg < 0:
        raise ValueError("invalid weight")
    minimum = MIN_KG[material]
    if has_bonus and material != "metal":
        minimum -= 1
    extra = weight_kg - minimum
    if extra <= 0:
        return 0
    if material == "metal":
        rate = 12
    else:
        rate = 6
    if extra > 20:
        rate = rate + 4
        if material == "metal":
            rate += 2
    return extra * rate


def collection_accepted(weight_kg, bags, is_hazardous):
    if is_hazardous:
        return weight_kg <= 5
    if weight_kg > 50:
        return False
    return bags <= 3


def slot_status(minutes_left, is_morning, is_holiday):
    if is_morning:
        cutoff = 20
    else:
        cutoff = 10
    if is_holiday:
        cutoff += 15
    if minutes_left >= cutoff:
        return "open"
    elif minutes_left >= cutoff - 15:
        return "late"
    return "missed"
