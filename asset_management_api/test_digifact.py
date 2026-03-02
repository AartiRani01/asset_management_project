from digifact import ProductionMetrics

factory = ProductionMetrics(
    total_time=564,
    ideal_production=1000,
    actual_count=875,
    total_count=1000,
    fault_count=10,
    total_downtime=60,
    total_uptime=375
)

print(factory.get_summary())