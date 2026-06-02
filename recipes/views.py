from django import urls
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.contrib.auth.decorators import login_required

from recipes.forms import RecipeForm
from recipes.models import Recipe, Tag


class IndexView(LoginRequiredMixin, generic.ListView):
    redirect_field_name = 'redirect_to'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        context['selected_tags'] = self.request.GET.getlist('tag', '')
        context['is_public_page'] = False
        return context

    def get_queryset(self):
        tags = self.request.GET.getlist('tag', '')
        if tags:
            return Recipe.objects.filter(tags__name__in=tags)
        return Recipe.objects.filter(user_id=self.request.user.id)

class PublicIndexView(generic.ListView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        context['selected_tags'] = self.request.GET.getlist('tag', '')
        context['is_public_page'] = True
        return context

    def get_queryset(self):
        tags = self.request.GET.getlist('tag', '')
        if tags:
            return Recipe.objects.filter(tags__name__in=tags)
        return Recipe.objects.filter(is_public=True)

class DetailView(generic.DetailView):
    model = Recipe

    def get_object(self, queryset=None):
        recipe = Recipe.objects.get(uuid=self.kwargs['uuid'])
        if not recipe.is_viewable_by(self.request.user):
            raise Http404
        return recipe


class UpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name_suffix = "_update_form"
    redirect_field_name = 'redirect_to'

    def get_success_url(self, **kwargs):
        return reverse("recipes:detail", kwargs={'uuid': self.kwargs['uuid']})

    def get_object(self, queryset=None):
        recipe = Recipe.objects.get(uuid=self.kwargs['uuid'])
        if recipe.user.id != self.request.user.id:
            raise Http404
        return recipe

class DeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Recipe
    success_url = ''
    redirect_field_name = 'redirect_to'

class CreateView(LoginRequiredMixin, generic.CreateView):
    model = Recipe
    form_class = RecipeForm
    success_url = ''
    redirect_field_name = 'redirect_to'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)