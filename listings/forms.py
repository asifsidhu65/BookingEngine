from django import forms
from django.utils import timezone

from listings.models import Reservation, HotelRoom


class AdminReservationFrom(forms.ModelForm):
    """Reservation form."""

    class Meta:
        """Meta attributes for form."""

        model = Reservation
        fields = (
            "listing",
            "room",
            "check_in",
            "check_out",
        )

    def clean_room(self):
        """Clean room information."""
        room = self.cleaned_data["room"]
        listing = self.cleaned_data.get("listing")
        if listing.listing_type == listing.APARTMENT:
            return None
        if not room:
            raise forms.ValidationError("This field is required.")
        is_valid_room = HotelRoom.objects.filter(
            pk=room.id, hotel_room_type__hotel=listing
        ).exists()
        if is_valid_room:
            return room
        raise forms.ValidationError(f"{room} does not belongs to hotel {listing.title}")

    def clean_check_in(self):
        """Validate check_in date"""
        checkin = self.cleaned_data["check_in"]
        if checkin < timezone.now().date():
            raise forms.ValidationError("Invalid checkin date.")
        return checkin

    def clean(self):
        """Clean data."""
        data = super(AdminReservationFrom, self).clean()
        checkout = data.get("check_out")
        checkin = data.get("check_in")
        if checkin and checkout and checkin > checkout:
            self.add_error("check_out", "Checkout must be greater then checkin date.")
        self.check_reservation()
        return data

    def check_reservation(self):
        """Check either reservation exists or not."""
        if not self.is_valid():
            return None
        data = self.cleaned_data
        checkin, checkout = data["check_in"], data["check_out"]
        res = Reservation.objects.filter(
            check_in__lte=checkout, check_out__gte=checkin, room=data["room"]
        )
        if res.exists():
            self.add_error(
                "room", f"Reservation already exists in {checkin} ~ {checkout}"
            )
        return None
