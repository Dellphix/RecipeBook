from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import urlencode
from django.views import generic

from recipes.forms import RecipeForm, IngredientFormSet
from recipes.models import Recipe, Tag, Ingredient


class IndexView(generic.ListView):
    paginate_by = 9
    model = Recipe

    def get_context_data(self, **kwargs):
        selected_tags = self.request.GET.getlist('tag', '')
        selected_tags_params = []
        for tag in selected_tags:
            selected_tags_params.append(('tag', tag))

        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        context['selected_tags'] = selected_tags
        context['selected_tags_params'] = urlencode(selected_tags_params)
        return context

    def get_recipes(self, **kwargs):
        tags = self.request.GET.getlist('tag', '')
        recipes = Recipe.objects.filter(**kwargs)

        if tags:
            # Can't use distinct and then order by a different field,
            # so use a subquery to get around that
            sub_query = (recipes.filter(tags__name__in=tags) # add filter to existing query
                         .distinct('id'))
            recipes = Recipe.objects.filter(id__in=sub_query)
        return recipes.order_by('name')

class UserIndexView(LoginRequiredMixin, IndexView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_public_page'] = False
        return context

    def get_queryset(self):
        return self.get_recipes(user_id=self.request.user.id)

class PublicIndexView(IndexView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_public_page'] = True
        return context

    def get_queryset(self):
        return self.get_recipes(is_public=True)

class DetailView(generic.DetailView):
    model = Recipe

    def dispatch(self, request, *args, **kwargs):
        recipe = self.get_object(queryset=request.GET)
        if self.request.user.id is not None and self.request.user.id != recipe.user.id:
            raise Http404
        if not recipe.is_viewable_by(self.request.user):
            return redirect_to_login(f'/{recipe.uuid}/', '/accounts/login/')
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        recipe = Recipe.objects.get(uuid=self.kwargs['uuid'])
        return recipe


class UpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name_suffix = "_update_form"

    def get_success_url(self, **kwargs):
        return reverse("recipes:detail", kwargs={'uuid': self.kwargs['uuid']})

    def get_object(self, queryset=None):
        recipe = Recipe.objects.get(uuid=self.kwargs['uuid'])
        if self.request.user.id is not None and self.request.user.id != recipe.user.id:
            raise Http404
        if not recipe.is_viewable_by(self.request.user):
            return redirect_to_login(f'/{recipe.uuid}/', '/accounts/login/')
        return recipe

    def get_context_data(self, **kwargs):
        data = super(UpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            data['ingredients'] = IngredientFormSet(self.request.POST, instance=self.object)
            # data['ingredients'].full_clean()
            print('post', self.request.POST)
            print('formset', data['ingredients'].forms)
        else:
            data['ingredients'] = IngredientFormSet(instance=self.object)
            print('not post', data['ingredients'].forms)
        return data

    def form_valid(self, form):
        context = self.get_context_data(form=form)
        formset = context['ingredients']
        if formset.is_valid():
            response = super().form_valid(form)
            formset.instance = self.object
            formset.save()
            return response
        else:
            print('invalid', formset.forms)
            return super().form_invalid(form)

class CreateView(LoginRequiredMixin, generic.CreateView):
    model = Recipe
    form_class = RecipeForm

    def get_success_url(self, **kwargs):
        return reverse("recipes:my_recipes")

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['ingredients'] = IngredientFormSet(self.request.POST)
        else:
            context['ingredients'] = IngredientFormSet()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        context = self.get_context_data(form=form)
        formset = context['ingredients']
        if formset.is_valid():
            response = super().form_valid(form)
            formset.instance = self.object
            formset.save()
            return response
        else:
            return super().form_invalid(form)

class DeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Recipe

    def get_success_url(self, **kwargs):
        return reverse("recipes:my_recipes")

    def get_object(self, queryset=None):
        recipe = Recipe.objects.get(uuid=self.kwargs['uuid'])
        if self.request.user.id is not None and self.request.user.id != recipe.user.id:
            raise Http404
        if not recipe.is_viewable_by(self.request.user):
            return redirect_to_login(f'/{recipe.uuid}/', '/accounts/login/')
        return recipe

def ajax_ingredient(request):
    formset = IngredientFormSet()
    return render(request, 'recipes/ajax_ingredient.html', {'formset': formset})