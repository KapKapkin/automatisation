from django.core.management.base import BaseCommand
from rooms.models import Building, Location, Department, RoomPurpose, RoomType, Room


class Command(BaseCommand):
    help = 'Загружает тестовые данные для проверки работы системы'

    def handle(self, *args, **options):
        self.stdout.write('Загрузка тестовых данных...')

        # Корпуса
        b1 = Building.objects.create(name='Главный корпус', address='ул. Ленина, 1', description='Основное здание университета')
        b2 = Building.objects.create(name='Корпус Б', address='ул. Ленина, 3', description='Естественнонаучный корпус')
        b3 = Building.objects.create(name='Корпус В', address='ул. Пушкина, 10', description='Инженерный корпус')
        self.stdout.write(f'  Создано корпусов: {Building.objects.count()}')

        # Расположения (этажи)
        loc_b1_1 = Location.objects.create(building=b1, name='1 этаж', ceiling_height=3.50)
        loc_b1_2 = Location.objects.create(building=b1, name='2 этаж', ceiling_height=3.20)
        loc_b1_3 = Location.objects.create(building=b1, name='3 этаж', ceiling_height=3.20)
        loc_b2_1 = Location.objects.create(building=b2, name='1 этаж', ceiling_height=3.00)
        loc_b2_2 = Location.objects.create(building=b2, name='2 этаж', ceiling_height=3.00)
        loc_b3_1 = Location.objects.create(building=b3, name='1 этаж', ceiling_height=4.00)
        loc_b3_2 = Location.objects.create(building=b3, name='2 этаж', ceiling_height=3.50)
        self.stdout.write(f'  Создано расположений: {Location.objects.count()}')

        # Назначения помещений
        p_aud = RoomPurpose.objects.create(name='Аудитория')
        p_lab = RoomPurpose.objects.create(name='Лаборатория')
        p_off = RoomPurpose.objects.create(name='Офис')
        p_stor = RoomPurpose.objects.create(name='Склад')
        p_lib = RoomPurpose.objects.create(name='Библиотека')
        self.stdout.write(f'  Создано назначений: {RoomPurpose.objects.count()}')

        # Виды помещений
        t_lect = RoomType.objects.create(name='Лекционная')
        t_comp = RoomType.objects.create(name='Компьютерный класс')
        t_sem = RoomType.objects.create(name='Семинарская')
        t_pract = RoomType.objects.create(name='Практическая')
        t_admin = RoomType.objects.create(name='Административная')
        self.stdout.write(f'  Создано видов: {RoomType.objects.count()}')

        # Подразделения (иерархия)
        fac_it = Department.objects.create(name='Факультет информатики', department_type='faculty')
        dep_prog = Department.objects.create(name='Кафедра программирования', department_type='department', parent=fac_it)
        dep_is = Department.objects.create(name='Кафедра информационных систем', department_type='department', parent=fac_it)
        lab_ai = Department.objects.create(name='Лаборатория ИИ', department_type='laboratory', parent=dep_prog)

        fac_phys = Department.objects.create(name='Факультет физики', department_type='faculty')
        dep_gen_phys = Department.objects.create(name='Кафедра общей физики', department_type='department', parent=fac_phys)
        dep_theor = Department.objects.create(name='Кафедра теоретической физики', department_type='department', parent=fac_phys)

        fac_math = Department.objects.create(name='Факультет математики', department_type='faculty')
        dep_algebra = Department.objects.create(name='Кафедра алгебры', department_type='department', parent=fac_math)
        self.stdout.write(f'  Создано подразделений: {Department.objects.count()}')

        # Комнаты
        rooms_data = [
            # Главный корпус
            (b1, loc_b1_1, '101', 12, 8, p_aud, t_lect, fac_it),
            (b1, loc_b1_1, '102', 8, 6, p_aud, t_sem, dep_prog),
            (b1, loc_b1_1, '103', 6, 4, p_off, t_admin, fac_it),
            (b1, loc_b1_2, '201', 10, 8, p_aud, t_comp, dep_is),
            (b1, loc_b1_2, '202', 10, 7, p_aud, t_lect, fac_math),
            (b1, loc_b1_2, '203', 5, 4, p_off, t_admin, dep_algebra),
            (b1, loc_b1_3, '301', 12, 10, p_aud, t_lect, fac_phys),
            (b1, loc_b1_3, '302', 8, 6, p_lab, t_pract, dep_gen_phys),
            # Корпус Б
            (b2, loc_b2_1, '101', 10, 8, p_lab, t_pract, dep_gen_phys),
            (b2, loc_b2_1, '102', 6, 5, p_off, t_admin, fac_phys),
            (b2, loc_b2_1, '103', 8, 4, p_stor, None, None),
            (b2, loc_b2_2, '201', 10, 10, p_aud, t_comp, dep_is),
            (b2, loc_b2_2, '202', 8, 6, p_lab, t_pract, dep_theor),
            # Корпус В
            (b3, loc_b3_1, '101', 15, 10, p_aud, t_lect, fac_it),
            (b3, loc_b3_1, '102', 10, 8, p_lab, t_comp, lab_ai),
            (b3, loc_b3_1, '103', 12, 6, p_lib, None, None),
            (b3, loc_b3_2, '201', 10, 8, p_aud, t_sem, dep_prog),
            (b3, loc_b3_2, '202', 8, 6, p_lab, t_pract, dep_gen_phys),
        ]

        for building, location, number, w, l, purpose, rtype, dept in rooms_data:
            Room.objects.create(
                building=building,
                location=location,
                room_number=number,
                width=w,
                length=l,
                purpose=purpose,
                room_type=rtype,
                department=dept,
            )

        self.stdout.write(f'  Создано комнат: {Room.objects.count()}')
        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно загружены!'))
