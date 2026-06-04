from django_simple_nav.nav import Nav
from django_simple_nav.nav import NavItem

class MainNav(Nav):
    template_name = "main_nav.html"
    items = [
        NavItem(title="Community Recipes", url='recipes:index', append_slash=False),
        NavItem(title="My Recipes", url='recipes:my_recipes', permissions=["is_authenticated"]),
    ]
