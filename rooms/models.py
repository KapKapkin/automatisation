from django.db import models
from django.core.validators import MinValueValidator


class Building(models.Model):
    """Модель Корпуса"""
    name = models.CharField(max_length=255, verbose_name='Наименование')
    address = models.CharField(max_length=500, blank=True, verbose_name='Адрес')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Корпус'
        verbose_name_plural = 'Корпуса'
        ordering = ['name']

    def __str__(self):
        return self.name


class Location(models.Model):
    """Модель Расположения в корпусе"""
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name='locations',
        verbose_name='Корпус'
    )
    name = models.CharField(max_length=255, verbose_name='Название расположения')
    ceiling_height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Высота потолков (м)'
    )

    class Meta:
        verbose_name = 'Расположение'
        verbose_name_plural = 'Расположения'
        ordering = ['building', 'name']

    def __str__(self):
        return f"{self.building.name} - {self.name}"


class Department(models.Model):
    """Модель Подразделения"""
    DEPARTMENT_TYPES = [
        ('faculty', 'Факультет'),
        ('department', 'Кафедра'),
        ('laboratory', 'Лаборатория'),
    ]

    name = models.CharField(max_length=255, verbose_name='Название')
    department_type = models.CharField(
        max_length=20,
        choices=DEPARTMENT_TYPES,
        verbose_name='Тип подразделения'
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительское подразделение'
    )

    class Meta:
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_department_type_display()})"


class RoomPurpose(models.Model):
    """Модель Назначения помещения"""
    name = models.CharField(max_length=255, verbose_name='Назначение')

    class Meta:
        verbose_name = 'Назначение помещения'
        verbose_name_plural = 'Назначения помещений'
        ordering = ['name']

    def __str__(self):
        return self.name


class RoomType(models.Model):
    """Модель Вида помещения"""
    name = models.CharField(max_length=255, verbose_name='Вид')

    class Meta:
        verbose_name = 'Вид помещения'
        verbose_name_plural = 'Виды помещений'
        ordering = ['name']

    def __str__(self):
        return self.name


class Room(models.Model):
    """Модель Комнаты"""
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name='rooms',
        verbose_name='Корпус'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='rooms',
        verbose_name='Расположение'
    )
    room_number = models.CharField(max_length=50, verbose_name='Номер комнаты')
    width = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Ширина (м)'
    )
    length = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Длина (м)'
    )
    purpose = models.ForeignKey(
        RoomPurpose,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rooms',
        verbose_name='Назначение'
    )
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rooms',
        verbose_name='Вид помещения'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rooms',
        verbose_name='Подразделение'
    )

    class Meta:
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'
        ordering = ['building', 'room_number']

    def __str__(self):
        return f"{self.building.name} - {self.room_number}"

    @property
    def area(self):
        """Вычисляемая площадь (ширина × длина)"""
        return self.width * self.length

    @property
    def volume(self):
        """Вычисляемый объём (ширина × длина × высота потолков)"""
        return self.width * self.length * self.location.ceiling_height
