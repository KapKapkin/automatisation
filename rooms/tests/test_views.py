from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from rooms.models import Building, Location, Department, RoomPurpose, RoomType, Room


class ViewTestBase(TestCase):
    """Базовый класс с общими тестовыми данными"""

    def setUp(self):
        self.client = Client()
        self.building = Building.objects.create(
            name='Корпус А', address='ул. Ленина, 1', description='Главный'
        )
        self.building2 = Building.objects.create(
            name='Корпус Б', address='ул. Пушкина, 5'
        )
        self.location = Location.objects.create(
            building=self.building, name='1 этаж', ceiling_height=Decimal('3.00')
        )
        self.location2 = Location.objects.create(
            building=self.building, name='2 этаж', ceiling_height=Decimal('3.50')
        )
        self.purpose = RoomPurpose.objects.create(name='Аудитория')
        self.room_type = RoomType.objects.create(name='Лекционная')
        self.faculty = Department.objects.create(
            name='Факультет ИТ', department_type='faculty'
        )
        self.department = Department.objects.create(
            name='Кафедра ПИ', department_type='department', parent=self.faculty
        )
        self.room = Room.objects.create(
            building=self.building, location=self.location,
            room_number='101', width=Decimal('10.00'), length=Decimal('5.00'),
            purpose=self.purpose, room_type=self.room_type, department=self.faculty,
        )
        self.room2 = Room.objects.create(
            building=self.building, location=self.location2,
            room_number='201', width=Decimal('8.00'), length=Decimal('6.00'),
            purpose=self.purpose, room_type=self.room_type, department=self.department,
        )


# ======================================================================
# Тесты главной страницы
# ======================================================================

class HomeViewTest(ViewTestBase):
    """Интеграционные тесты главной страницы"""

    def test_home_status_code(self):
        """Проверяет, что главная страница возвращает 200"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_template(self):
        """Проверяет использование шаблона home.html"""
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'rooms/home.html')

    def test_home_context_counts(self):
        """Проверяет, что контекст содержит корректные счётчики"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.context['buildings_count'], 2)
        self.assertEqual(response.context['rooms_count'], 2)
        self.assertEqual(response.context['departments_count'], 2)


# ======================================================================
# Тесты CRUD корпусов (ТЗ п.3: добавление и изменение корпусов)
# ======================================================================

class BuildingListViewTest(ViewTestBase):
    """Интеграционные тесты списка корпусов"""

    def test_building_list_status(self):
        """Проверяет, что список корпусов возвращает 200"""
        response = self.client.get(reverse('building_list'))
        self.assertEqual(response.status_code, 200)

    def test_building_list_template(self):
        """Проверяет шаблон списка корпусов"""
        response = self.client.get(reverse('building_list'))
        self.assertTemplateUsed(response, 'rooms/building_list.html')

    def test_building_list_contains_buildings(self):
        """Проверяет, что все корпуса отображаются в списке"""
        response = self.client.get(reverse('building_list'))
        self.assertContains(response, 'Корпус А')
        self.assertContains(response, 'Корпус Б')

    def test_building_list_context(self):
        """Проверяет, что контекст содержит queryset корпусов"""
        response = self.client.get(reverse('building_list'))
        self.assertEqual(len(response.context['buildings']), 2)


class BuildingDetailViewTest(ViewTestBase):
    """Интеграционные тесты детальной страницы корпуса"""

    def test_building_detail_status(self):
        """Проверяет, что страница деталей корпуса возвращает 200"""
        response = self.client.get(reverse('building_detail', args=[self.building.pk]))
        self.assertEqual(response.status_code, 200)

    def test_building_detail_template(self):
        """Проверяет шаблон деталей корпуса"""
        response = self.client.get(reverse('building_detail', args=[self.building.pk]))
        self.assertTemplateUsed(response, 'rooms/building_detail.html')

    def test_building_detail_context_rooms(self):
        """Проверяет, что контекст содержит комнаты корпуса"""
        response = self.client.get(reverse('building_detail', args=[self.building.pk]))
        self.assertEqual(len(response.context['rooms']), 2)

    def test_building_detail_context_locations(self):
        """Проверяет, что контекст содержит расположения корпуса"""
        response = self.client.get(reverse('building_detail', args=[self.building.pk]))
        self.assertEqual(len(response.context['locations']), 2)

    def test_building_detail_404(self):
        """Проверяет 404 для несуществующего корпуса"""
        response = self.client.get(reverse('building_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)


class BuildingCreateViewTest(ViewTestBase):
    """Интеграционные тесты создания корпуса (ТЗ п.3)"""

    def test_building_create_get(self):
        """Проверяет, что форма создания корпуса отображается"""
        response = self.client.get(reverse('building_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rooms/building_form.html')

    def test_building_create_post_valid(self):
        """Проверяет создание корпуса через POST с валидными данными"""
        data = {'name': 'Корпус В', 'address': 'ул. Мира, 10', 'description': 'Новый'}
        response = self.client.post(reverse('building_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Building.objects.filter(name='Корпус В').exists())

    def test_building_create_post_invalid(self):
        """Проверяет, что пустое имя не создаёт корпус"""
        data = {'name': '', 'address': '', 'description': ''}
        response = self.client.post(reverse('building_create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Building.objects.count(), 2)

    def test_building_create_redirect(self):
        """Проверяет редирект после создания на список корпусов"""
        data = {'name': 'Корпус Г', 'address': '', 'description': ''}
        response = self.client.post(reverse('building_create'), data)
        self.assertRedirects(response, reverse('building_list'))


class BuildingUpdateViewTest(ViewTestBase):
    """Интеграционные тесты редактирования корпуса (ТЗ п.3)"""

    def test_building_update_get(self):
        """Проверяет отображение формы редактирования"""
        response = self.client.get(reverse('building_update', args=[self.building.pk]))
        self.assertEqual(response.status_code, 200)

    def test_building_update_post(self):
        """Проверяет обновление данных корпуса"""
        data = {'name': 'Корпус А (обновлён)', 'address': 'Новый адрес', 'description': ''}
        response = self.client.post(
            reverse('building_update', args=[self.building.pk]), data
        )
        self.assertEqual(response.status_code, 302)
        self.building.refresh_from_db()
        self.assertEqual(self.building.name, 'Корпус А (обновлён)')
        self.assertEqual(self.building.address, 'Новый адрес')


class BuildingDeleteViewTest(ViewTestBase):
    """Интеграционные тесты удаления корпуса"""

    def test_building_delete_get(self):
        """Проверяет отображение страницы подтверждения удаления"""
        response = self.client.get(reverse('building_delete', args=[self.building.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rooms/building_confirm_delete.html')

    def test_building_delete_post(self):
        """Проверяет удаление корпуса через POST"""
        response = self.client.post(reverse('building_delete', args=[self.building.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Building.objects.filter(pk=self.building.pk).exists())


# ======================================================================
# Тесты CRUD комнат (ТЗ п.4: добавление и изменение комнат)
# ======================================================================

class RoomListViewTest(ViewTestBase):
    """Интеграционные тесты списка комнат"""

    def test_room_list_status(self):
        """Проверяет, что список комнат возвращает 200"""
        response = self.client.get(reverse('room_list'))
        self.assertEqual(response.status_code, 200)

    def test_room_list_template(self):
        """Проверяет шаблон списка комнат"""
        response = self.client.get(reverse('room_list'))
        self.assertTemplateUsed(response, 'rooms/room_list.html')

    def test_room_list_filter_by_building(self):
        """Проверяет фильтрацию комнат по корпусу"""
        response = self.client.get(reverse('room_list'), {'building': self.building.pk})
        self.assertEqual(len(response.context['rooms']), 2)

    def test_room_list_filter_empty_building(self):
        """Проверяет, что фильтрация по корпусу без комнат возвращает пустой список"""
        response = self.client.get(reverse('room_list'), {'building': self.building2.pk})
        self.assertEqual(len(response.context['rooms']), 0)

    def test_room_list_context_buildings(self):
        """Проверяет, что контекст содержит все корпуса для фильтра"""
        response = self.client.get(reverse('room_list'))
        self.assertEqual(len(response.context['buildings']), 2)


class RoomDetailViewTest(ViewTestBase):
    """Интеграционные тесты детальной страницы комнаты"""

    def test_room_detail_status(self):
        """Проверяет, что страница комнаты возвращает 200"""
        response = self.client.get(reverse('room_detail', args=[self.room.pk]))
        self.assertEqual(response.status_code, 200)

    def test_room_detail_template(self):
        """Проверяет шаблон деталей комнаты"""
        response = self.client.get(reverse('room_detail', args=[self.room.pk]))
        self.assertTemplateUsed(response, 'rooms/room_detail.html')

    def test_room_detail_404(self):
        """Проверяет 404 для несуществующей комнаты"""
        response = self.client.get(reverse('room_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)


class RoomCreateViewTest(ViewTestBase):
    """Интеграционные тесты создания комнаты (ТЗ п.4)"""

    def test_room_create_get(self):
        """Проверяет отображение формы создания комнаты"""
        response = self.client.get(reverse('room_create'))
        self.assertEqual(response.status_code, 200)

    def test_room_create_post_valid(self):
        """Проверяет создание комнаты через POST"""
        data = {
            'building': self.building.pk,
            'location': self.location.pk,
            'room_number': '301',
            'width': '12.00',
            'length': '8.00',
            'purpose': self.purpose.pk,
            'room_type': self.room_type.pk,
            'department': self.faculty.pk,
        }
        response = self.client.post(reverse('room_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Room.objects.filter(room_number='301').exists())

    def test_room_create_post_invalid_negative_width(self):
        """Проверяет, что комната с отрицательной шириной не создаётся"""
        data = {
            'building': self.building.pk,
            'location': self.location.pk,
            'room_number': '302',
            'width': '-5.00',
            'length': '8.00',
        }
        response = self.client.post(reverse('room_create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Room.objects.filter(room_number='302').exists())


class RoomUpdateViewTest(ViewTestBase):
    """Интеграционные тесты редактирования комнаты"""

    def test_room_update_get(self):
        """Проверяет отображение формы редактирования комнаты"""
        response = self.client.get(reverse('room_update', args=[self.room.pk]))
        self.assertEqual(response.status_code, 200)

    def test_room_update_post(self):
        """Проверяет обновление данных комнаты"""
        data = {
            'building': self.building.pk,
            'location': self.location.pk,
            'room_number': '101А',
            'width': '12.00',
            'length': '6.00',
            'purpose': self.purpose.pk,
            'room_type': self.room_type.pk,
            'department': self.faculty.pk,
        }
        response = self.client.post(reverse('room_update', args=[self.room.pk]), data)
        self.assertEqual(response.status_code, 302)
        self.room.refresh_from_db()
        self.assertEqual(self.room.room_number, '101А')
        self.assertEqual(self.room.width, Decimal('12.00'))


class RoomDeleteViewTest(ViewTestBase):
    """Интеграционные тесты удаления комнаты"""

    def test_room_delete_get(self):
        """Проверяет страницу подтверждения удаления комнаты"""
        response = self.client.get(reverse('room_delete', args=[self.room.pk]))
        self.assertEqual(response.status_code, 200)

    def test_room_delete_post(self):
        """Проверяет удаление комнаты через POST"""
        response = self.client.post(reverse('room_delete', args=[self.room.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Room.objects.filter(pk=self.room.pk).exists())


# ======================================================================
# Тесты отчёта по площадям и объёмам (ТЗ п.1)
# ======================================================================

class ReportAreasViewTest(ViewTestBase):
    """Интеграционные тесты отчёта по площадям и объёмам помещений"""

    def test_report_areas_status(self):
        """Проверяет, что отчёт возвращает 200"""
        response = self.client.get(reverse('report_areas'))
        self.assertEqual(response.status_code, 200)

    def test_report_areas_template(self):
        """Проверяет шаблон отчёта"""
        response = self.client.get(reverse('report_areas'))
        self.assertTemplateUsed(response, 'rooms/report_areas.html')

    def test_report_areas_total_area(self):
        """ТЗ п.1: Проверяет общую площадь (10*5 + 8*6 = 50 + 48 = 98)"""
        response = self.client.get(reverse('report_areas'))
        self.assertEqual(response.context['total_area'], Decimal('98.00'))

    def test_report_areas_total_volume(self):
        """ТЗ п.1: Проверяет общий объём (10*5*3 + 8*6*3.5 = 150 + 168 = 318)"""
        response = self.client.get(reverse('report_areas'))
        expected = Decimal('150.0000') + Decimal('168.0000')
        self.assertEqual(response.context['total_volume'], expected)

    def test_report_areas_buildings_stats(self):
        """ТЗ п.1: Проверяет статистику по корпусам"""
        response = self.client.get(reverse('report_areas'))
        stats = response.context['buildings_stats']
        building_a_stats = [s for s in stats if s['building'] == self.building][0]
        self.assertEqual(building_a_stats['rooms_count'], 2)
        self.assertEqual(building_a_stats['total_area'], Decimal('98.00'))

    def test_report_areas_empty_building(self):
        """Проверяет статистику для корпуса без комнат"""
        response = self.client.get(reverse('report_areas'))
        stats = response.context['buildings_stats']
        building_b_stats = [s for s in stats if s['building'] == self.building2][0]
        self.assertEqual(building_b_stats['rooms_count'], 0)
        self.assertEqual(building_b_stats['total_area'], 0)


# ======================================================================
# Тесты структуры факультетов в корпусе (ТЗ п.2)
# ======================================================================

class BuildingDepartmentsViewTest(ViewTestBase):
    """Интеграционные тесты структуры факультетов в корпусе"""

    def test_departments_status(self):
        """Проверяет, что страница возвращает 200"""
        response = self.client.get(
            reverse('building_departments', args=[self.building.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_departments_template(self):
        """Проверяет шаблон"""
        response = self.client.get(
            reverse('building_departments', args=[self.building.pk])
        )
        self.assertTemplateUsed(response, 'rooms/building_departments.html')

    def test_departments_faculties_count(self):
        """ТЗ п.2: Проверяет количество факультетов в корпусе"""
        response = self.client.get(
            reverse('building_departments', args=[self.building.pk])
        )
        self.assertEqual(response.context['faculties_count'], 1)

    def test_departments_faculties_names(self):
        """ТЗ п.2: Проверяет названия факультетов"""
        response = self.client.get(
            reverse('building_departments', args=[self.building.pk])
        )
        faculty_names = list(
            response.context['faculties'].values_list('name', flat=True)
        )
        self.assertIn('Факультет ИТ', faculty_names)

    def test_departments_hierarchy(self):
        """ТЗ п.2: Проверяет иерархическую структуру подразделений"""
        response = self.client.get(
            reverse('building_departments', args=[self.building.pk])
        )
        departments = response.context['departments']
        self.assertTrue(departments.filter(name='Факультет ИТ').exists())
        self.assertTrue(departments.filter(name='Кафедра ПИ').exists())

    def test_departments_404(self):
        """Проверяет 404 для несуществующего корпуса"""
        response = self.client.get(reverse('building_departments', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_departments_empty_building(self):
        """Проверяет корпус без подразделений"""
        response = self.client.get(
            reverse('building_departments', args=[self.building2.pk])
        )
        self.assertEqual(response.context['faculties_count'], 0)


# ======================================================================
# Тесты CRUD расположений
# ======================================================================

class LocationListViewTest(ViewTestBase):
    """Интеграционные тесты списка расположений"""

    def test_location_list_status(self):
        """Проверяет, что список расположений возвращает 200"""
        response = self.client.get(reverse('location_list'))
        self.assertEqual(response.status_code, 200)

    def test_location_list_template(self):
        """Проверяет шаблон"""
        response = self.client.get(reverse('location_list'))
        self.assertTemplateUsed(response, 'rooms/location_list.html')

    def test_location_list_count(self):
        """Проверяет количество расположений в списке"""
        response = self.client.get(reverse('location_list'))
        self.assertEqual(len(response.context['locations']), 2)


class LocationCreateViewTest(ViewTestBase):
    """Интеграционные тесты создания расположения"""

    def test_location_create_post(self):
        """Проверяет создание расположения через POST"""
        data = {
            'building': self.building.pk,
            'name': '3 этаж',
            'ceiling_height': '2.80',
        }
        response = self.client.post(reverse('location_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Location.objects.filter(name='3 этаж').exists())


class LocationDeleteViewTest(ViewTestBase):
    """Интеграционные тесты удаления расположения"""

    def test_location_delete_post(self):
        """Проверяет удаление расположения"""
        response = self.client.post(
            reverse('location_delete', args=[self.location.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Location.objects.filter(pk=self.location.pk).exists())


# ======================================================================
# Тесты CRUD подразделений
# ======================================================================

class DepartmentListViewTest(ViewTestBase):
    """Интеграционные тесты списка подразделений"""

    def test_department_list_status(self):
        """Проверяет, что список подразделений возвращает 200"""
        response = self.client.get(reverse('department_list'))
        self.assertEqual(response.status_code, 200)

    def test_department_list_template(self):
        """Проверяет шаблон"""
        response = self.client.get(reverse('department_list'))
        self.assertTemplateUsed(response, 'rooms/department_list.html')


class DepartmentCreateViewTest(ViewTestBase):
    """Интеграционные тесты создания подразделения"""

    def test_department_create_post(self):
        """Проверяет создание подразделения через POST"""
        data = {
            'name': 'Факультет физики',
            'department_type': 'faculty',
            'parent': '',
        }
        response = self.client.post(reverse('department_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Department.objects.filter(name='Факультет физики').exists())


class DepartmentDeleteViewTest(ViewTestBase):
    """Интеграционные тесты удаления подразделения"""

    def test_department_delete_post(self):
        """Проверяет удаление подразделения"""
        response = self.client.post(
            reverse('department_delete', args=[self.department.pk])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Department.objects.filter(pk=self.department.pk).exists())
