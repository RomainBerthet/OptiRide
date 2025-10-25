def fueling_plan(total_seconds: float, work_J: float, gross_eff: float = 0.22):
    kcal = work_J / gross_eff / 4184.0
    hours = total_seconds/3600.0
    if hours < 2.5:
        carbs_gph = 45
    else:
        carbs_gph = 75
    carbs_total = carbs_gph*hours
    liters_per_h = 0.6
    sodium_mg_per_h = 500
    return dict(
        kcal=float(kcal),
        carbs_total=float(carbs_total),
        carbs_gph=float(carbs_gph),
        liters_per_h=float(liters_per_h),
        sodium_mg_per_h=float(sodium_mg_per_h),
        duration_h=float(hours)
    )
