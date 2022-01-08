"""Serializer module form listings."""
from rest_framework import serializers

from listings.models import Listing


class ApartmentSerializer(serializers.ModelSerializer):

    price = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = (
            'country',
            'city',
            'title',
            'listing_type',
            'price',
        )

    def get_price(self, instance):
        return instance.booking_info.price


class HotelRoomSerializer(serializers.Serializer):

    def to_representation(self, instance):
        pre_data = {
            'listing_type': instance.listing_type,
            'country': instance.country,
            'city': instance.city,
        }
        data = []
        for htype in instance.hotel_room_types.all():
            for room in htype.hotel_rooms.all():
                _info = {
                    'title': str(room),
                    'price': htype.booking_info.price,
                }
                _info.update(pre_data)
                data.append(_info)
        return data


class AvailableUnitsCriteriaSerialiser(serializers.Serializer):

    max_price = serializers.DecimalField(required=True, min_value=1, max_digits=7, decimal_places=2)
    checkin = serializers.DateField(required=True)
    checkout = serializers.DateField(required=True)
