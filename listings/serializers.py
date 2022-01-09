"""Serializer module form listings."""
from rest_framework import serializers

from listings.models import Listing


class ApartmentSerializer(serializers.ModelSerializer):
    """Apartment Serializer"""

    price = serializers.SerializerMethodField()

    class Meta:
        """Meta class for serializer."""

        model = Listing
        fields = (
            'country',
            'city',
            'title',
            'listing_type',
            'price',
        )

    @staticmethod
    def get_price(instance):
        """Fetch price from booking info."""
        return instance.booking_info.price


class HotelRoomSerializer(serializers.Serializer):
    """Hotel room serializer."""

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
    """Serializer for available units (rooms/apartments)."""

    max_price = serializers.DecimalField(required=True, min_value=1, max_digits=7, decimal_places=2)
    checkin = serializers.DateField(required=True)
    checkout = serializers.DateField(required=True)

    def validate(self, attrs):
        """Validate checkout"""
        attrs = super().validate(attrs)
        checkout = attrs.get('checkout')
        checkin = attrs.get('checkin')
        if checkout and checkin and checkout < checkin:
            raise serializers.ValidationError('Checkout must be greater then checkin.')
        return attrs
