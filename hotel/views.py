import logging
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.utils import timezone
import json
from datetime import datetime, date
from rest_framework.views import APIView
from decimal import Decimal
# from dateutil.parser import parse as parse_date

from .models import Room, ServiceCategory, Service, Booking, RoomBooking, CheckIn, CheckOut, ServiceUsage, GuestDetails
from order.models import Order
from accounts.models import Tenant, User
from .serializers import RoomSerializer, ServiceCategorySerializer, ServiceSerializer, BookingSerializer, RoomBookingSerializer, CheckInSerializer, CheckOutSerializer, ServiceUsageSerializer, UserSerializer, GuestUserSerializer, CheckInDetailSerializer
from utils.image_upload import handle_image_upload
from utils.get_or_create_user import get_or_create_user

logger = logging.getLogger(__name__)

class RoomViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Room.objects.all()
        return Room.objects.filter(tenant=user.tenant)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = RoomSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        room = get_object_or_404(queryset, pk=pk)
        serializer = RoomSerializer(room)
        return Response(serializer.data)

    def create(self, request):
        user = self.request.user
        tenant_name = user.tenant.tenant_name if not user.is_superuser else None

        if user.is_superuser:
            tenant_id = request.data.get('tenant')
            if not tenant_id:
                raise PermissionDenied("Superuser must include tenant ID in request.")
            tenant = get_object_or_404(Tenant, id=tenant_id)
            tenant_name = tenant.tenant_name

        # Handle image file upload
        image_urls = handle_image_upload(request, tenant_name, 'room', 'image')
        if image_urls:
            request.data._mutable = True  # Make request data mutable
            request.data['image'] = json.dumps(image_urls)  # Convert list to JSON string
            request.data._mutable = False  # Make request data immutable
            logger.debug(f'Image URLs added to request data: {request.data["image"]}')
        else:
            logger.debug('No image URLs returned from handle_image_upload.')

        serializer = RoomSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(tenant=user.tenant if not user.is_superuser else tenant)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                room_number = request.data.get('room_number')
                return Response(
                    {"error": f"Room number {room_number} already exists for this tenant."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        user = self.request.user
        if not user.is_superuser:
            raise PermissionDenied("You do not have permission to perform this action.")

        queryset = self.get_queryset()
        room = get_object_or_404(queryset, pk=pk)
        tenant_name = user.tenant.tenant_name if not user.is_superuser else room.tenant.tenant_name

        # Handle image file upload
        image_urls = handle_image_upload(request, tenant_name, 'room', 'image')
        if image_urls:
            request.data._mutable = True  # Make request data mutable
            request.data['image'] = json.dumps(image_urls)  # Convert list to JSON string
            request.data._mutable = False  # Make request data immutable
            logger.debug(f'Image URLs added to request data: {request.data["image"]}')
        else:
            logger.debug('No image URLs returned from handle_image_upload.')

        serializer = RoomSerializer(room, data=request.data, partial=True)
        if serializer.is_valid():
            tenant_id = request.data.get('tenant')
            if tenant_id:
                tenant = get_object_or_404(Tenant, id=tenant_id)
                serializer.save(tenant=tenant)
            else:
                serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        user = self.request.user
        if not user.is_superuser:
            raise PermissionDenied("You do not have permission to perform this action.")

        queryset = self.get_queryset()
        room = get_object_or_404(queryset, pk=pk)
        room_number = room.room_number
        room.delete()
        return Response({"message": f"Room - {room_number} deleted"}, status=status.HTTP_204_NO_CONTENT)

class ServiceCategoryViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            queryset = ServiceCategory.objects.all()
        else:
            queryset = ServiceCategory.objects.filter(tenant=user.tenant)
        
        logger.debug(f"ServiceCategory queryset for user {user.id}: {queryset}")
        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        serializer = ServiceCategorySerializer(queryset, many=True)
        logger.debug(f"Serialized ServiceCategory data: {serializer.data}")
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        service_category = get_object_or_404(queryset, pk=pk)
        serializer = ServiceCategorySerializer(service_category)
        return Response(serializer.data)

    def create(self, request):
        user = request.user
        serializer = ServiceCategorySerializer(data=request.data)
        if serializer.is_valid():
            if not user.is_superuser:
                serializer.save(tenant=user.tenant)
            else:
                serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        queryset = self.get_queryset()
        service_category = get_object_or_404(queryset, pk=pk)
        serializer = ServiceCategorySerializer(service_category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = self.get_queryset()
        service_category = get_object_or_404(queryset, pk=pk)
        service_category_name = service_category.name
        service_category_id = service_category.id
        service_category.delete()
        return Response(
            {"message": f"ServiceCategory '{service_category_name}' with ID {service_category_id} deleted"},
            status=status.HTTP_204_NO_CONTENT
        )

    def partial_update(self, request, pk=None):
        queryset = self.get_queryset()
        service_category = get_object_or_404(queryset, pk=pk)
        serializer = ServiceCategorySerializer(service_category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServiceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            queryset = Service.objects.all()
        else:
            queryset = Service.objects.filter(tenant=user.tenant)
        
        logger.debug(f"Service queryset for user {user.id}: {queryset}")
        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        serializer = ServiceSerializer(queryset, many=True)
        logger.debug(f"Serialized Service data: {serializer.data}")
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        service = get_object_or_404(queryset, pk=pk)
        serializer = ServiceSerializer(service)
        return Response(serializer.data)

    def create(self, request):
        user = request.user
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            if not user.is_superuser:
                serializer.save(tenant=user.tenant)
            else:
                serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        queryset = self.get_queryset()
        service = get_object_or_404(queryset, pk=pk)
        serializer = ServiceSerializer(service, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = self.get_queryset()
        service = get_object_or_404(queryset, pk=pk)
        service_name = service.name
        service_id = service.id
        service.delete()
        return Response(
            {"message": f"Service '{service_name}' with ID {service_id} deleted"},
            status=status.HTTP_204_NO_CONTENT
        )

    def partial_update(self, request, pk=None):
        queryset = self.get_queryset()
        service = get_object_or_404(queryset, pk=pk)
        serializer = ServiceSerializer(service, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookingViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Booking.objects.all()
        return Booking.objects.filter(tenant=user.tenant)

    def create(self, request):
        user = request.user
        tenant = user.tenant

        # Check if the request is a form submission
        if request.content_type.startswith('multipart/form-data'):
            data = request.data.dict()  # Convert QueryDict to a regular dict
            rooms_data = json.loads(data.get('rooms', '[]'))  # Parse rooms data from JSON string
        else:
            data = request.data
            rooms_data = data.get('rooms', [])

        # Verify that all room IDs exist and belong to the current tenant
        room_ids = [room_data.get('room') for room_data in rooms_data]
        existing_room_ids = set(
            Room.objects.filter(id__in=room_ids, tenant=user.tenant).values_list('id', flat=True)
        )
        non_existent_rooms = [room_id for room_id in room_ids if room_id not in existing_room_ids]

        if non_existent_rooms:
            return Response(
                {"error": f"Room(s) with ID(s) {non_existent_rooms} does not exist."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate room dates
        invalid_dates = []
        for room_data in rooms_data:
            start_date = room_data.get('start_date')
            end_date = room_data.get('end_date')
            if start_date and end_date and start_date >= end_date:
                invalid_dates.append({
                    "room_id": room_data.get('room'),
                    "start_date": start_date,
                    "end_date": end_date
                })

        if invalid_dates:
            return Response(
                {"error": "End date must be greater than start date for the following rooms", "details": invalid_dates},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Handle guest details
        phone = data.get('phone')
        email = data.get('email')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        address_line_1 = data.get('address_line_1', '')
        address_line_2 = data.get('address_line_2', '')
        dob = data.get('dob', None)

        guest_id = get_or_create_user(
            username=phone or email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='guest',
            phone=phone,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            password=data.get(dob, 'default_password'),
            tenant=tenant
        )

        # Handle ID card image upload
        id_card_urls = handle_image_upload(request, tenant.tenant_name, 'hotel/id_card', 'id_card')
        if id_card_urls:
            data['id_card'] = id_card_urls
        else:
            data['id_card'] = None

        # Prepare booking data
        data['tenant'] = tenant.id
        data['guests'] = [guest_id]
        data['total_amount'] = data.get('total_amount', 0.0)
        data['advance_paid'] = data.get('advance_paid', 0.0)

        # Check room availability
        unavailable_rooms = []
        for room_data in rooms_data:
            room_id = room_data.get('room')
            start_date = room_data.get('start_date')
            end_date = room_data.get('end_date')

            overlapping_bookings = RoomBooking.objects.filter(
                room_id=room_id,
                start_date__lt=end_date,
                end_date__gt=start_date,
                booking__status__in=['pending', 'confirmed', 'checked_in'],
                is_active=True
            )

            if overlapping_bookings.exists():
                unavailable_rooms.append({
                    "room_id": room_id,
                    "start_date": start_date,
                    "end_date": end_date
                })

        if unavailable_rooms:
            return Response(
                {"error": "Some rooms are not available", "details": unavailable_rooms},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the booking
        serializer = BookingSerializer(data=data)
        if serializer.is_valid():
            try:
                booking = serializer.save()

                # Allocate rooms
                for room_data in rooms_data:
                    room_id = room_data.get('room')
                    start_date = room_data.get('start_date')
                    end_date = room_data.get('end_date')

                    room_booking = RoomBooking(
                        booking=booking,
                        room_id=room_id,
                        start_date=start_date,
                        end_date=end_date,
                        is_active=True
                    )
                    room_booking.save()

                # Fetch the detailed guest and room information for the response
                booking_data = BookingSerializer(booking).data
                booking_data['guests'] = [UserSerializer(User.objects.get(id=guest_id)).data]
                booking_data['rooms'] = RoomBookingSerializer(RoomBooking.objects.filter(booking=booking), many=True).data

                return Response(booking_data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                logger.error(f"IntegrityError: {e}")
                return Response({"error": "Integrity error occurred", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.error(f"Validation error: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = BookingSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        booking = get_object_or_404(queryset, pk=pk)
        serializer = BookingSerializer(booking)
        return Response(serializer.data)

    def update(self, request, pk=None):
        queryset = self.get_queryset()
        booking = get_object_or_404(queryset, pk=pk)
        old_status = booking.status
        new_status = request.data.get('status', old_status)

        # Prevent status from being set to 'checked_in' or 'checked_out'
        if new_status in ['checked_in', 'checked_out']:
            return Response(
                {"error": "Status cannot be updated to Checked-in or Checked-out directly."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.dict()  # Convert QueryDict to a regular dict

        # Handle ID card image upload
        tenant = booking.tenant
        id_card_urls = handle_image_upload(request, tenant.tenant_name, 'hotel/id_card', 'id_card')
        if id_card_urls:
            data['id_card'] = id_card_urls  # Store as list of URLs
        else:
            data['id_card'] = booking.id_card  # Keep existing value if no new files are uploaded

        serializer = BookingSerializer(booking, data=data, partial=True)
        if serializer.is_valid():
            booking = serializer.save()

            # Update is_active based on status
            if new_status in ['cancelled', 'completed', 'no_show']:
                RoomBooking.objects.filter(booking=booking).update(is_active=False)
            elif new_status in ['pending', 'confirmed', 'checked_in', 'checked_out']:
                RoomBooking.objects.filter(booking=booking).update(is_active=True)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        queryset = self.get_queryset()
        booking = get_object_or_404(queryset, pk=pk)
        old_status = booking.status
        new_status = request.data.get('status', old_status)

        # Prevent status from being set to 'checked_in' or 'checked_out'
        if new_status in ['checked_in', 'checked_out']:
            return Response(
                {"error": "Status cannot be updated to Checked-in or Checked-out directly."},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.dict()  # Convert QueryDict to a regular dict

        # Handle ID card image upload
        tenant = booking.tenant
        id_card_urls = handle_image_upload(request, tenant.tenant_name, 'hotel/id_card', 'id_card')
        if id_card_urls:
            data['id_card'] = id_card_urls  # Store as list of URLs
        else:
            data['id_card'] = booking.id_card  # Keep existing value if no new files are uploaded

        serializer = BookingSerializer(booking, data=data, partial=True)
        if serializer.is_valid():
            booking = serializer.save()

            # Update is_active based on status
            if new_status in ['cancelled', 'completed', 'no_show']:
                RoomBooking.objects.filter(booking=booking).update(is_active=False)
            elif new_status in ['pending', 'confirmed', 'checked_in', 'checked_out']:
                RoomBooking.objects.filter(booking=booking).update(is_active=True)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = self.get_queryset()
        booking = get_object_or_404(queryset, pk=pk)
        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RoomBookingViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = RoomBooking.objects.all()
        serializer = RoomBookingSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = RoomBooking.objects.all()
        room_booking = get_object_or_404(queryset, pk=pk)
        serializer = RoomBookingSerializer(room_booking)
        return Response(serializer.data)

    def create(self, request):
        serializer = RoomBookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        queryset = RoomBooking.objects.all()
        room_booking = get_object_or_404(queryset, pk=pk)
        serializer = RoomBookingSerializer(room_booking, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = RoomBooking.objects.all()
        room_booking = get_object_or_404(queryset, pk=pk)
        room_booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CheckInViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return CheckIn.objects.all()
        return CheckIn.objects.filter(room_booking__booking__tenant=user.tenant)

    def create(self, request):
        try:
            # Check if the request is JSON or form-data
            if request.content_type == 'application/json':
                data = request.data
            else:
                # Convert QueryDict to a regular dict
                data = request.POST.dict()
                # Manually combine nested fields into a single JSON string
                guests = []
                i = 0
                while True:
                    guest = {
                        'email': request.POST.get(f'guests[{i}][email]'),
                        'first_name': request.POST.get(f'guests[{i}][first_name]'),
                        'last_name': request.POST.get(f'guests[{i}][last_name]'),
                        'phone': request.POST.get(f'guests[{i}][phone]'),
                        'address_line_1': request.POST.get(f'guests[{i}][address_line_1]'),
                        'address_line_2': request.POST.get(f'guests[{i}][address_line_2]'),
                        'dob': request.POST.get(f'guests[{i}][dob]'),
                        'coming_from': request.POST.get(f'guests[{i}][coming_from]'),
                        'going_to': request.POST.get(f'guests[{i}][going_to]'),
                        'purpose': request.POST.get(f'guests[{i}][purpose]'),
                        'foreigner': request.POST.get(f'guests[{i}][foreigner]') == 'true',  # Convert to boolean
                        'c_form': request.POST.get(f'guests[{i}][c_form]')
                    }
                    if any(guest.values()):  # Ensure at least one field is not None
                        guests.append(guest)
                        i += 1
                    else:
                        break

                if not guests:
                    return Response({"error": "Guests data is missing"}, status=status.HTTP_400_BAD_REQUEST)

                data['guests'] = guests

            booking_id = data.get('booking_id')
            room_id = data.get('room_id')
            check_in_date_str = data.get('check_in_date', timezone.now().isoformat())
            guests = data.get('guests', [])

            if not guests:
                return Response({"error": "Guests data is missing"}, status=status.HTTP_400_BAD_REQUEST)

            # Parse the check_in_date string to a datetime object
            check_in_date_str = data.get('check_in_date', timezone.now().isoformat())
            try:
                # Attempt to parse as datetime first
                check_in_date = datetime.fromisoformat(check_in_date_str.replace('Z', '+00:00'))
            except ValueError:
                # Fallback to parsing as date if datetime parsing fails
                check_in_date = datetime.strptime(check_in_date_str, '%Y-%m-%d').date()

            # Ensure check_in_date is a datetime object
            if isinstance(check_in_date, date) and not isinstance(check_in_date, datetime):
                check_in_date = datetime.combine(check_in_date, datetime.min.time())

            room_booking = get_object_or_404(RoomBooking, booking_id=booking_id, room_id=room_id)

            if not (room_booking.start_date <= check_in_date <= room_booking.end_date):
                raise ValidationError("Check-in date must be within the booking period.")

            # Check the status of the associated booking
            if room_booking.booking.status not in ['pending', 'confirmed', 'partial_checked_in', 'partial_checked_in_out', 'partial_checked_out']:
                return Response(
                    {"error": f"Cannot check-in. Booking status is {room_booking.booking.get_status_display()}."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Add validation to check if the room is already checked in
            existing_check_in = CheckIn.objects.filter(room_booking=room_booking).first()
            if existing_check_in:
                logger.error(f"Room {room_id} is already checked in.")
                return Response({"error": f"Room {room_id} is already checked in for booking {booking_id}."}, status=status.HTTP_400_BAD_REQUEST)

            # Create users for guests and their details
            guest_ids = []
            for i, guest in enumerate(guests):
                guest_id = get_or_create_user(
                    username=guest['phone'] or guest['email'],
                    email=guest['email'],
                    first_name=guest['first_name'],
                    last_name=guest['last_name'],
                    role='guest',
                    phone=guest['phone'],
                    address_line_1=guest['address_line_1'],
                    address_line_2=guest['address_line_2'],
                    password=guest['dob'] or 'guest',  # Default password, can be changed later
                    tenant=request.user.tenant
                )
                guest_ids.append(guest_id)

                # Create or update GuestDetails
                guest_user = User.objects.get(id=guest_id)
                guest_details, created = GuestDetails.objects.update_or_create(
                    user=guest_user,
                    defaults={
                        'coming_from': guest.get('coming_from', ''),
                        'going_to': guest.get('going_to', ''),
                        'purpose': guest.get('purpose', ''),
                        'foreigner': guest.get('foreigner', False)  # Ensure boolean value
                    }
                )

                # Handle file upload for each guest
                file_key = f'guests[{i}][id_card]'
                if file_key in request.FILES:
                    guest['id_card'] = request.FILES[file_key]

                # Handle guest_id image upload
                guest_id_file_key = f'guests[{i}][guest_id]'
                if guest_id_file_key in request.FILES:
                    guest_id_urls = handle_image_upload(request, request.user.tenant.tenant_name, 'hotel/guest_id', guest_id_file_key)
                    guest_details.guest_id = guest_id_urls
                else:
                    guest_details.guest_id = []  # Ensure guest_id is an empty list if no image is uploaded

                # Handle c_form field
                c_form_file_key = f'guests[{i}][c_form]'
                if c_form_file_key in request.FILES:
                    c_form_urls = handle_image_upload(request, request.user.tenant.tenant_name, 'hotel/c_form', c_form_file_key)
                    guest_details.c_form = c_form_urls
                elif 'c_form' in guest and isinstance(guest['c_form'], str):
                    guest_details.c_form = guest['c_form']
                else:
                    guest_details.c_form = None

                guest_details.save()

            # Create a mutable copy of request.data
            mutable_data = request.data.copy()
            mutable_data['checked_in_by'] = request.user.id
            mutable_data['room_booking'] = room_booking.id

            serializer = CheckInSerializer(data=mutable_data)
            if serializer.is_valid():
                check_in = serializer.save()
                check_in.guests.set(guest_ids)  # Associate guests with the check-in

                # Check the status of all room bookings for this booking
                all_room_bookings = RoomBooking.objects.filter(booking=room_booking.booking)
                all_checked_in = all(
                    CheckIn.objects.filter(room_booking=rb).exists() for rb in all_room_bookings
                )
                any_checked_in = any(
                    CheckIn.objects.filter(room_booking=rb).exists() for rb in all_room_bookings
                )
                any_checked_out = any(
                    CheckOut.objects.filter(room_booking=rb).exists() for rb in all_room_bookings
                )
                all_checked_out = all(
                    CheckOut.objects.filter(room_booking=rb).exists() for rb in all_room_bookings
                )

                # Update booking status based on room check-in status
                if all_checked_in and not any_checked_out:
                    room_booking.booking.status = 'checked_in'
                elif any_checked_in and not all_checked_in and not any_checked_out:
                    room_booking.booking.status = 'partial_checked_in'
                elif all_checked_in and any_checked_out and not all_checked_out:
                    room_booking.booking.status = 'partial_checked_out'
                elif any_checked_in and any_checked_out:
                    room_booking.booking.status = 'partial_checked_in_out'
                else:
                    raise ValidationError("Unexpected booking status. Please check the room statuses.")

                room_booking.booking.save()

                # Add guests to the response
                response_data = serializer.data
                response_data['guests'] = [GuestUserSerializer(User.objects.get(id=guest_id)).data for guest_id in guest_ids]

                return Response(response_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("An error occurred during check-in.")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = CheckInSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        check_in = get_object_or_404(queryset, pk=pk)
        serializer = CheckInSerializer(check_in)
        return Response(serializer.data)

    def update(self, request, pk=None):
        queryset = self.get_queryset()
        check_in = get_object_or_404(queryset, pk=pk)
        serializer = CheckInSerializer(check_in, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = self.get_queryset()
        check_in = get_object_or_404(queryset, pk=pk)
        check_in.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CheckOutViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return CheckOut.objects.all()
        return CheckOut.objects.filter(tenant=user.tenant)

    def create(self, request):
        try:
            booking_id = request.data.get('booking_id')
            room_id = request.data.get('room_id')
            check_out_date_str = request.data.get('check_out_date', timezone.now().isoformat())

            # Parse the check_out_date string to a datetime object
            try:
                check_out_date = datetime.fromisoformat(check_out_date_str.replace('Z', '+00:00'))
            except ValueError:
                check_out_date = datetime.strptime(check_out_date_str, '%Y-%m-%d').date()

            # Ensure check_out_date is a datetime object
            if isinstance(check_out_date, date) and not isinstance(check_out_date, datetime):
                check_out_date = datetime.combine(check_out_date, datetime.min.time())

            logger.debug(f"Attempting to check out for booking_id: {booking_id}, room_id: {room_id} at {check_out_date}")

            booking = get_object_or_404(Booking, id=booking_id)
            room_booking = get_object_or_404(RoomBooking, booking_id=booking_id, room_id=room_id)
            logger.debug(f"Room booking start date: {room_booking.start_date}, end date: {room_booking.end_date}")

            if not (room_booking.start_date <= check_out_date <= room_booking.end_date):
                logger.error("Check-out date is not within the booking period.")
                raise ValidationError("Check-out date must be within the booking period.")

            # Ensure the room is checked in
            check_in = CheckIn.objects.filter(room_booking=room_booking).first()
            if not check_in:
                logger.error("Room is not checked in.")
                raise ValidationError("Room is not checked in.")

            # Ensure the room is not already checked out
            if CheckOut.objects.filter(room_booking=room_booking).exists():
                logger.error("Room is already checked out.")
                raise ValidationError("Room is already checked out.")

            request.data['checked_out_by'] = request.user.id
            request.data['room_booking'] = room_booking.id
            serializer = CheckOutSerializer(data=request.data)
            if serializer.is_valid():
                check_out = serializer.save()
                room_booking.is_active = False  # Set is_active to False
                room_booking.save()

                # Check the status of all room bookings for this booking
                all_room_bookings = RoomBooking.objects.filter(booking=booking)
                all_checked_in = all(
                    CheckIn.objects.filter(room_booking=rb).exists() for rb in all_room_bookings
                )
                all_checked_out = all(
                    CheckOut.objects.filter(room_booking=rb).exists() for rb in all_room_bookings
                )
                any_checked_in = any(
                    CheckIn.objects.filter(room_booking=rb).exists() for rb in all_room_bookings
                )
                any_checked_out = any(
                    CheckOut.objects.filter(room_booking=rb).exists() for rb in all_room_bookings
                )

                # Update booking status based on room check-out status
                if all_checked_out:
                    booking.status = 'checked_out'
                elif all_checked_in and not all_checked_out:
                    booking.status = 'partial_checked_out'
                elif any_checked_in and any_checked_out:
                    booking.status = 'partial_checked_in_out'
                else:
                    raise ValidationError("Unexpected booking status. Please check the room statuses.")

                booking.save()

                logger.info(f"Check-out successful for room_booking_id: {room_booking.id}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            logger.error(f"Check-out failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.exception("Validation error during check-out.")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("An error occurred during check-out.")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = CheckOutSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        check_out = get_object_or_404(queryset, pk=pk)
        serializer = CheckOutSerializer(check_out)
        return Response(serializer.data)

    def update(self, request, pk=None):
        queryset = self.get_queryset()
        check_out = get_object_or_404(queryset, pk=pk)
        serializer = CheckOutSerializer(check_out, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = self.get_queryset()
        check_out = get_object_or_404(queryset, pk=pk)
        check_out.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ServiceUsageViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return ServiceUsage.objects.all()
        # Filter ServiceUsage by the tenant of the booking
        return ServiceUsage.objects.filter(room_id__booking__tenant=user.tenant)

    def list(self, request):
        queryset = self.get_queryset()
        serializer = ServiceUsageSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        service_usage = get_object_or_404(queryset, pk=pk)
        serializer = ServiceUsageSerializer(service_usage)
        return Response(serializer.data)

    def create(self, request):
        service_id = request.data.get('service_id')
        service = get_object_or_404(Service, id=service_id)

        if not service.status:
            return Response(
                {"error": f"Cannot add disabled service: {service.name} with ID {service_id}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get room_id and booking_id from the request data
        room_id = request.data.get('room_id')
        booking_id = request.data.get('booking_id')

        # Find the corresponding RoomBooking instance
        room_booking = get_object_or_404(RoomBooking, room_id=room_id, booking_id=booking_id)

        # Validate room's check-in and check-out status
        check_in_details = CheckIn.objects.filter(room_booking=room_booking).first()
        check_out_date = CheckOut.objects.filter(room_booking=room_booking).first()

        if not check_in_details or check_out_date:
            return Response(
                {"error": "Service usage can only be added if the room is checked in and not checked out."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Prepare data for ServiceUsage creation
        service_usage_data = {
            'booking_id': booking_id,
            'room_id': room_booking.id,  # Use RoomBooking ID for the ServiceUsage
            'service_id': service_id,
            'usage_date': timezone.now()
        }

        serializer = ServiceUsageSerializer(data=service_usage_data)
        if serializer.is_valid():
            service_usage = serializer.save()
            response_data = serializer.data
            response_data['room_id'] = room_id  # Return the original room_id in the response
            # response_data['room_booking_id'] = room_booking.id  # Include RoomBooking ID in the response
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        queryset = self.get_queryset()
        service_usage = get_object_or_404(queryset, pk=pk)
        serializer = ServiceUsageSerializer(service_usage, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = self.get_queryset()
        service_usage = get_object_or_404(queryset, pk=pk)
        service_usage.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)





