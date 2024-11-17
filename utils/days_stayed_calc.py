from rest_framework.exceptions import ValidationError
from datetime import time

def calculate_days_stayed(check_in_date, check_out_date, day_calculation_method):
    # Calculate days stayed based on the selected method
    if day_calculation_method == 'hotel_standard':
        # Hotel standard logic
        if check_in_date.time() < time(12, 0, 0):
            days_stayed = 1  # Count the first day if checked in before 12 PM
        else:
            days_stayed = 0  # No full day counted if checked in after 12 PM
        
        # Calculate full days in between
        full_days = (check_out_date.date() - check_in_date.date()).days - days_stayed
        
        # Add full days to days_stayed
        days_stayed += full_days
        
        # Updated logic for checkout time
        if check_out_date.time() < time(11, 59, 59):
            days_stayed = max(days_stayed, 1)  # Ensure at least 1 day if checked out before 11:59 AM
        elif check_out_date.time() >= time(12, 0, 0):
            days_stayed += 1  # Count an additional day if checked out after 12 PM
    elif day_calculation_method == '24h_basis':
        # 24h basis logic
        total_hours = (check_out_date - check_in_date).total_seconds() / 3600
        days_stayed = int(total_hours // 24) + (1 if total_hours % 24 > 0 else 0)
    else:
        raise ValidationError("Invalid day calculation method.")
    
    return days_stayed 

# Example:
# Check-in: October 1, 2023, 11:30 AM
# Check-out: October 3, 2023, 10:00 AM
# Method: 'hotel_standard'
# Days stayed: 2 (1 full day for October 2 and partial for October 1) 