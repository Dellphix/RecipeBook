import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.http import Http404, HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.http import urlencode
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from measurement_converter import MeasurementConverter

from recipes.forms import RecipeForm, IngredientFormSet
from recipes.models import Recipe, Tag, TagCategory, Ingredient, Unit
from recipes.templatetags.custom_filters import display_quantity


class IndexView(generic.ListView):
    paginate_by = 12
    model = Recipe

    def dispatch(self, request, *args, **kwargs):
        hungry = self.request.GET.get('hungry', False)
        random = self.get_random_recipe()
        if hungry and random:
            return HttpResponseRedirect(reverse("recipes:detail", kwargs={'uuid': random.uuid}))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        search = self.request.GET.get('search', '')
        selected_tags = self.get_selected_tags()
        search_params = []
        for cat_name, cat_tags in selected_tags.items():
            for tag in cat_tags:
                search_params.append((cat_name, tag))
        search_params.append(('search', search))

        context = super().get_context_data(**kwargs)
        # Convert dict to list  without category names, then flatten list
        tags = [row[1] for row in selected_tags.items()]
        context['selected_tags'] = [val for row in tags for val in row]
        context['tag_categories'] = TagCategory.objects.all()
        context['selected_tags_params'] = urlencode(search_params)
        context['search'] = search
        return context

    def get_selected_tags(self):
        tags = {}
        for category in TagCategory.objects.all():
            category_tags = self.request.GET.getlist(category.name, '')
            if category_tags != '':
                tags[category.name] = category_tags
        return tags

    def get_recipes(self, **kwargs):
        tags = self.get_selected_tags()
        search = self.request.GET.get('search', '')
        recipes = Recipe.objects.filter(**kwargs)

        if tags:
            # Can't use distinct and then order by a different field,
            # so use a subquery to get around that
            sub_query = recipes
            for cat_name, cat_tags in tags.items():
                sub_query = sub_query.filter(tags__name__in=cat_tags)
            sub_query = sub_query.distinct('id')
            recipes = Recipe.objects.filter(id__in=sub_query)
        if search:
            recipes = recipes.filter(name__icontains=search)
        return recipes.order_by('name')

    def get_random_recipe(self, **kwargs):
        return self.get_recipes(**kwargs).order_by("?").first()

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

class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Recipe

    def dispatch(self, request, *args, **kwargs):
        recipe = self.get_object(queryset=request.GET)
        if not recipe.is_viewable_by(self.request.user):
            if self.request.user.id is not None and self.request.user.id != recipe.user.id:
                raise Http404
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
        else:
            data['ingredients'] = IngredientFormSet(instance=self.object)
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
            return super().form_invalid(form)

class CreateView(LoginRequiredMixin, generic.CreateView):
    model = Recipe
    form_class = RecipeForm

    def get_success_url(self, **kwargs):
        return reverse("recipes:detail", kwargs={'uuid': self.object.uuid})

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

def convert_quantity(request):
    value = float(request.GET['value'])
    from_unit = request.GET['from_unit']
    to_unit = request.GET['to_unit']
    result = MeasurementConverter.convert(value, from_unit, to_unit).to_value
    return HttpResponse("%s" % result)

@csrf_exempt
def convert_quantities(request):
    def get_conversion_unit(unit, unit_system):
        unit_system = 'us_customary' if unit_system == 'metric' else 'metric'
        conversion_table = {
            'metric': {
                Unit.KILOGRAM.__str__(): Unit.POUND.__str__(),
                Unit.GRAM.__str__(): Unit.OUNCE.__str__(),
                Unit.MILLILITRE.__str__(): Unit.CUP.__str__(),
                Unit.LITRE.__str__(): Unit.CUP.__str__()
            },
            'us_customary': {
                Unit.POUND.__str__(): Unit.KILOGRAM.__str__(),
                Unit.OUNCE.__str__(): Unit.GRAM.__str__(),
            }
        }

        try:
            conversion = conversion_table[unit_system][unit]
        except KeyError:
            # Not found, can't convert
            return None
        return conversion

    data = json.loads(request.body)
    converted_ingredients = []
    for ingredient in data["ingredients"]:
        to_unit = get_conversion_unit(ingredient["unit"], data["convert_to"])
        if to_unit:
            converted_quantity = MeasurementConverter.convert(float(ingredient["quantity"]), ingredient["unit"], to_unit).to_value;
            # print(round(converted_quantity, 2))
            converted_ingredients.append({
                "id": ingredient["id"],
                "quantity": display_quantity(round(converted_quantity, 2), to_unit),
                "unit": to_unit
            })
        else:
            ingredient["quantity"] = display_quantity(float(ingredient["quantity"]), ingredient["unit"])
            converted_ingredients.append(ingredient)
    return JsonResponse(converted_ingredients, safe=False)

