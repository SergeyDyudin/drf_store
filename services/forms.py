from django import forms

from items.models import Item
from services.models import Rent


class RentForm(forms.ModelForm):

    class Meta:
        model = Rent
        fields = [
            'item',
            'date_from',
            'date_to',
            'daily_payment',
        ]
        widgets = {
            'item': forms.TextInput(attrs={'readonly': True}),
            'date_from': forms.SelectDateWidget(),
            'date_to': forms.SelectDateWidget(),
            'daily_payment': forms.TextInput(attrs={'readonly': True}),
        }
