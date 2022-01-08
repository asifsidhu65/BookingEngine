from django.db.models import Prefetch, Q, Count
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from listings.models import Listing, Reservation, HotelRoom
from listings.serializers import (
    AvailableUnitsCriteriaSerialiser, ApartmentSerializer, HotelRoomSerializer,
)


class FetchAvailableUnitsApiView(ListAPIView):
    """API view to check available units."""

    serializer_class = AvailableUnitsCriteriaSerialiser
    http_method_names = ["get"]

    def get_queryset(self):
        """Queryset."""
        checkin = self.request.GET.get("checkin")
        checkout = self.request.GET.get("checkout")
        max_price = self.request.GET["max_price"]
        reserved_rooms = Reservation.objects.filter(
            check_in__lte=checkout, check_out__gte=checkin
        ).values_list("room_id")
        hotel_rooms = HotelRoom.objects.exclude(id__in=reserved_rooms)
        return (
            Listing.objects.annotate(
                room_count=Count(
                    "hotel_room_types__hotel_rooms",
                    filter=Q(
                        hotel_room_types__hotel_rooms__in=HotelRoom.objects.exclude(
                            id__in=reserved_rooms
                        ).filter(hotel_room_type__booking_info__price__lt=max_price)
                    ),
                )
            )
            .filter(
                Q(booking_info__price__lte=max_price, listing_type=Listing.APARTMENT)
                | Q(
                    hotel_room_types__booking_info__price__lte=max_price,
                    room_count__gt=0,
                )
            )
            .select_related('booking_info')
            .prefetch_related(
                "hotel_room_types",
                Prefetch("hotel_room_types__hotel_rooms", queryset=hotel_rooms),
            )
            .distinct()
        )

    def get(self, request, *args, **kwargs):
        """"""
        data = {
            "checkin": request.GET.get("checkin"),
            "checkout": request.GET.get("checkout"),
            "max_price": request.GET.get("max_price"),
        }
        serializer = AvailableUnitsCriteriaSerialiser(data=data)
        serializer.is_valid(raise_exception=True)
        return super().get(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
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
