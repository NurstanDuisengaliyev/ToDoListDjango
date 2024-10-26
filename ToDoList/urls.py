from django.urls import path
from .views import *
from django.contrib.auth.views import LogoutView
from django.contrib import admin

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),


    path("", CustomLoginView.as_view(), name="login"),
    path("admin/", admin.site.urls),
    path("tasks/", TaskListView.as_view(), name="tasks-page"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task"),
    path("task-create/", TaskCreateView.as_view(), name="task-create"),
    path("task-update/<int:pk>/", TaskUpdateView.as_view(), name="task-update"),
    path("task-delete/<int:pk>/", TaskDeleteView.as_view(), name="task-delete"),
    path("category-create/", CategoryCreateView.as_view(), name="category-create"),
    # path("/", ) login, authentication
]