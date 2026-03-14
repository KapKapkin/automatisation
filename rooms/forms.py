from django import forms
from django.core.exceptions import ValidationError
from .models import Building, Location, Department, RoomPurpose, RoomType, Room


class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = ['name', 'address', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['building', 'name', 'ceiling_height']
        widgets = {
            'building': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'ceiling_height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def clean_ceiling_height(self):
        ceiling_height = self.cleaned_data.get('ceiling_height')
        if ceiling_height is not None and ceiling_height <= 0:
            raise ValidationError('Высота потолков должна быть положительным числом')
        return ceiling_height


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'department_type', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'department_type': forms.Select(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
        }


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['building', 'location', 'room_number', 'width', 'length', 'capacity', 'purpose', 'room_type', 'department']
        widgets = {
            'building': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
            'width': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'length': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'purpose': forms.Select(attrs={'class': 'form-control'}),
            'room_type': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_width(self):
        width = self.cleaned_data.get('width')
        if width is not None and width <= 0:
            raise ValidationError('Ширина должна быть положительным числом')
        return width

    def clean_length(self):
        length = self.cleaned_data.get('length')
        if length is not None and length <= 0:
            raise ValidationError('Длина должна быть положительным числом')
        return length

    def clean(self):
        cleaned_data = super().clean()
        building = cleaned_data.get('building')
        location = cleaned_data.get('location')
        
        if building and location and location.building != building:
            raise ValidationError('Выбранное расположение не принадлежит указанному корпусу')
        
        return cleaned_data
