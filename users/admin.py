from django.contrib import admin

from .models import Invitation

class InvitationAdmin(admin.ModelAdmin):
    readonly_fields = ["user"]
    list_display = ["code", "link", "user", "was_used"]

admin.site.register(Invitation, InvitationAdmin)
