from datetime import datetime
from utils.days_stayed_calc import calculate_days_stayed

# Test data
check_in_date_1 = datetime(2024, 12, 1, 14, 5)  # 2 PM
check_out_date_1 = datetime(2024, 12, 5, 10, 6)  # 10 AM
day_calculation_method_1 = 'hotel_standard'

# Test the function with the first set of values
days_stayed_1 = calculate_days_stayed(check_in_date_1, check_out_date_1, day_calculation_method_1)
print(f"Days stayed (Test 1): {days_stayed_1}")  # Expected output: 4

# Additional test data
check_in_date_2 = datetime(2023, 10, 1, 13, 0)  # 1 PM
check_out_date_2 = datetime(2023, 10, 3, 12, 0)  # 12 PM
day_calculation_method_2 = 'hotel_standard'

# Test the function with the second set of values
days_stayed_2 = calculate_days_stayed(check_in_date_2, check_out_date_2, day_calculation_method_2)
print(f"Days stayed (Test 2): {days_stayed_2}")  # Expected output: 2

# Another test with 24h basis
check_in_date_3 = datetime(2023, 10, 1, 10, 0)  # 10 AM
check_out_date_3 = datetime(2023, 10, 3, 10, 0)  # 10 AM
day_calculation_method_3 = '24h_basis'

# Test the function with the third set of values
days_stayed_3 = calculate_days_stayed(check_in_date_3, check_out_date_3, day_calculation_method_3)
print(f"Days stayed (Test 3): {days_stayed_3}")  # Expected output: 2 