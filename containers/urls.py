from django.urls import path
from . import views

# urlpatterns = [
#     path("", views.home),
#     path("start/", views.start_container),
#     path("stop/", views.stop_container),
#     path("kill/", views.kill_container),
#     path("list/", views.list_containers),
#     path("remove/", views.remove_container),
# ]

urlpatterns = [
    # path("", views.dashboard, name="dashboard"),
    path("", views.home, name="home"),  # LOGIN PAGE
    path("containers/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_view, name="logout"),
    path("terminal/", views.terminal_page, name="terminal_page"),
    path("logs/<str:name>/", views.logs_page, name="logs_page"),
    
]

