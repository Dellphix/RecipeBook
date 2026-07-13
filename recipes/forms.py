from django import forms
from django.forms import inlineformset_factory

from recipes.models import Recipe, Ingredient

class CustomImageInput(forms.ClearableFileInput):
    template_name = 'custom_image_input.html'


class RecipeForm(forms.ModelForm):
    image = forms.ImageField(widget=CustomImageInput(), required=False)
    def __init__(self, *args, **kwargs):
        super(RecipeForm, self).__init__(*args, **kwargs)
        self.fields['is_public'].widget.attrs = {
            'class': 'boolean-checkbox'
        }

    class Meta:
        model=Recipe
        exclude = ['user', 'uuid']
        widgets = {
            'tags': forms.CheckboxSelectMultiple,
        }
        prep_time = forms.CharField(label="Prep Time (min)")

        labels = {
            'prep_time': 'Prep Time (min)',
            'cook_time': 'Cook Time (min)',
        }

IngredientFormSet = inlineformset_factory(Recipe, Ingredient, fields=[
    "quantity",
    "unit",
    "description",
], extra=1, max_num = None, )
