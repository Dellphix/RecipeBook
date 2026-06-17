from dataclasses import dataclass
from urllib.parse import urlparse

from django import template
from django.template import Context
from django.urls import reverse

register = template.Library()


@dataclass
class NavItem:
    title: str
    url: str
    active: bool = False

    def check_active(self, request):
        url_path = urlparse(self.url).path
        request_path = request.path
        self.active = url_path == request_path

class MainNav:
    template_name = "main_nav.html"
    items = [
        NavItem(title="Community Recipes", url=reverse('recipes:index')),
        NavItem(title="My Recipes", url=reverse('recipes:my_recipes')),
    ]

    def process_items(self, request):
        for item in self.items:
            item.check_active(request)

class NavNode(template.Node):
    def __init__(self):
        pass

    def render(self, context):
        request = context.get("request", None)
        nav = MainNav()
        nav.process_items(request)
        template = context.template.engine.get_template(MainNav.template_name)
        return template.render(Context({"items": nav.items}, autoescape=context.autoescape))


@register.tag
def recipe_nav(parser, token):
    return NavNode()

