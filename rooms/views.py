from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum, Count
from .models import Building, Location, Department, Room, RoomPurpose, RoomType
from .forms import BuildingForm, RoomForm, LocationForm, DepartmentForm


def home(request):
    """Главная страница"""
    context = {
        'buildings_count': Building.objects.count(),
        'rooms_count': Room.objects.count(),
        'departments_count': Department.objects.count(),
    }
    return render(request, 'rooms/home.html', context)


# Views для Корпусов (Building)
class BuildingListView(ListView):
    model = Building
    template_name = 'rooms/building_list.html'
    context_object_name = 'buildings'


class BuildingDetailView(DetailView):
    model = Building
    template_name = 'rooms/building_detail.html'
    context_object_name = 'building'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['rooms'] = self.object.rooms.select_related('location', 'purpose', 'room_type', 'department')
        context['locations'] = self.object.locations.all()
        return context


class BuildingCreateView(CreateView):
    model = Building
    form_class = BuildingForm
    template_name = 'rooms/building_form.html'
    success_url = reverse_lazy('building_list')


class BuildingUpdateView(UpdateView):
    model = Building
    form_class = BuildingForm
    template_name = 'rooms/building_form.html'
    success_url = reverse_lazy('building_list')


class BuildingDeleteView(DeleteView):
    model = Building
    template_name = 'rooms/building_confirm_delete.html'
    success_url = reverse_lazy('building_list')


# Views для Комнат (Room)
class RoomListView(ListView):
    model = Room
    template_name = 'rooms/room_list.html'
    context_object_name = 'rooms'

    def get_queryset(self):
        queryset = Room.objects.select_related('building', 'location', 'purpose', 'room_type', 'department')
        building_id = self.request.GET.get('building')
        if building_id:
            queryset = queryset.filter(building_id=building_id)
        search = self.request.GET.get('search', '').strip()
        if search:
            queryset = queryset.filter(number__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['buildings'] = Building.objects.all()
        context['selected_building'] = self.request.GET.get('building', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class RoomDetailView(DetailView):
    model = Room
    template_name = 'rooms/room_detail.html'
    context_object_name = 'room'


class RoomCreateView(CreateView):
    model = Room
    form_class = RoomForm
    template_name = 'rooms/room_form.html'
    success_url = reverse_lazy('room_list')


class RoomUpdateView(UpdateView):
    model = Room
    form_class = RoomForm
    template_name = 'rooms/room_form.html'
    success_url = reverse_lazy('room_list')


class RoomDeleteView(DeleteView):
    model = Room
    template_name = 'rooms/room_confirm_delete.html'
    success_url = reverse_lazy('room_list')


# Views для отчётов
def report_areas(request):
    """Отчёт по площадям и объёмам всех помещений"""
    rooms = Room.objects.select_related('building', 'location', 'purpose', 'room_type')
    
    total_area = sum(room.area for room in rooms)
    total_volume = sum(room.volume for room in rooms)
    
    # Статистика по корпусам
    buildings_stats = []
    for building in Building.objects.prefetch_related('rooms__location'):
        building_rooms = building.rooms.all()
        building_area = sum(room.area for room in building_rooms)
        building_volume = sum(room.volume for room in building_rooms)
        buildings_stats.append({
            'building': building,
            'rooms_count': len(building_rooms),
            'total_area': building_area,
            'total_volume': building_volume,
        })
    
    context = {
        'rooms': rooms,
        'total_area': total_area,
        'total_volume': total_volume,
        'buildings_stats': buildings_stats,
    }
    return render(request, 'rooms/report_areas.html', context)


def building_departments(request, pk):
    """Структура факультетов в корпусе"""
    building = get_object_or_404(Building, pk=pk)
    
    # Получаем все подразделения, связанные с комнатами в этом корпусе
    department_ids = Room.objects.filter(building=building).values_list('department_id', flat=True).distinct()
    departments = Department.objects.filter(id__in=department_ids)
    
    # Получаем только факультеты
    faculties = departments.filter(department_type='faculty')
    faculties_count = faculties.count()
    
    # Строим иерархию подразделений
    def build_hierarchy(departments):
        """Строит иерархическую структуру подразделений"""
        hierarchy = []
        root_departments = departments.filter(parent__isnull=True)
        
        for dept in root_departments:
            children = departments.filter(parent=dept)
            hierarchy.append({
                'department': dept,
                'children': build_hierarchy(children) if children.exists() else []
            })
        
        return hierarchy
    
    hierarchy = build_hierarchy(departments)
    
    context = {
        'building': building,
        'departments': departments,
        'faculties': faculties,
        'faculties_count': faculties_count,
        'hierarchy': hierarchy,
    }
    return render(request, 'rooms/building_departments.html', context)


# Views для Расположений (Location)
class LocationListView(ListView):
    model = Location
    template_name = 'rooms/location_list.html'
    context_object_name = 'locations'

    def get_queryset(self):
        return Location.objects.select_related('building')


class LocationCreateView(CreateView):
    model = Location
    form_class = LocationForm
    template_name = 'rooms/location_form.html'
    success_url = reverse_lazy('location_list')


class LocationUpdateView(UpdateView):
    model = Location
    form_class = LocationForm
    template_name = 'rooms/location_form.html'
    success_url = reverse_lazy('location_list')


class LocationDeleteView(DeleteView):
    model = Location
    template_name = 'rooms/location_confirm_delete.html'
    success_url = reverse_lazy('location_list')


# Views для Подразделений (Department)
class DepartmentListView(ListView):
    model = Department
    template_name = 'rooms/department_list.html'
    context_object_name = 'departments'


class DepartmentCreateView(CreateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'rooms/department_form.html'
    success_url = reverse_lazy('department_list')


class DepartmentUpdateView(UpdateView):
    model = Department
    form_class = DepartmentForm
    template_name = 'rooms/department_form.html'
    success_url = reverse_lazy('department_list')


class DepartmentDeleteView(DeleteView):
    model = Department
    template_name = 'rooms/department_confirm_delete.html'
    success_url = reverse_lazy('department_list')
