from decimal import Decimal
from django.test import TestCase
from rooms.models import Building, Location, Department, RoomPurpose, RoomType, Room


class BuildingModelTest(TestCase):
    """Юнит-тесты модели Building (Корпус)"""

    def setUp(self):
        self.building = Building.objects.create(
            name='Корпус А',
            address='ул. Ленина, 1',
            description='Главный корпус'
        )

    def test_building_creation(self):
        """Проверяет создание корпуса с корректными данными"""
        self.assertEqual(self.building.name, 'Корпус А')
        self.assertEqual(self.building.address, 'ул. Ленина, 1')
        self.assertEqual(self.building.description, 'Главный корпус')

    def test_building_str(self):
        """Проверяет строковое представление корпуса"""
        self.assertEqual(str(self.building), 'Корпус А')

    def test_building_ordering(self):
        """Проверяет сортировку корпусов по имени"""
        Building.objects.create(name='Корпус В')
        Building.objects.create(name='Корпус Б')
        buildings = list(Building.objects.values_list('name', flat=True))
        self.assertEqual(buildings, ['Корпус А', 'Корпус Б', 'Корпус В'])

    def test_building_blank_fields(self):
        """Проверяет создание корпуса с пустыми необязательными полями"""
        building = Building.objects.create(name='Корпус Б')
        self.assertEqual(building.address, '')
        self.assertEqual(building.description, '')


class LocationModelTest(TestCase):
    """Юнит-тесты модели Location (Расположение)"""

    def setUp(self):
        self.building = Building.objects.create(name='Корпус А')
        self.location = Location.objects.create(
            building=self.building,
            name='1 этаж',
            ceiling_height=Decimal('3.50')
        )

    def test_location_creation(self):
        """Проверяет создание расположения с корректными данными"""
        self.assertEqual(self.location.name, '1 этаж')
        self.assertEqual(self.location.ceiling_height, Decimal('3.50'))
        self.assertEqual(self.location.building, self.building)

    def test_location_str(self):
        """Проверяет строковое представление расположения"""
        self.assertEqual(str(self.location), 'Корпус А - 1 этаж')

    def test_location_cascade_delete(self):
        """Проверяет каскадное удаление расположений при удалении корпуса"""
        self.building.delete()
        self.assertEqual(Location.objects.count(), 0)


class DepartmentModelTest(TestCase):
    """Юнит-тесты модели Department (Подразделение)"""

    def setUp(self):
        self.faculty = Department.objects.create(
            name='Факультет ИТ',
            department_type='faculty'
        )

    def test_department_creation(self):
        """Проверяет создание подразделения с корректными данными"""
        self.assertEqual(self.faculty.name, 'Факультет ИТ')
        self.assertEqual(self.faculty.department_type, 'faculty')

    def test_department_str(self):
        """Проверяет строковое представление подразделения"""
        self.assertEqual(str(self.faculty), 'Факультет ИТ (Факультет)')

    def test_department_hierarchy(self):
        """Проверяет иерархическую связь parent → children"""
        child = Department.objects.create(
            name='Кафедра ПИ',
            department_type='department',
            parent=self.faculty
        )
        self.assertEqual(child.parent, self.faculty)
        self.assertIn(child, self.faculty.children.all())

    def test_department_types(self):
        """Проверяет допустимые типы подразделений"""
        dept = Department.objects.create(name='Кафедра', department_type='department')
        lab = Department.objects.create(name='Лаборатория', department_type='laboratory')
        self.assertEqual(dept.get_department_type_display(), 'Кафедра')
        self.assertEqual(lab.get_department_type_display(), 'Лаборатория')


class RoomPurposeModelTest(TestCase):
    """Юнит-тесты модели RoomPurpose (Назначение помещения)"""

    def test_room_purpose_str(self):
        purpose = RoomPurpose.objects.create(name='Учебная аудитория')
        self.assertEqual(str(purpose), 'Учебная аудитория')


class RoomTypeModelTest(TestCase):
    """Юнит-тесты модели RoomType (Вид помещения)"""

    def test_room_type_str(self):
        room_type = RoomType.objects.create(name='Лекционная')
        self.assertEqual(str(room_type), 'Лекционная')


class RoomModelTest(TestCase):
    """Юнит-тесты модели Room (Комната) — включая расчёт площади и объёма"""

    def setUp(self):
        self.building = Building.objects.create(name='Корпус А')
        self.location = Location.objects.create(
            building=self.building,
            name='1 этаж',
            ceiling_height=Decimal('3.00')
        )
        self.purpose = RoomPurpose.objects.create(name='Аудитория')
        self.room_type = RoomType.objects.create(name='Лекционная')
        self.department = Department.objects.create(
            name='Факультет ИТ',
            department_type='faculty'
        )
        self.room = Room.objects.create(
            building=self.building,
            location=self.location,
            room_number='101',
            width=Decimal('10.00'),
            length=Decimal('5.00'),
            purpose=self.purpose,
            room_type=self.room_type,
            department=self.department,
        )

    def test_room_creation(self):
        """Проверяет создание комнаты с корректными данными"""
        self.assertEqual(self.room.room_number, '101')
        self.assertEqual(self.room.building, self.building)
        self.assertEqual(self.room.location, self.location)

    def test_room_str(self):
        """Проверяет строковое представление комнаты"""
        self.assertEqual(str(self.room), 'Корпус А - 101')

    def test_room_area_calculation(self):
        """ТЗ п.1: Проверяет расчёт площади (ширина × длина = 10 × 5 = 50)"""
        self.assertEqual(self.room.area, Decimal('50.00'))

    def test_room_volume_calculation(self):
        """ТЗ п.1: Проверяет расчёт объёма (10 × 5 × 3 = 150)"""
        self.assertEqual(self.room.volume, Decimal('150.00'))

    def test_room_area_with_decimal_dimensions(self):
        """Проверяет расчёт площади с дробными размерами (7.5 × 4.2 = 31.50)"""
        room = Room.objects.create(
            building=self.building,
            location=self.location,
            room_number='102',
            width=Decimal('7.50'),
            length=Decimal('4.20'),
        )
        self.assertEqual(room.area, Decimal('31.5000'))

    def test_room_volume_with_decimal_dimensions(self):
        """Проверяет расчёт объёма с дробными размерами (7.5 × 4.2 × 3.0 = 94.50)"""
        room = Room.objects.create(
            building=self.building,
            location=self.location,
            room_number='103',
            width=Decimal('7.50'),
            length=Decimal('4.20'),
        )
        self.assertEqual(room.volume, Decimal('94.500000'))

    def test_room_cascade_delete_building(self):
        """Проверяет каскадное удаление комнат при удалении корпуса"""
        self.building.delete()
        self.assertEqual(Room.objects.count(), 0)

    def test_room_department_set_null(self):
        """Проверяет, что при удалении подразделения комната сохраняется (SET_NULL)"""
        self.department.delete()
        self.room.refresh_from_db()
        self.assertIsNone(self.room.department)

    def test_room_ordering(self):
        """Проверяет сортировку комнат по корпусу и номеру"""
        Room.objects.create(
            building=self.building, location=self.location,
            room_number='050', width=Decimal('5'), length=Decimal('5'),
        )
        rooms = list(Room.objects.values_list('room_number', flat=True))
        self.assertEqual(rooms, ['050', '101'])
