from django.urls import path
from . import views

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),
    
    # Корпуса (Buildings)
    path('buildings/', views.BuildingListView.as_view(), name='building_list'),
    path('buildings/create/', views.BuildingCreateView.as_view(), name='building_create'),
    path('buildings/<int:pk>/', views.BuildingDetailView.as_view(), name='building_detail'),
    path('buildings/<int:pk>/edit/', views.BuildingUpdateView.as_view(), name='building_update'),
    path('buildings/<int:pk>/delete/', views.BuildingDeleteView.as_view(), name='building_delete'),
    path('buildings/<int:pk>/departments/', views.building_departments, name='building_departments'),
    
    # Комнаты (Rooms)
    path('rooms/', views.RoomListView.as_view(), name='room_list'),
    path('rooms/create/', views.RoomCreateView.as_view(), name='room_create'),
    path('rooms/<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),
    path('rooms/<int:pk>/edit/', views.RoomUpdateView.as_view(), name='room_update'),
    path('rooms/<int:pk>/delete/', views.RoomDeleteView.as_view(), name='room_delete'),
    
    # Расположения (Locations)
    path('locations/', views.LocationListView.as_view(), name='location_list'),
    path('locations/create/', views.LocationCreateView.as_view(), name='location_create'),
    path('locations/<int:pk>/edit/', views.LocationUpdateView.as_view(), name='location_update'),
    path('locations/<int:pk>/delete/', views.LocationDeleteView.as_view(), name='location_delete'),
    
    # Подразделения (Departments)
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department_update'),
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='department_delete'),
    
    # Отчёты (Reports)
    path('reports/areas/', views.report_areas, name='report_areas'),
]
