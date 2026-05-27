from django import urls
from django.urls import reverse_lazy, reverse
from django.views import generic

from recipes.models import Recipe, Tag


class IndexView(generic.ListView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        context['selected_tags'] = self.request.GET.getlist('tag', '')
        return context

    def get_queryset(self):
        tags = self.request.GET.getlist('tag', '')
        if tags:
            return Recipe.objects.filter(tags__name__in=tags)
        return Recipe.objects.all()

class DetailView(generic.DetailView):
    model = Recipe

class UpdateView(generic.UpdateView):
    model = Recipe
    fields = ["name", "prep_time", "cook_time", "description", "tags"]
    template_name_suffix = "_update_form"

    def get_success_url(self, **kwargs):
        return reverse("recipes:detail", kwargs={'pk': self.kwargs['pk']})

class DeleteView(generic.DeleteView):
    model = Recipe
    success_url = '/recipes'

class CreateView(generic.CreateView):
    model = Recipe
    fields = ["name", "prep_time", "cook_time", "description", "tags"]
    success_url = '/recipes'