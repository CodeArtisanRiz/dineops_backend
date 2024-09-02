# Booking Flow

# **Scenario 1: Single ID for Entire Booking.**

Use Case:

- Booking: A single guest books one or more rooms.
- Check-in: Each room is checked in independently.
- Check-out: Each room is checked out independently.

Booking:

```json
{
    "booking_date": "2023-10-01T12:00:00Z",
    "from_date": "2023-10-10",
    "to_date": "2023-10-15",
    "scenario": 1,
    "guests": [
        {
            "id": 10,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "",
            "dob": null,
            "address": "123 Main St, Springfield",
            "identification": "file",
            "status": 1 // Pending
        }
    ],
    "rooms": [
        {
            "room_number": "101",
            "price_per_day": "100.00",
            "check_in": null,
            "check_out": null,
            "no_of_days_stayed": null,
            "room_status": "available",
            "paid_amount": null,
            "discount": null,
            "food": [],
            "services": [],
            "total_amount": null,
            "payment_method": null,
            "guests": [10]
        }
    ],
    "total_amount_per_booking": null
}
```

Check-in:

```json
{
    "rooms": [
        {
            "room_number": "101",
            "check_in": "2023-10-10T14:00:00Z",
            "room_status": "occupied"
        }
    ]
}
```

Check-out:

```json
{
    "rooms": [
        {
            "room_number": "101",
            "check_out": "2023-10-15T12:00:00Z",
            "no_of_days_stayed": 5,
            "room_status": "available",
            "paid_amount": "500.00",
            "discount": "0.00",
            "total_amount": "500.00",
            "payment_method": 1 // Cash
        }
    ],
    "total_amount_per_booking": "500.00"
}
```

# Scenario 2: Single ID per Room

Use Case:

- Booking: Multiple guests book separate rooms.
- Check-in: Each room is checked in independently.
- Check-out: Each room is checked out independently.

Booking:

```json
{
    "booking_date": "2023-10-01T12:00:00Z",
    "from_date": "2023-10-10",
    "to_date": "2023-10-15",
    "scenario": 2,
    "guests": [
        {
            "id": 10,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "",
            "dob": null,
            "address": "123 Main St, Springfield",
            "identification": "file",
            "status": 1 // Pending
        },
        {
            "id": 11,
            "first_name": "Jane",
            "last_name": "Smith",
            "phone": "",
            "dob": null,
            "address": "456 Elm St, Springfield",
            "identification": "file",
            "status": 1 // Pending
        }
    ],
    "rooms": [
        {
            "room_number": "101",
            "price_per_day": "100.00",
            "check_in": null,
            "check_out": null,
            "no_of_days_stayed": null,
            "room_status": "available",
            "paid_amount": null,
            "discount": null,
            "food": [],
            "services": [],
            "total_amount": null,
            "payment_method": null,
            "guests": [10]
        },
        {
            "room_number": "102",
            "price_per_day": "120.00",
            "check_in": null,
            "check_out": null,
            "no_of_days_stayed": null,
            "room_status": "available",
            "paid_amount": null,
            "discount": null,
            "food": [],
            "services": [],
            "total_amount": null,
            "payment_method": null,
            "guests": [11]
        }
    ],
    "total_amount_per_booking": null
}
```

Check-in:

```json
{
    "rooms": [
        {
            "room_number": "101",
            "check_in": "2023-10-10T14:00:00Z",
            "room_status": "occupied"
        },
        {
            "room_number": "102",
            "check_in": "2023-10-10T14:00:00Z",
            "room_status": "occupied"
        }
    ]
}
```

Check-out:

```json
{
    "rooms": [
        {
            "room_number": "101",
            "check_out": "2023-10-15T12:00:00Z",
            "no_of_days_stayed": 5,
            "room_status": "available",
            "paid_amount": "500.00",
            "discount": "0.00",
            "total_amount": "500.00",
            "payment_method": 1 // Cash
        },
        {
            "room_number": "102",
            "check_out": "2023-10-15T12:00:00Z",
            "no_of_days_stayed": 5,
            "room_status": "available",
            "paid_amount": "600.00",
            "discount": "0.00",
            "total_amount": "600.00",
            "payment_method": 2 // Credit Card
        }
    ],
    "total_amount_per_booking": "1100.00"
}
```

# Scenario 3: All Guests ID

Use Case:

- Booking: Multiple guests book one or more rooms, and some rooms may be shared.
- Check-in: Each room is checked in independently.
- Check-out: Each room is checked out independently.

Booking:

```json
{
    "booking_date": "2023-10-01T12:00:00Z",
    "from_date": "2023-10-10",
    "to_date": "2023-10-15",
    "scenario": 3,
    "guests": [
        {
            "id": 10,
            "first_name": "John",
            "last_name": "Doe",
            "phone": "",
            "dob": null,
            "address": "123 Main St, Springfield",
            "identification": "file",
            "status": 1 // Pending
        },
        {
            "id": 11,
            "first_name": "Jane",
            "last_name": "Smith",
            "phone": "",
            "dob": null,
            "address": "456 Elm St, Springfield",
            "identification": "file",
            "status": 1 // Pending
        }
    ],
    "rooms": [
        {
            "room_number": "101",
            "price_per_day": "100.00",
            "check_in": null,
            "check_out": null,
            "no_of_days_stayed": null,
            "room_status": "available",
            "paid_amount": null,
            "discount": null,
            "food": [],
            "services": [],
            "total_amount": null,
            "payment_method": null,
            "guests": [10, 11] // Both guests share this room
        }
    ],
    "total_amount_per_booking": null
}
```

Check-in:

```json
{
    "rooms": [
        {
            "room_number": "101",
            "check_in": "2023-10-10T14:00:00Z",
            "room_status": "occupied"
        }
    ]
}
```

Check-out:

```json
{
    "rooms": [
        {
            "room_number": "101",
            "check_out": "2023-10-15T12:00:00Z",
            "no_of_days_stayed": 5,
            "room_status": "available",
            "paid_amount": "500.00",
            "discount": "0.00",
            "total_amount": "500.00",
            "payment_method": 1 // Cash
        }
    ],
    "total_amount_per_booking": "500.00"
}
```

## Summary:

**Scenario 1**: Single guest, single ID, rooms checked in/out independently.
**Scenario 2**: Multiple guests, each with their own room and ID, rooms checked in/out independently.
**Scenario 3**: Multiple guests, some sharing rooms, rooms checked in/out independently, but charges are not duplicated.

This structure ensures that check-in and check-out are handled room-wise, providing flexibility and clarity for different booking scenarios.