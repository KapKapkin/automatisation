from decimal import Decimal
from django.test import TestCase
from rooms.forms import BuildingForm, LocationForm, DepartmentForm, RoomForm
from rooms.models import Building, Location, Department


class BuildingFormTest(TestCase):
    """Юнит-тесты формы BuildingForm (ТЗ п.3: добавление/изменение корпусов)"""

    def test_valid_building_form(self):
        """Проверяет валидность формы с корректными данными"""
        form = BuildingForm(data={
            'name': 'Корпус А',
            'address': 'ул. Ленина, 1',
            'description': 'Главный корпус',
        })
        self.assertTrue(form.is_valid())

    def test_building_form_minimal(self):
        """Проверяет валидность формы только с обязательным полем name"""
        form = BuildingForm(data={'name': 'Корпус Б', 'address': '', 'description': ''})
        self.assertTrue(form.is_valid())

    def test_building_form_empty_name(self):
        """Проверяет, что пустое имя не проходит валидацию"""
        form = BuildingForm(data={'name': '', 'address': '', 'description': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_building_form_widgets(self):
        """Проверяет наличие CSS-класса form-control у виджетов"""
        form = BuildingForm()
        self.assertIn('form-control', form.fields['name'].widget.attrs.get('class', ''))


class LocationFormTest(TestCase):
    """Юнит-тесты формы LocationForm"""

    def setUp(self):
        self.building = Building.objects.create(name='Корпус А')

    def test_valid_location_form(self):
        """Проверяет валидность формы расположения с корректными данными"""
        form = LocationForm(data={
            'building': self.building.pk,
            'name': '1 этаж',
            'ceiling_height': '3.50',
        })
        self.assertTrue(form.is_valid())

    def test_location_form_negative_height(self):
        """Проверяет, что отрицательная высота потолков не проходит валидацию"""
        form = LocationForm(data={
            'building': self.building.pk,
            'name': '1 этаж',
            'ceiling_height': '-2.00',
        })
        self.assertFalse(form.is_valid())

    def test_location_form_zero_height(self):
        """Проверяет, что нулевая высота потолков не проходит валидацию"""
        form = LocationForm(data={
            'building': self.building.pk,
            'name': '1 этаж',
            'ceiling_height': '0',
        })
        self.assertFalse(form.is_valid())


class DepartmentFormTest(TestCase):
    """Юнит-тесты формы DepartmentForm"""

    def test_valid_department_form(self):
        """Проверяет валидность формы подразделения"""
        form = DepartmentForm(data={
            'name': 'Факультет ИТ',
            'department_type': 'faculty',
            'parent': '',
        })
        self.assertTrue(form.is_valid())

    def test_department_form_with_parent(self):
        """Проверяет создание подразделения с родительским элементом"""
        parent = Department.objects.create(name='Факультет ИТ', department_type='faculty')
        form = DepartmentForm(data={
            'name': 'Кафедра ПИ',
            'department_type': 'department',
            'parent': parent.pk,
        })
        self.assertTrue(form.is_valid())

    def test_department_form_empty_name(self):
        """Проверяет, что пустое название не проходит валидацию"""
        form = DepartmentForm(data={
            'name': '',
            'department_type': 'faculty',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class RoomFormTest(TestCase):
    """Юнит-тесты формы RoomForm (ТЗ п.4: добавление/изменение комнат)"""

    def setUp(self):
        self.building = Building.objects.create(name='Корпус А')
        self.location = Location.objects.create(
            building=self.building,
            name='1 этаж',
            ceiling_height=Decimal('3.00'),
        )

    def test_valid_room_form(self):
        """Проверяет валидность формы комнаты с корректными данными"""
        form = RoomForm(data={
            'building': self.building.pk,
            'location': self.location.pk,
            'room_number': '101',
            'width': '10.00',
            'length': '5.00',
            'capacity': '30',
            'purpose': '',
            'room_type': '',
            'department': '',
        })
        self.assertTrue(form.is_valid())

    def test_room_form_negative_width(self):
        """Проверяет, что отрицательная ширина не проходит валидацию"""
        form = RoomForm(data={
            'building': self.building.pk,
            'location': self.location.pk,
            'room_number': '101',
            'width': '-5.00',
            'length': '5.00',
        })
        self.assertFalse(form.is_valid())

    def test_room_form_negative_length(self):
        """Проверяет, что отрицательная длина не проходит валидацию"""
        form = RoomForm(data={
            'building': self.building.pk,
            'location': self.location.pk,
            'room_number': '101',
            'width': '5.00',
            'length': '-3.00',
        })
        self.assertFalse(form.is_valid())

    def test_room_form_location_building_mismatch(self):
        """Проверяет, что расположение из другого корпуса не проходит валидацию"""
        other_building = Building.objects.create(name='Корпус Б')
        other_location = Location.objects.create(
            building=other_building,
            name='2 этаж',
            ceiling_height=Decimal('3.00'),
        )
        form = RoomForm(data={
            'building': self.building.pk,
            'location': other_location.pk,
            'room_number': '201',
            'width': '5.00',
            'length': '5.00',
        })
        self.assertFalse(form.is_valid())

    def test_room_form_missing_room_number(self):
        """Проверяет, что пустой номер комнаты не проходит валидацию"""
        form = RoomForm(data={
            'building': self.building.pk,
            'location': self.location.pk,
            'room_number': '',
            'width': '5.00',
            'length': '5.00',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('room_number', form.errors)
