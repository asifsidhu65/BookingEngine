"""Module for Listings app views."""
from django.db.models import Prefetch, Q, Count
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from listings.models import Listing, Reservation, HotelRoom
from listings.serializers import (
    AvailableUnitsCriteriaSerialiser,
    ApartmentSerializer,
    HotelRoomSerializer,
)


class FetchAvailableUnitsApiView(ListAPIView):
    """API view to check available units."""

    serializer_class = AvailableUnitsCriteriaSerialiser
    http_method_names = ["get"]
    query_data = {}

    def get_queryset(self):
        """Queryset."""
        checkin = self.query_data["checkin"]
        checkout = self.query_data["checkout"]
        max_price = self.query_data["max_price"]
        reserved_rooms = Reservation.objects.filter(
            check_in__lte=checkout,
            check_out__gte=checkin,
            listing__listing_type=Listing.HOTEL,
        ).values_list("room_id", flat=True)
        reserved_apartments = Reservation.objects.filter(
            check_in__lte=checkout,
            check_out__gte=checkin,
            listing__listing_type=Listing.APARTMENT,
        ).values_list("listing_id", flat=True)
        hotel_rooms = HotelRoom.objects.exclude(id__in=reserved_rooms)
        return (
            Listing.objects.annotate(
                room_count=Count(
                    "hotel_room_types__hotel_rooms",
                    filter=Q(
                        hotel_room_types__hotel_rooms__in=hotel_rooms.filter(
                            hotel_room_type__booking_info__price__lte=max_price
                        )
                    ),
                )
            )
            .exclude(id__in=reserved_apartments)
            .filter(
                Q(booking_info__price__lte=max_price, listing_type=Listing.APARTMENT)
                | Q(
                    hotel_room_types__booking_info__price__lte=max_price,
                    room_count__gt=0,
                )
            )
            .select_related("booking_info")
            .prefetch_related(
                "hotel_room_types",
                Prefetch(
                    "hotel_room_types__hotel_rooms",
                    queryset=hotel_rooms.filter(
                        hotel_room_type__booking_info__price__lte=max_price
                    ),
                ),
            )
            .distinct()
        )

    def get(self, request, *args, **kwargs):
        """Handle GET type request."""
        data = {
            "checkin": request.GET.get("checkin"),
            "checkout": request.GET.get("checkout"),
            "max_price": request.GET.get("max_price"),
        }
        serializer = self.get_serializer_class()(data=data)
        serializer.is_valid(raise_exception=True)
        self.query_data = serializer.validated_data
        return super().get(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """Handle units listing response."""
        queryset = self.filter_queryset(self.get_queryset())
        data = []
        for instance in queryset:
            if instance.listing_type == instance.APARTMENT:
                data.append(ApartmentSerializer(instance=instance).data)
            else:
                data.extend(HotelRoomSerializer(instance=[instance], many=True).data[0])
        from django.db import connection

        print(len(connection.queries))
        return Response(data)
