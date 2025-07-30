from django import forms
from .models import BotConfiguration

QUANTITY_CHOICES = [
    ('1', '1'),
    ('5', '5'),
    ('10', '10'),
    ('25', '25'),
    ('50', '50'),
]

class BotConfigurationForm(forms.ModelForm):
    class Meta:
        model = BotConfiguration
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter bot config name'}),
            'time_frame': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.Select(choices=QUANTITY_CHOICES, attrs={'class': 'form-select'}),
            'broker': forms.Select(attrs={'class': 'form-select'}),
            'strategy': forms.Select(attrs={'class': 'form-select'}),
            'exit_type': forms.Select(attrs={'class': 'form-select'}),
            'index': forms.Select(attrs={'class': 'form-select'}),
            'target': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stoploss': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
