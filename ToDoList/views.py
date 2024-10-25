import calendar
from datetime import timedelta

from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .forms import *


class CustomLoginView(LoginView):
    template_name = "ToDoList/login.html"
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("tasks-page")


class RegisterView (FormView):
    template_name = "ToDoList/register.html"
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy("tasks-page")

    def form_valid(self, form):

        user = form.save() # Once form is validated, we have to save it, which is a User object
        if user is not None:
            login(self.request, user) # log in the user

        return super(RegisterView, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("tasks-page")

        return super(RegisterView, self).get(*args, **kwargs)


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "ToDoList/task_list.html"
    ordering = "deadline"

    def get_queryset(self):
        period = self.request.GET.get("period", "all")
        category = self.request.GET.get("category", None)
        queryset = Task.objects.all()

        # Filter by category
        if category:
            queryset = queryset.filter(category__title=category)

        # Filter by period

        now = timezone.now()

        if period == "today":
            queryset = queryset.filter(deadline__date=now.date())

        elif period == "week":
            start_of_week = now.date() - timedelta(days=now.weekday())
            end_of_week = now.date() + timedelta(days=7 - now.weekday())
            queryset = queryset.filter(deadline__date__gte=start_of_week).filter(deadline__date__lt=end_of_week)

        elif period == "month":
            start_of_month = now.replace(day=1).date()
            end_of_month = (start_of_month + timedelta(days=32)).replace(day=1)
            queryset = queryset.filter(deadline__date__gte=start_of_month).filter(deadline__date__lt=end_of_month)

        elif period == "year":
            start_of_year = now.replace(day=1, month=1).date()
            end_of_year = start_of_year.replace(year=start_of_year.year + 1)
            queryset = queryset.filter(deadline__date__gte=start_of_year).filter(deadline__date__lt=end_of_year)

        return queryset.filter(User=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["categories"] = Category.objects.all().filter(User=self.request.user)
        context["current_category"] = self.request.GET.get('category', None)
        context["current_period"] = self.request.GET.get('period', 'all')

        queryset = self.get_queryset()
        uncompleted_tasks = queryset.filter(completed=False).order_by("-deadline")
        completed_tasks = queryset.filter(completed=True).order_by("-finished_date")

        # Uncompleted_tasks should be allocated between sub-periods

        current_period = self.request.GET.get('period', 'all')
        sub_period_names = []
        sub_period_tasks = {}

        if current_period == "all":
            sub_period_names.append("all")
            sub_period_tasks["all"] = uncompleted_tasks

        elif current_period == "today":
            now = timezone.now()
            today = now.date().strftime("Today - %-d %b")

            sub_period_names.append(today)
            sub_period_tasks[today] = uncompleted_tasks

        elif current_period == "week":
            now = timezone.now()
            start_of_week = now.date() - timedelta(days=now.weekday())

            for i in range(7):
                week_day = start_of_week + timedelta(days=i)

                sub_period_names.append(week_day.strftime("%A - %-d %b"))  # Monday - 8 Oct
                sub_period_tasks[week_day.strftime("%A - %-d %b")] = uncompleted_tasks.filter(deadline__date=week_day)

        elif current_period == "month":
            now = timezone.now()
            start_of_month = now.replace(day=1).date()
            end_of_month = (start_of_month + timedelta(days=32)).replace(day=1)

            for i in range(4):
                section_start_day = start_of_month + timedelta(days=i * 7)
                section_end_day = None
                if i != 3:
                    section_end_day = section_start_day + timedelta(days=7)
                else:
                    section_end_day = end_of_month

                sub_period_names.append(section_start_day.strftime(f"%-d - {section_end_day.day} %B"))  # 1-7 October
                sub_period_tasks[
                    section_start_day.strftime(f"%-d - {section_end_day.day} %B")] = uncompleted_tasks.filter(
                    deadline__date__gte=section_start_day).filter(deadline__date__lt=section_end_day)

        elif current_period == "year":
            now = timezone.now()
            start_of_year = now.replace(day=1, month=1).date()
            end_of_year = start_of_year.replace(year=start_of_year.year + 1)

            for i in range(12):
                sub_period_names.append(calendar.month_name[i + 1])
                sub_period_tasks[calendar.month_name[i + 1]] = uncompleted_tasks.filter(deadline__date__month=i + 1)

        context["uncompleted_tasks"] = uncompleted_tasks
        context["completed_tasks"] = completed_tasks

        context["sub_period_names"] = sub_period_names
        context["sub_period_tasks"] = sub_period_tasks

        # So, by this time, we introduced to our context
        # categories = All categories created by user
        # current_category = the current chosen category (None, if not chosen)
        # current_period = the current chosen period ("all", if not chosen)
        # sub_period_names = list of subdivisions for current period
        # sub_period_tasks = dictionary of key-value, where each sub_period_name equals list of uncompleted tasks.
        # completed_tasks = list of completed tasks
        # uncompleted_tasks = list of uncompleted tasks

        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = "task"


class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("tasks-page")
    # template_name = "task_form.html" default

    def form_valid(self, form):
        form.instance.User = self.request.user
        return super(TaskCreateView, self).form_valid(form)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()

        return form_class(user=self.request.user, **self.get_form_kwargs())


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("tasks-page")
    # template_name = "task_form.html" default

    def form_valid(self, form):
        form.instance.User = self.request.user
        return super(TaskUpdateView, self).form_valid(form)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()

        return form_class(user=self.request.user, **self.get_form_kwargs())


class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy("tasks-page")

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    success_url = reverse_lazy("tasks-page")

    def form_valid(self, form):
        form.instance.User = self.request.user
        return super(CategoryCreateView, self).form_valid(form)


