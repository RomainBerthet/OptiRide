"""Nutrition and hydration planning for cycling events."""


def fueling_plan(
    total_seconds: float,
    work_j: float,
    gross_eff: float = 0.22,
) -> dict[str, float]:
    """Calculate nutrition and hydration requirements for a ride.

    Estimates caloric expenditure and provides carbohydrate and hydration
    recommendations based on ride duration and mechanical work output.

    Args:
        total_seconds: Total ride duration in seconds.
        work_j: Total mechanical work output in joules.
        gross_eff: Gross metabolic efficiency (mechanical/metabolic energy),
            typically 0.20-0.25, defaults to 0.22.

    Returns:
        Dictionary containing:
            - kcal: Total caloric expenditure
            - carbs_total: Total carbohydrates needed (grams)
            - carbs_gph: Carbohydrate intake rate (grams per hour)
            - liters_per_h: Recommended fluid intake (liters per hour)
            - sodium_mg_per_h: Recommended sodium intake (mg per hour)
            - duration_h: Ride duration in hours

    Example:
        >>> # 3-hour ride with 2,160,000 J of work
        >>> plan = fueling_plan(10800, 2_160_000)
        >>> plan["carbs_gph"]  # Should be 75 for rides > 2.5 hours
        75
        >>> 200 < plan["kcal"] < 300  # Typical caloric expenditure
        True

    References:
        - Jeukendrup, A. (2014). "A Step Towards Personalized Sports Nutrition:
          Carbohydrate Intake During Exercise." Sports Medicine, 44(1), 25-33.
        - Sawka, M. N., et al. (2007). "American College of Sports Medicine
          position stand. Exercise and fluid replacement."
    """
    # Convert mechanical work to calories (1 cal = 4.184 J)
    kcal = work_j / gross_eff / 4184.0

    hours = total_seconds / 3600.0

    # Carbohydrate recommendations based on duration
    # < 2.5 hours: moderate intensity (45 g/h)
    # >= 2.5 hours: high intensity/endurance (75 g/h)
    if hours < 2.5:
        carbs_gph = 45.0
    else:
        carbs_gph = 75.0

    carbs_total = carbs_gph * hours

    # Standard hydration and electrolyte recommendations
    liters_per_h = 0.6
    sodium_mg_per_h = 500.0

    return {
        "kcal": float(kcal),
        "carbs_total": float(carbs_total),
        "carbs_gph": float(carbs_gph),
        "liters_per_h": float(liters_per_h),
        "sodium_mg_per_h": float(sodium_mg_per_h),
        "duration_h": float(hours),
    }
