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
from datetime import datetime

from .models import Room, ServiceCategory, Service, Booking, RoomBooking, CheckIn, CheckOut, ServiceUsage, Billing, Payment, GuestDetails
from accounts.models import Tenant, User
from .serializers import RoomSerializer, ServiceCategorySerializer, ServiceSerializer, BookingSerializer, RoomBookingSerializer, CheckInSerializer, CheckOutSerializer, ServiceUsageSerializer, BillingSerializer, PaymentSerializer, UserSerializer, GuestUserSerializer, CheckInDetailSerializer
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
            serializer.save(tenant=user.tenant if not user.is_superuser else tenant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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

    def list(self, request):
        queryset = ServiceCategory.objects.all()
        serializer = ServiceCategorySerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = ServiceCategory.objects.all()
        service_category = get_object_or_404(queryset, pk=pk)
        serializer = ServiceCategorySerializer(service_category)
        return Response(serializer.data)

    def create(self, request):
        serializer = ServiceCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        queryset = ServiceCategory.objects.all()
        service_category = get_object_or_404(queryset, pk=pk)
        serializer = ServiceCategorySerializer(service_category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = ServiceCategory.objects.all()
        service_category = get_object_or_404(queryset, pk=pk)
        service_category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ServiceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Service.objects.all()
        serializer = ServiceSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Service.objects.all()
        service = get_object_or_404(queryset, pk=pk)
        serializer = ServiceSerializer(service)
        return Response(serializer.data)

    def create(self, request):
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        queryset = Service.objects.all()
        service = get_object_or_404(queryset, pk=pk)
        serializer = ServiceSerializer(service, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = Service.objects.all()
        service = get_object_or_404(queryset, pk=pk)
        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class BookingViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

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

        # Handle guest details
        phone = data.get('phone')
        email = data.get('email')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        address_line_1 = data.get('address_line_1', '')
        address_line_2 = data.get('address_line_2', '')
        dob = data.get('dob', None)
        address = f"{address_line_1} {address_line_2}".strip()

        guest_id = get_or_create_user(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='guest',
            phone=phone,
            address=address,
            password=data.get('password', 'guest'),
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
                status__in=[1, 2, 3],  # Pending, Confirmed, Checked-in
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
                        status=1,  # Set initial status to 'Pending'
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
        # queryset = Booking.objects.all()
        user = request.user
        queryset = Booking.objects.filter(tenant=user.tenant)  # Filter by current tenant
        serializer = BookingSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        # queryset = Booking.objects.all()
        user = request.user
        queryset = Booking.objects.filter(tenant=user.tenant)
        booking = get_object_or_404(queryset, pk=pk)
        serializer = BookingSerializer(booking)
        return Response(serializer.data)

    def update(self, request, pk=None):
        # queryset = Booking.objects.all()
        user = request.user
        queryset = Booking.objects.filter(tenant=user.tenant)
        booking = get_object_or_404(queryset, pk=pk)
        old_status = booking.status
        new_status = request.data.get('status', old_status)

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

            # Handle status change to Cancelled
            if old_status != 3 and new_status == 3:
                RoomBooking.objects.filter(booking=booking).update(is_active=False)

            # Handle status change from Cancelled to Confirmed
            if old_status == 3 and new_status == 2:
                rooms_data = RoomBooking.objects.filter(booking=booking)
                for room_booking in rooms_data:
                    room_id = room_booking.room_id
                    start_date = room_booking.start_date
                    end_date = room_booking.end_date

                    overlapping_bookings = RoomBooking.objects.filter(
                        room_id=room_id,
                        start_date__lt=end_date,
                        end_date__gt=start_date,
                        status__in=[1, 2, 3],  # Pending, Confirmed, Checked-in
                        is_active=True
                    ).exclude(booking=booking)

                    if overlapping_bookings.exists():
                        return Response(
                            {"error": f"Room {room_id} is not available from {start_date} to {end_date}"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    room_booking.is_active = True
                    room_booking.status = 2  # Set status to 'Confirmed'
                    room_booking.save()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        # queryset = Booking.objects.all()
        user = request.user
        queryset = Booking.objects.filter(tenant=user.tenant)
        booking = get_object_or_404(queryset, pk=pk)
        old_status = booking.status
        new_status = request.data.get('status', old_status)

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

            # Handle status change to Cancelled
            if old_status != 3 and new_status == 3:
                RoomBooking.objects.filter(booking=booking).update(is_active=False)

            # Handle status change from Cancelled to Confirmed
            if old_status == 3 and new_status == 2:
                rooms_data = RoomBooking.objects.filter(booking=booking)
                for room_booking in rooms_data:
                    room_id = room_booking.room_id
                    start_date = room_booking.start_date
                    end_date = room_booking.end_date

                    overlapping_bookings = RoomBooking.objects.filter(
                        room_id=room_id,
                        start_date__lt=end_date,
                        end_date__gt=start_date,
                        status__in=[1, 2, 3],  # Pending, Confirmed, Checked-in
                        is_active=True
                    ).exclude(booking=booking)

                    if overlapping_bookings.exists():
                        return Response(
                            {"error": f"Room {room_id} is not available from {start_date} to {end_date}"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    room_booking.is_active = True
                    room_booking.status = 2  # Set status to 'Confirmed'
                    room_booking.save()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        # queryset = Booking.objects.all()
        user = request.user
        queryset = Booking.objects.filter(tenant=user.tenant)
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
            check_in_date = datetime.fromisoformat(check_in_date_str)

            room_booking = get_object_or_404(RoomBooking, booking_id=booking_id, room_id=room_id)

            if not (room_booking.start_date <= check_in_date <= room_booking.end_date):
                raise ValidationError("Check-in date must be within the booking period.")

            if room_booking.status != 1:  # Ensure the room is in 'Pending' status
                raise ValidationError("Room is not available for check-in.")

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
                    address=f"{guest['address_line_1']} {guest['address_line_2']}".strip(),
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
                room_booking.status = 3  # Set status to 'Checked-in'
                room_booking.save()

                # Add guests to the response
                response_data = serializer.data
                response_data['guests'] = [GuestUserSerializer(User.objects.get(id=guest_id)).data for guest_id in guest_ids]

                return Response(response_data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        # queryset = CheckIn.objects.all()
        user = request.user
        queryset = CheckIn.objects.filter(tenant=user.tenant)
        serializer = CheckInSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        # queryset = CheckIn.objects.all()
        user = request.user
        queryset = CheckIn.objects.filter(tenant=user.tenant)
        check_in = get_object_or_404(queryset, pk=pk)
        serializer = CheckInSerializer(check_in)
        return Response(serializer.data)

    def update(self, request, pk=None):
        # queryset = CheckIn.objects.all()
        user = request.user
        queryset = CheckIn.objects.filter(tenant=user.tenant)
        check_in = get_object_or_404(queryset, pk=pk)
        serializer = CheckInSerializer(check_in, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        # queryset = CheckIn.objects.all()
        user = request.user
        queryset = CheckIn.objects.filter(tenant=user.tenant)
        check_in = get_object_or_404(queryset, pk=pk)
        check_in.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CheckOutViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # queryset = CheckOut.objects.all()
        user = request.user
        queryset = CheckOut.objects.filter(tenant=user.tenant)
        serializer = CheckOutSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        # queryset = CheckOut.objects.all()
        user = request.user
        queryset = CheckOut.objects.filter(tenant=user.tenant)
        check_out = get_object_or_404(queryset, pk=pk)
        serializer = CheckOutSerializer(check_out)
        return Response(serializer.data)

    def create(self, request):
        try:
            booking_id = request.data.get('booking_id')
            room_id = request.data.get('room_id')
            check_out_date_str = request.data.get('check_out_date', timezone.now().isoformat())

            # Parse the check_out_date string to a datetime object
            check_out_date = datetime.fromisoformat(check_out_date_str)

            logger.debug(f"Attempting to check out for booking_id: {booking_id}, room_id: {room_id} at {check_out_date}")

            room_booking = get_object_or_404(RoomBooking, booking_id=booking_id, room_id=room_id)
            logger.debug(f"Room booking start date: {room_booking.start_date}, end date: {room_booking.end_date}")

            if not (room_booking.start_date <= check_out_date <= room_booking.end_date):
                logger.error("Check-out date is not within the booking period.")
                raise ValidationError("Check-out date must be within the booking period.")

            if room_booking.status != 3:  # Ensure the room is in 'Checked-in' status
                logger.error("Room is not available for check-out.")
                raise ValidationError("Room is not available for check-out.")

            request.data['checked_out_by'] = request.user.id
            request.data['room_booking'] = room_booking.id
            serializer = CheckOutSerializer(data=request.data)
            if serializer.is_valid():
                check_out = serializer.save()
                room_booking.status = 4  # Set status to 'Checked-out'
                room_booking.save()
                logger.info(f"Check-out successful for room_booking_id: {room_booking.id}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            logger.error(f"Check-out failed: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("An error occurred during check-out.")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None):
        # queryset = CheckOut.objects.all()
        user = request.user
        queryset = CheckOut.objects.filter(tenant=user.tenant)
        check_out = get_object_or_404(queryset, pk=pk)
        serializer = CheckOutSerializer(check_out, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        # queryset = CheckOut.objects.all()
        user = request.user
        queryset = CheckOut.objects.filter(tenant=user.tenant)
        check_out = get_object_or_404(queryset, pk=pk)
        check_out.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ServiceUsageViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = ServiceUsage.objects.all()
        serializer = ServiceUsageSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = ServiceUsage.objects.all()
        service_usage = get_object_or_404(queryset, pk=pk)
        serializer = ServiceUsageSerializer(service_usage)
        return Response(serializer.data)

    def create(self, request):
        serializer = ServiceUsageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        queryset = ServiceUsage.objects.all()
        service_usage = get_object_or_404(queryset, pk=pk)
        serializer = ServiceUsageSerializer(service_usage, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = ServiceUsage.objects.all()
        service_usage = get_object_or_404(queryset, pk=pk)
        service_usage.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class BillingViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Billing.objects.all()
        serializer = BillingSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Billing.objects.all()
        billing = get_object_or_404(queryset, pk=pk)
        serializer = BillingSerializer(billing)
        return Response(serializer.data)

    def create(self, request):
        serializer = BillingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        queryset = Billing.objects.all()
        billing = get_object_or_404(queryset, pk=pk)
        serializer = BillingSerializer(billing, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = Billing.objects.all()
        billing = get_object_or_404(queryset, pk=pk)
        billing.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PaymentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Payment.objects.all()
        serializer = PaymentSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Payment.objects.all()
        payment = get_object_or_404(queryset, pk=pk)
        serializer = PaymentSerializer(payment)
        return Response(serializer.data)

    def create(self, request):
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        queryset = Payment.objects.all()
        payment = get_object_or_404(queryset, pk=pk)
        serializer = PaymentSerializer(payment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = Payment.objects.all()
        payment = get_object_or_404(queryset, pk=pk)
        payment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)