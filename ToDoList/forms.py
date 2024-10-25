from django import forms
from .models import Category, Task


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["title"]


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "deadline", "category"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields["category"].queryset = Category.objects.filter(User=user)


class CompleteTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["completed"]
        labels = {
            "completed": "",
        }
