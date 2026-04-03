from django import forms
from .models import Booking, Room, Category
from django.db.models import Q


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'guests']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'guests': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        self.room_id = kwargs.pop('room_id', None)
        super().__init__(*args, **kwargs)

        self.fields['guests'].initial = 1

        if self.room_id:
            room = Room.objects.get(id=self.room_id)
            self.fields['guests'].widget.attrs['max'] = room.capacity

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')

        if check_in and check_out and self.room_id:
            overlapping_bookings = Booking.objects.filter(
                room_id=self.room_id,
                status__in=['pending', 'confirmed']
            ).filter(
                Q(check_in__lt=check_out) & Q(check_out__gt=check_in)
            )

            if overlapping_bookings.exists():
                raise forms.ValidationError("К сожалению, на выбранные даты этот номер уже занят.")

        return cleaned_data

    def clean_guests(self):
        guests = self.cleaned_data.get('guests')

        if guests < 1:
            raise forms.ValidationError("Минимальное количество гостей — 1")

        if self.room_id:
            room = Room.objects.get(id=self.room_id)
            if guests > room.capacity:
                raise forms.ValidationError(f"Максимум гостей для этого номера: {room.capacity}")

        return guests


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'custom-input', 'placeholder': 'Например: Люкс'}),
            'slug': forms.TextInput(attrs={'class': 'custom-input', 'placeholder': 'Например: lux'}),
            'description': forms.Textarea(attrs={'class': 'custom-input', 'rows': 3}),
        }

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['category', 'number', 'capacity', 'price_per_night', 'description', 'image', 'is_active']
        widgets = {
            'category': forms.Select(attrs={'class': 'custom-select'}),
            'number': forms.TextInput(attrs={'class': 'custom-input'}),
            'capacity': forms.NumberInput(attrs={'class': 'custom-input'}),
            'price_per_night': forms.NumberInput(attrs={'class': 'custom-input'}),
            'description': forms.Textarea(attrs={'class': 'custom-input', 'rows': 4}),
            'is_active': forms.CheckboxInput(attrs={'class': 'custom-checkbox'}),
        }
