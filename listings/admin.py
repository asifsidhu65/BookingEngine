from django.contrib import admin

from .forms import AdminReservationFrom
from .models import Listing, HotelRoomType, HotelRoom, BookingInfo, Reservation


class HotelRoomTypeInline(admin.StackedInline):
    model = HotelRoomType
    extra = 1
    show_change_link = True


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    inlines = [HotelRoomTypeInline]
    list_display = (
        "title",
        "listing_type",
        "country",
        "city",
    )
    list_filter = ("listing_type",)


class HotelRoomInline(admin.StackedInline):
    model = HotelRoom
    extra = 1


@admin.register(HotelRoomType)
class HotelRoomTypeAdmin(admin.ModelAdmin):
    inlines = [HotelRoomInline]
    list_display = (
        "hotel",
        "title",
    )
    show_change_link = True


@admin.register(HotelRoom)
class HotelRoomAdmin(admin.ModelAdmin):
    list_display = ("room_number",)


@admin.register(BookingInfo)
class BookingInfoAdmin(admin.ModelAdmin):
    pass


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    """Admin class for reservation model."""

    form = AdminReservationFrom
    list_display = ("hotel_or_apartment", "room", "check_in", "check_out", "created_on")

    def hotel_or_apartment(self, obj):
        """Display name for listing."""
        return f"{obj.listing.title} ({obj.listing.listing_type})".title()

    hotel_or_apartment.short_description = "Hotel / Apartment"
