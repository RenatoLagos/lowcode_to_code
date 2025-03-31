from datetime import datetime, timedelta

week_days = [0, 1, 2, 3, 4, 5, 6]

def binary_to_dictionary(code):
    binary = bin(code)[2:]  # Convert to binary without '0b' prefix
    # Make sure it has exactly 7 bits (padding with zeros on the left)
    binary = binary.zfill(7)
    # Convert binary string to list of integers and reverse it
    bits_array = [int(digit) for digit in binary][::-1]
    
    # Shift the array to match the desired order
    # Move the last element (Sunday) to the first position
    bits_array = bits_array[1:] + [bits_array[0]]
    
    # Create dictionary with weekdays in order from Monday to Sunday
    return {week_days[i]: bits_array[i] for i in range(7)}

def generate_calendar(days_dictionary, years=1):
    calendar = {}
    today = datetime.now()
    end_date = today + timedelta(days=365 * years)
    current_date = today

    while current_date <= end_date:   # Check if weekday is valid
        weekday = current_date.weekday()
        if weekday in days_dictionary:
            if days_dictionary[weekday] == 1:
                    calendar[current_date.strftime('%Y-%m-%d')] = current_date.strftime('%A')
        # Advance one day
        current_date += timedelta(days=1)

    return calendar

if __name__ == "__main__":
    days_dictionary = binary_to_dictionary(65)
    print("Days dictionary:", days_dictionary)  # Debug print
    calendar = generate_calendar(days_dictionary, years=1)
    print(calendar)