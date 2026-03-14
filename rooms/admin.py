from django.contrib import admin
from .models import Building, Location, Department, RoomPurpose, RoomType, Room


class LocationInline(admin.TabularInline):
    model = Location
    extra = 1


class RoomInline(admin.TabularInline):
    model = Room
    extra = 0
    fields = ['room_number', 'width', 'length', 'capacity', 'purpose', 'room_type', 'department']


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'rooms_count']
    search_fields = ['name', 'address']
    inlines = [LocationInline]

    def rooms_count(self, obj):
        return obj.rooms.count()
    rooms_count.short_description = 'Кол-во комнат'


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'building', 'ceiling_height']
    list_filter = ['building']
    search_fields = ['name', 'building__name']
    inlines = [RoomInline]


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'department_type', 'parent']
    list_filter = ['department_type']
    search_fields = ['name']


@admin.register(RoomPurpose)
class RoomPurposeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'building', 'location', 'capacity', 'purpose', 'room_type', 'department', 'get_area', 'get_volume']
    list_filter = ['building', 'purpose', 'room_type', 'department']
    search_fields = ['room_number', 'building__name']
    list_select_related = ['building', 'location', 'purpose', 'room_type', 'department']

    def get_area(self, obj):
        return f"{obj.area:.2f} м²"
    get_area.short_description = 'Площадь'

    def get_volume(self, obj):
        return f"{obj.volume:.2f} м³"
    get_volume.short_description = 'Объём'
