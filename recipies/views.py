from django.views import generic

from recipies.models import Recipe, Tag


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