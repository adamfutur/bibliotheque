from django.contrib import admin
from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('',views.index, name='home'),
    path('apropos/', views.apropos, name='apropos'),
    path('contacteznous/', views.contacteznous, name='contacteznous'),
    path('ouvrage/<str:foo>',views.afficher_ouvrage,name='ouvrage'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/',views.logout_user,name='logout_user'),
    path('login_user/',views.LoginView.as_view(),name='login_user'),
    path('update_profile/',views.UpdateUser.as_view(),name='update_profile'),
    path('update_paswd/',views.UpdatePswd.as_view(),name='update_paswd'),
    path('search/', views.search, name='search'),
    path('gerer/', views.GererReservations.as_view(), name='gerer'),
    path('emprunts/', views.GererEmptunts.as_view(), name='emprunts'),
    path('reservation/annuler', views.AnnulerReservations.as_view(), name='annuler_reservation'),
    path('signaler_perte/', views.SignalerPerte.as_view(), name='signaler_perte'),
    path('signlaer_deterioration/', views.SignalerDeterioration.as_view(), name='signlaer_deterioration'),
    #liens pour categorie
    path('categorie/',views.categorie,name='categorie'),
    path('ajouter_categorie/', views.ajouter_categorie, name='ajouter_categorie'),
    path('modifier_categorie/', views.modifier_categorie,name='modifier_categorie'),
    path('supprimer_categorie/<id_categorie>/', views.supprimer_categorie,name='supprimer_categorie'),
    #liens our gestion de Bibliothecaire
    path('bibliothecaire/', views.bibliothecaire, name='bibliothecaire'),
    path('ajouter_bibliothecaire/', views.ajouter_bibliothecaire, name='ajouter_bibliothecaire'),
    path('modifier_bibliothecaire/', views.modifier_bibliothecaire, name='modifier_bibliothecaire'),
    path('supprimer_bibliothecaire/<str:id_bibliothecaire>/', views.supprimer_bibliothecaire, name='supprimer_bibliothecaire'),
    #liens pour emprunter
    path('reservations/',views.emprunt,name='reservations'),
    path('reservation_to_emprunt/<int:id_reservation>/', views.reservation_to_emprunt, name='reservation_to_emprunt'),
    path('rejeter_reservation/<int:id_reservation>/', views.rejeter_reservation, name='rejeter_reservation'),
    path('liste_emprunt/', views.liste_emprunt, name='liste_emprunt'),
    path('emprunts_overdue/', views.emprunts_overdue, name='emprunts_overdue'),
    path('modifier_emprunt/', views.modifier_emprunt, name='modifier_emprunt'),
    path('supprimer_emprunt/<id_emprunt>/', views.supprimer_emprunt, name='supprimer_emprunt'),
    path('rendre_emprunt/<id_emprunt>/', views.rendre_emprunt, name='supprimer_emprunt'),
    path('overdue_emprunt/', views.overdue_emprunt, name='overdue_emprunt'),
    path('prolonger_date_retour/', views.prolonger_date_retour, name='prolonger_date_retour'),
    #dash
    path('administration/', views.dash, name='admin'),
     #ouvrage 
    path('ouvrage/', views.ouvrage, name='ouvrage'),
    path('add_ouvrage/', views.add_ouvrage, name='add_ouvrage'),
    path('modifier_ouvrage/', views.modifier_ouvrage, name='modifier_ouvrage'),
    path('supprimer_ouvrage/<str:ISBN>/', views.supprimer_ouvrage, name='supprimer_ouvrage'),
    #exemplaires
    path('exemplaire/', views.exemplaire, name='exemplaire'),
        path('exemplaires/', views.exemplaires, name='exemplaires'),

    path('add_exemplaire/', views.add_exemplaire, name='add_exemplaire'),
    path('modify_exemplaire/', views.modifier_exemplaire, name='modifier_exemplaire'),
    path('delete_exemplaire/<str:id_exemplaire>/', views.delete_exemplaire, name='delete_exemplaire'),
    #historique
    path('historique/', views.historique, name='historique'),
    #consultation
    path('liste_consultation/', views.liste_consultation, name='liste_consultation'),
    path('consulter/', views.consulter, name='consulter'),
    path('supprimer_consultation/<int:id_consultation>/', supprimer_consultation, name='supprimer_consultation'),
    
    #notifications
    path('notifications/', views.notifications_view, name='notifications_view'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
     
]
