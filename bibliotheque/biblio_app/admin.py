from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from .forms import *

class PersonneAdmin(admin.ModelAdmin):
    list_display = ('email', 'nom', 'prenom', 'telephone', 'role')
    search_fields = ('email', 'nom', 'prenom', 'telephone')
    form = UpdateUserForm

admin.site.register(Personne, PersonneAdmin)

admin.site.register(Categorie)
admin.site.register(Ouvrage)
# admin.site.register(Personne)
admin.site.register(Utilisateur)
admin.site.register(Visiteur)
admin.site.register(Rechercher)
admin.site.register(Bibliothecaire)
admin.site.register(AdminSup)
admin.site.register(Exemplaire)
admin.site.register(Emprunter)
admin.site.register(Reservation)
admin.site.register(Gerer)
admin.site.register(Notification)