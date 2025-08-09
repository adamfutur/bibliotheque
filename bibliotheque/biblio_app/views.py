from datetime import timedelta, datetime
from .models import Notification
from django.views.decorators.http import require_POST
from django.utils.functional import SimpleLazyObject
from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .models import *
from django.core.exceptions import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import *
from cart.cart import *
from django.utils import timezone
from django.contrib.auth.models import User
from django.views.decorators.debug import sensitive_variables
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.forms import *
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.core.cache import cache


#-----------------------------------------------COTE ADMINISTRATION----------------------------------------
@login_required
def is_Staff(request):
    if not request.user.is_authenticated:
        return redirect('login_user')
    elif request.user.role == 'BIBLIOTHECAIRE' or request.user.role == 'ADMINSUP':
        return True
    else:
        return False
    

def is_staff_no_auth(request):
    if request.user.is_authenticated and (request.user.role == 'BIBLIOTHECAIRE' or request.user.role == 'ADMINSUP'):
        return True
    else:
        return False


@login_required
def is_adminSup(request):
    if not request.user.is_authenticated:
        return redirect('login_user')
    elif request.user.role == 'ADMINSUP':
        return True
    else:
        return False
    
@login_required
def is_bibliothecaire(request):
    if not request.user.is_authenticated:
        return redirect('login_user')
    elif request.user.role == 'BIBLIOTHECAIRE':
        return True
    else:
        return False


@login_required    
def overdue_emprunt(request):
    overdue_emprunts = Emprunter.objects.filter(date_retour__lt=timezone.now()).values()
    overdue_emprunts_length = len(overdue_emprunts)
    return JsonResponse({'overdue_emprunts_length': overdue_emprunts_length})


# DASHBOARD
@login_required
def dash(request):
    if is_Staff(request) : 
        ouvrages = Ouvrage.objects.all()
        categories=Categorie.objects.all()
        return render(request, 'admin_dash.html', {
            'ouvrages': ouvrages,
            'categories':categories
            })
    else:
        return redirect('home')


@login_required
def bibliothecaire(request):
    authorized = is_adminSup(request)
    if authorized:
        bibliothecaires = Bibliothecaire.objects.all() 
        paginator = Paginator(bibliothecaires, 10)  # Show 10 categories per page

        page_number = request.GET.get('page')
        bibliothecaires_list = paginator.get_page(page_number) 
        return render(request, 'bibliothecaire.html', {'bibliothecaires': bibliothecaires_list})
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')  # Rediriger vers la page d'accueil si non autorisé


def ajouter_bibliothecaire(request):
    authorized = is_adminSup(request)
    if authorized:
        if request.method == 'POST':
            nom = request.POST.get('nom')
            prenom = request.POST.get('prenom')
            telephone = request.POST.get('telephone')
            email = request.POST.get('email')
            password = request.POST.get('password')
            AdminSup.Ajouter_bibliothecaire(nom, prenom, telephone, email, password)
            messages.success(request, 'Bibliothecaire ajouté avec succès.')
            return JsonResponse({'message': 'Bibliothecaire ajouté avec succès.'}, status=200)
        else:
            return JsonResponse({'error': 'Méthode erronée.'}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': 'Vous n\'êtes pas autorisé à accéder à cette page.'}, status=400)


def modifier_bibliothecaire(request):
    authorized = is_adminSup(request)
    if authorized:
        ad_id = request.POST.get('id_bibliothecaire')
        bibliothecaire = get_object_or_404(Bibliothecaire, id_bibliothecaire=ad_id)

        if request.method == 'POST':
            nom = request.POST.get('nom')
            prenom = request.POST.get('prenom')
            telephone = request.POST.get('telephone')
            email = request.POST.get('email')
            password = request.POST.get('password')
            adminsup = AdminSup()
            adminsup.Modifier_bibliothecaire(ad_id, n_nom=nom, n_prenom=prenom, n_telephone=telephone, n_email=email,
                                        n_password=password)
            messages.success(request, 'Bibliothecaire modifié avec succès.')
            return JsonResponse({'message': 'Bibliothecaire modifié avec succès.'}, status=200)

        return JsonResponse({'error': 'Méthode incorrecte.'}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)


def supprimer_bibliothecaire(request, id_bibliothecaire):
    authorized = is_adminSup(request)
    if authorized:
        if request.method == 'DELETE':
            adminsup = AdminSup()
            adminsup.supprimer_bibliothecaire(id_bibliothecaire=id_bibliothecaire)
            messages.success(request, 'Bibliothecaire supprimé avec succès.')
            return JsonResponse({'message': 'Bibliothecaire supprimé avec succès.'}, status=200)
        else:
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error': 'Méthode incorrecte.'}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)
    

# les méthodes de réservations
@login_required
def reservations(request):
    if is_bibliothecaire(request) :
        reservations_query = Reservation.objects.all().order_by('id_reservation')
        return render(request,{'reservations': reservations_query})
    else :
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')


# les méthodes de emprunt
@login_required
def emprunt(request):
    if is_bibliothecaire(request) :
        reservations_list = Reservation.objects.all().order_by('id_reservation')
        paginator = Paginator(reservations_list, 10)  # Show 10 categories per page

        page_number = request.GET.get('page')
        reservations = paginator.get_page(page_number)
        return render(request, 'liste_reservations.html', {'reservations': reservations})
    else :
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')


def reservation_to_emprunt(request, id_reservation):
    if is_bibliothecaire(request):
        reservation = Reservation.objects.get(id_reservation=id_reservation)
        print(reservation.ouvrage)
        done, consulter, message = Emprunter.emprunter(id_bibliothecaire=request.user.email, id_ouvrage=reservation.ouvrage.ISBN, id_utilisateur=reservation.id_utilisateur.email)
        if done:
            reservation.delete()
            messages.success(request, message)
            return JsonResponse({'message': message}, status=200)
        elif consulter == 1:
            return JsonResponse({'consulter': message}, status=400)
        else:
            messages.error(request, message)
            return JsonResponse({'error': message}, status=500)
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)



def rejeter_reservation(request, id_reservation):
    if is_bibliothecaire(request) :
        if request.method == 'DELETE':
            print(id_reservation)
            Reservation.delete_reservation(Reservation,reservation_id=id_reservation)
            messages.success(request,'Réservation rejetée avec succès.')
            return JsonResponse({'message': 'Réservation rejetée avec succès.'}, status=200)
        
        messages.error(request, 'Méthode non autorisée.')
        return JsonResponse({'error': 'Méthode incorrecte.'}, status=500)
    else :
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)

#liste des emprunts
@login_required
def liste_emprunt(request):
    if is_bibliothecaire(request) :
        emprunt_list = Emprunter.objects.all().order_by('id_emprunt')
        ouvrages = Ouvrage.objects.all()
        exemplaires = Exemplaire.objects.all()
        paginator = Paginator(emprunt_list, 10)  # Show 10 categories per page

        page_number = request.GET.get('page')
        emprunts = paginator.get_page(page_number)
        return render(request, 'liste_emprunt.html', {'emprunts': emprunts, 'ouvrages': ouvrages, 'exemplaires': exemplaires,'showing':True})
    else :
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')
    

@login_required
def emprunts_overdue(request):
    if is_Staff(request) :
        emprunt_list = Emprunter.objects.filter(date_retour__lt=timezone.now(),rendu=False)
        ouvrages = Ouvrage.objects.all()
        exemplaires = Exemplaire.objects.all()
        paginator = Paginator(emprunt_list, 10)  # Show 10 categories per page

        page_number = request.GET.get('page')
        emprunts = paginator.get_page(page_number)
        return render(request, 'liste_emprunt.html', {'emprunts': emprunts, 'ouvrages': ouvrages, 'exemplaires': exemplaires,'showing':False})
    else :
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')
    

def modifier_emprunt(request):
    if is_bibliothecaire(request) :
        print("starting")
        emp_id = request.POST.get('id_emprunt')
        emprunt = get_object_or_404(Emprunter, id_emprunt=emp_id)
        
        if request.method == 'POST':
            id_exp = request.POST.get('id_exp')
            id_ouvrage = request.POST.get('id_o')
            id_bibliothecaire= request.user.email
            new_date = request.POST.get('date_s')
            emprunt.modifier_emprunt(id_exemplaire=id_exp, id_ouvrage=id_ouvrage, id_bibliothecaire=id_bibliothecaire, new_date=new_date)
            messages.success(request, 'Emprunt modifié avec succès.')
            return JsonResponse({'message': 'Emprunt modifié avec succès.'}, status=200)
        
        return JsonResponse({'error': 'Méthode incorrecte.'}, status=500)
    else :
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)


def rendre_emprunt(request, id_emprunt):
    if is_bibliothecaire(request) :
            Emprunter.Retourner_Emprunt(id_emprunt= id_emprunt)
            messages.success(request, 'Emprunt enregistrée!')
            return JsonResponse({'message' : 'Emprunt enregistrée!' }, status=200)
    else :
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error' : "Vous n'êtes pas autorisé à accéder à cette page." }, status=400)


def supprimer_emprunt(request, id_emprunt):
    if is_bibliothecaire(request) :
        if request.method == 'DELETE':
            Emprunter.Annuler_Emprunt(id_emprunt= id_emprunt)
            messages.success(request, 'Emprunt supprimée avec succès.')
            return JsonResponse({'message' : 'Emprunt supprimée avec succès.' }, status=200)
        
        messages.error(request, 'Méthode non autorisée.')
        return JsonResponse({'error' : 'Méthode non autorisée.' }, status=500)
    else :
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error' : "Vous n'êtes pas autorisé à accéder à cette page." }, status=400)


# Les méthodes de categorie
@login_required
def categorie(request):
    if is_Staff(request) :
        categories_list = Categorie.objects.all().order_by('id_categorie')
        paginator = Paginator(categories_list, 10)  # Show 10 categories per page

        page_number = request.GET.get('page')
        categories = paginator.get_page(page_number)

        return render(request, 'categorie.html', {'categories': categories})
    else :
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')


def ajouter_categorie(request):
    if is_Staff(request) :
        if request.method == 'POST':
            # id = request.POST.get('id_categorie')
            nom = request.POST.get('nom_categorie')
            description = request.POST.get('description_categorie')
            # Appel touts les enregistrements
            Categorie.Ajouter_Categorie(nom_categorie=nom, description_categorie=description)
            # Mise à jour de la table
            messages.success(request, 'Catégorie ajoutée avec succès.')
            return JsonResponse({'message' : 'Catégorie ajoutée avec succès.' }, status=200) 
        else:
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error' : 'Méthode non autorisée.' }, status=500)
    else :
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error' : 'Méthode non autorisée.' }, status=400)
    

def modifier_categorie(request):
    if is_Staff(request) :
        print("starting")
        categorie_id = request.POST.get('id_categorie')
        categorie = get_object_or_404(Categorie, id_categorie=categorie_id)
        
        if request.method == 'POST':
            nom = request.POST.get('nom_categorie')
            description = request.POST.get('description_categorie')
            categorie.modifier_categorie(categorie_id, nouveau_nom=nom,nouvelle_description=description)
            messages.success(request, 'Catégorie modifiée avec succès.')
            return JsonResponse({'message' : 'Catégorie modifiée avec succès.' }, status=200) 
        
        messages.error(request, 'Méthode non autorisée.')
        return JsonResponse({'error' : 'Méthode non autorisée.' }, status=500)
    else : 
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error' : "Vous n'êtes pas autorisé à accéder à cette page." }, status=400)


def supprimer_categorie(request,id_categorie):
    if is_Staff(request) :
        if request.method == 'DELETE':
            Categorie.supprimer_categorie(Categorie, categorie_id=id_categorie)
            messages.success(request, 'Catégorie supprimée avec succès.')
            return JsonResponse({'message' : 'Catégorie supprimée avec succès.' }, status=200)
        
        messages.error(request, 'Méthode non autorisée.')
        return JsonResponse({'error' : 'Méthode non autorisée.' }, status=500)
    else :
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error' : "Vous n'êtes pas autorisé à accéder à cette page." }, status=400)


#NEED TO BE MODIFIED 
@login_required
def ouvrage(request):
    ouvrages = Ouvrage.objects.all()
    categories = Categorie.objects.all()
    paginator = Paginator(ouvrages, 10)  # Show 10 categories per page

    page_number = request.GET.get('page')
    ouvrages_list = paginator.get_page(page_number)
    return render(request, 'ouvrage.html', {'ouvrages': ouvrages_list, 'categories': categories})



def add_ouvrage(request):
    if is_Staff(request) : 
        if request.method == 'POST':
            # Extract form data from request.POST
            ISBN = request.POST.get('ISBN')
            titre = request.POST.get('titre')
            auteur = request.POST.get('auteur')
            edition = request.POST.get('edition')
            type = request.POST.get('type')
            categorie_id = request.POST.get('categorie')
            categorie = get_object_or_404(Categorie, id_categorie=categorie_id)
            image = request.FILES.get('image')
            description = request.POST.get('description')
            num_exmp_dispo = request.POST.get('num_exmp_dispo')
            num_exemplaire= request.POST.get('num_exemplaire')

            Ouvrage.ajouter_ouvrage(Ouvrage,titre,auteur,edition,ISBN,type,categorie,image,description)
            messages.success(request, 'Ouvrage ajouté avec succés!')
            return JsonResponse({'message' : 'Ouvrage ajouté avec succés!' }, status=200)
        else:
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error' : 'Méthode non autorisée.' }, status=500)
    else :
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error' : "Vous n'êtes pas autorisé à accéder à cette page." }, status=400)


def modifier_ouvrage(request):
    if is_Staff(request) : 
        
        if request.method == 'POST':
            # Extract form data from request.POST
            isbn_g = request.POST.get('ISBN')
            titre = request.POST.get('titre')
            auteur = request.POST.get('auteur')
            edition = request.POST.get('edition')
            type = request.POST.get('type')
            nouvelle_categorie_id = request.POST.get('categorie')
            categorie = get_object_or_404(Categorie, id_categorie=nouvelle_categorie_id)
            image = request.FILES.get('image')
            description = request.POST.get('description')
            num_exmp_dispo = request.POST.get('num_exmp_dispo')
            num_exemplaire= request.POST.get('num_exemplaire')

            Ouvrage.modifier_ouvrage(Ouvrage,isbn_g,titre,auteur,edition,type,categorie,image,description)
        # Call modifier_ouvrage with isbn argument
            messages.success(request, 'Ouvrage modifié avec succés!')
            return JsonResponse({'message' : 'Ouvrage modifié avec succés!' }, status=200)
        else:
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error' : 'Méthode non autorisée.' }, status=500)
    else :
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error' : "Vous n'êtes pas autorisé à accéder à cette page." }, status=400)
     


def supprimer_ouvrage(request, ISBN):
    if is_Staff(request) :
        if request.method == 'DELETE':
            done=Ouvrage.supprimer_ouvrage(Ouvrage, ISBN=ISBN)
            if done :
                messages.success(request, 'Ouvrage supprimé avec succés!')
                return JsonResponse({'message': 'Ouvrage supprimé avec succés!'}, status=200)
            else :
                messages.error(request, 'Méthode non autorisée.')
                return JsonResponse({'error' : 'Echec de suppression de l\'ouvrage.' }, status=500)

        else :
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error' : 'Méthode non autorisée.' }, status=500)
    else :
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error' : "Vous n'êtes pas autorisé à accéder à cette page." }, status=400)


#exemplaire
@login_required
def exemplaire(request):
    print('katchaw')
    exemplaires = Exemplaire.objects.all()
    ouvrages = Ouvrage.objects.all()
    paginator = Paginator(exemplaires, 10)  # Show 10 categories per page

    page_number = request.GET.get('page')
    exemplaires_list = paginator.get_page(page_number)
    return render(request, 'exemplaire.html', {'exemplaires':exemplaires_list ,'ouvrages': ouvrages})


def add_exemplaire(request):
    if is_Staff(request) : 
        if request.method == 'POST':
            # Extract form data from request.POST
            deteriore_checked = request.POST.get('deteriore')
            deteriore = True if deteriore_checked else False

            emprunte_checked = request.POST.get('empruntable')
            empruntable = True if emprunte_checked else False

            perdu_checked = request.POST.get('perdu')
            perdu = True if perdu_checked else False

            ouvrage_id =request.POST.get('ouvrage')
            ouvrage = get_object_or_404(Ouvrage, ISBN=ouvrage_id)

            disponible_checked = request.POST.get('disponible')
            disponible = True if disponible_checked else False
            
        
            Bibliothecaire.add_exemplaire(deteriore=deteriore,perdu=perdu,empruntable=empruntable,ouvrage=ouvrage,disponible=disponible)
            messages.success(request, 'Exemplaire ajouté avec succés!')
            return JsonResponse({'message': 'Exemplaire ajouté avec succés!'}, status=200)
        else:
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error' : 'Méthode non autorisée.' }, status=500)
    else :
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error' : "Vous n'êtes pas autorisé à accéder à cette page." }, status=400)
    
def modifier_exemplaire(request):
    if is_Staff(request) : 
        id_ex = request.POST.get('id_exemplaire')
        exemplaire = get_object_or_404(Exemplaire, id_exemplaire=id_ex)
        id_ex = request.POST.get('id_exemplaire')
        ouvrages = Ouvrage.objects.all()
        if request.method == 'POST':
            # Extract form data from request.POST
            deteriore_checked = request.POST.get('deteriore')
            deteriore = True if deteriore_checked else False

            emprunte_checked = request.POST.get('empruntable')
            empruntable = True if emprunte_checked else False

            perdu_checked = request.POST.get('perdu')
            perdu = True if perdu_checked else False

            nouvelle_ouvrage_id = request.POST.get('ouvrage')
            ouvrage = get_object_or_404(Ouvrage, ISBN=nouvelle_ouvrage_id)

            disponible_checked = request.POST.get('disponible')
            disponible = True if disponible_checked else False
       
            bibliothecaire=Bibliothecaire()
            bibliothecaire.Modifier_exemplaire(id_ex, ndeteriore=deteriore, nperdu=perdu,nempruntable=empruntable, nouvrage=ouvrage ,ndisponible=disponible)
            messages.success(request, 'Exemplaire modifié avec succés!')
            return JsonResponse({'message': 'Exemplaire modifié avec succés!'}, status=200)
        else :
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error' : 'Méthode non autorisée.' }, status=500)
    else :
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error' : "Vous n'êtes pas autorisé à accéder à cette page." }, status=400)
    
     


def delete_exemplaire(request, id_exemplaire):
    if is_Staff(request) :
        if request.method == 'DELETE':
            bibliothecaire=Bibliothecaire()
            done = bibliothecaire.delete_exemplaire(id_exemplaire=id_exemplaire)
            if done :
                messages.success(request, 'Exemplaire modifié avec succés!')
                return JsonResponse({'message': 'Ouvrage deleted successfully.'}, status=200)
            else :
                messages.error(request, 'Echec lors de suppression de l\'exemplaire.')
                return JsonResponse({'error' : 'Echec lors de suppression de l\'exemplaire.' }, status=500)
   
        else:
            messages.error(request, 'Méthode non autorisée.')
            return JsonResponse({'error' : 'Méthode non autorisée.' }, status=500)
    else :
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error' : "Vous n'êtes pas autorisé à accéder à cette page." }, status=400)
     


#liste des consultations
@login_required
def liste_consultation(request):
    if is_bibliothecaire(request):
        consultation_list = Consulter.objects.all().order_by('id_consultation')
        ouvrages = Ouvrage.objects.all()
        exemplaires = Exemplaire.objects.all()
        paginator = Paginator(consultation_list, 10)  # Show 10 consultations per page

        page_number = request.GET.get('page')
        consultations = paginator.get_page(page_number)
        return render(request, 'liste_consultation.html', {'consultations': consultations, 'ouvrages': ouvrages, 'exemplaires': exemplaires, 'showing': True})
    else:
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')
    

@login_required
def supprimer_consultation(request, id_consultation):
    if is_bibliothecaire(request):
        if request.method == 'DELETE':
            try:
                consultation = Consulter.objects.get(id_consultation=id_consultation)
                done= Consulter.supprimer_consultation(consultation.id_consultation)
                if done :
                    messages.success(request,'Consultation supprimée avec succès.')
                    return JsonResponse({'message': 'Consultation supprimée avec succès.'}, status=200)
                else : 
                    messages.error(request,'Echec lors de la suppression de la consultation!')
                    return JsonResponse({'error': 'Echec lors de la suppression de la consultation!'}, status=500)
            except Consulter.DoesNotExist:
                messages.error(request,'Consultation non trouvée.')
                return JsonResponse({'error': 'Consultation non trouvée.'}, status=500)
        else:
            messages.error(request,'Méthode non autorisée.')
            return JsonResponse({'error': 'Méthode non autorisée.'}, status=400)
    else:
        messages.error(request,"Vous n'êtes pas autorisé à accéder à cette page.")
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)
    

def historique(request):
    if is_adminSup(request):
        history_entries = LogEntry.objects.all()
        paginator = Paginator(history_entries, 10)
        page_number = request.GET.get('page')
        try:
            page_obj = paginator.get_page(page_number)
        except PageNotAnInteger:
            page_obj = paginator.get_page(1)
        except EmptyPage:
            page_obj = paginator.get_page(paginator.num_pages)
        return render(request, 'historique.html', {'page_obj': page_obj})
    else:
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)
    

def consulter(request):
    if is_bibliothecaire(request):
        id_ouvrage = request.POST.get('isbn')
        user_email = request.POST.get('user_email')

        if not (id_ouvrage and user_email):
            messages.error('Tous les champs sont requis.')
            return JsonResponse({ 'error': 'Tous les champs sont requis.'}, status=400 )
        
        try:
            success, message = Consulter.consulter(id_ouvrage=id_ouvrage, id_bibliothecaire=request.user.email, id_utilisateur=user_email)
            if success :
                messages.success(request,message)
                return JsonResponse({'message': message}, status=200)
            else :
                messages.error(request,message)
                return JsonResponse({'error': message}, status=400)
        except Ouvrage.DoesNotExist:
            messages.error(request,"L'ouvrage n'existe pas.")
            return JsonResponse({'error': "L'ouvrage n'existe pas."}, status=500)
        except Bibliothecaire.DoesNotExist:
            messages.error(request,"Le bibliothecaire n'existe pas.")
            return JsonResponse({'error': "L'adhérent n'existe pas."}, status=500)
        except Utilisateur.DoesNotExist:
            messages.error(request,"L'utilisateur n'existe pas.")
            return JsonResponse({'error': "L'utilisateur n'existe pas."}, status=500)
        except Exception as e:
            messages.error(request,str(e))
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': "Vous n'êtes pas autorisé à accéder à cette page."}, status=400)

#-----------------------------------------COMMUN-------------------------------------------------

def index(request):
    ouvrages = Ouvrage.objects.all()
    categories = Categorie.objects.all()
    current_tab = 'home'
    if is_staff_no_auth(request):
        return render_admin(request,ouvrages,categories,current_tab)
    else:
        return render_user(request,ouvrages,categories,current_tab)


@login_required
def render_admin(request,ouvrages,categories,current_tab):
    return render(request, 'admin_dash.html', {
        'ouvrages': ouvrages,
        'categories': categories,
        'current_tab': current_tab
    })



def render_user(request,ouvrages,categories,current_tab):
    ouvrages = Ouvrage.objects.all()
    categories = Categorie.objects.all()
    current_tab = 'home'
    return render(request, 'accueil.html', {
        'ouvrages': ouvrages,
        'categories': categories,
        'current_tab': current_tab
    })


#-----------------------------------COTE UTILISATEUR----------------------------------------------- 

def accieul(request):
     return render(request,"base.html",context={})




def search_view(request):
    exemplaires = Utilisateur.get_all_exemplaires()
    return render(request, 'home.html', {'exemplaires': exemplaires})



def search(request):
    if request.method == 'GET':
        adresse_ip = request.META.get('REMOTE_ADDR')
        print(adresse_ip)
        
        # Create a Visiteur object to store the visitor's IP
        visiteur = Visiteur(adresse_ip=adresse_ip)
        
        try:
            # Retrieve GET parameters
            query = request.GET.get('query')  
            ouvrage_search = request.GET.get("ouvrage")
            exemplaire_search = request.GET.get("exemplaire")
            categorie_search = request.GET.get("categorie")
            ouvrages = Ouvrage.objects.all()  # Start with all objects
            categories = Categorie.objects.all()
            
            if categorie_search == 'tous_categories':
                categorie_search = None  # Remove category filter
            if ouvrage_search == 'tous_ouvrages':
                ouvrage_search = None  # Remove ouvrage filter
                
            if exemplaire_search:
                 ouvrages = ouvrages.filter(titre__icontains=exemplaire_search) | ouvrages.filter(auteur__icontains=exemplaire_search)
            else:
                # If exemplaire is not provided, apply other filters
                if ouvrage_search:
                    ouvrages = ouvrages.filter(type=ouvrage_search)
                if categorie_search:
                    ouvrages = ouvrages.filter(categorie=categorie_search)
                    
            print(ouvrages)
            
        except ValueError as e:
            print(e)
            messages.error(request, "Le type de recherche n'est pas compatible avec les champs de la classe. Vérifiez le critère de Rechercher.")
            return render(request, 'accueil.html', {})
     
        # Pass the queryset and categories to the template
        return render(request, 'accueil.html', {'ouvrages': ouvrages, 'categories': categories})
    else:
        # If the request method is not GET, render accueil.html without any data
        return render(request, 'accueil.html', {})



def exemplaire_actions(request):
    if request.method == 'POST':
        exemplaire_id = request.POST.get('exemplaire_id')
        action = request.POST.get('action')
        visiteur=Visiteur()

        try:
            user=Utilisateur()
            exemplaire = Exemplaire.objects.get(id=exemplaire_id)
            if action == 'signaler_deterioration':
                if user.signaler_deterioration(exemplaire):
                    messages.success(request, "Détérioration signalée avec succès.")
                else:
                    messages.error(request, "Impossible de signaler la détérioration pour cet exemplaire.")
            elif action == 'signaler_perte':
                if user.signaler_perdu(exemplaire):
                    messages.success(request, "Perte signalée avec succès.")
                else:
                    messages.error(request, "Impossible de signaler la perte pour cet exemplaire.")
            elif action == 'rendre_inempruntable':
                if user.rendre_inempruntable(exemplaire):
                    
                    messages.success(request, "Exemplaire rendu inempruntable avec succès.")
                else:
                    messages.error(request, "Impossible de rendre cet exemplaire inempruntable.")
            # Ajoutez d'autres conditions pour d'autres actions si nécessaire

        except Exemplaire.DoesNotExist:
            messages.error(request, "L'exemplaire n'existe pas.")
        except ValidationError as e:
            messages.error(request, str(e))

    return redirect('home')




class LoginView(View):

    @method_decorator(sensitive_variables('request'))
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, 'login.html', {})
    
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            password = request.POST.get('password')
            email = request.POST.get('email')
            user = authenticate(request, email=email, password=password)
            print(user)
            if user is not None:
                login(request, user)
                messages.success(request,'Vous avez fait votre authentification avec succès')
                return redirect('home')  # Redirect to a success URL
            else:
                messages.error(request,'Invalid email or password')
                return render(request, 'login.html',{})
        else:
            # Handle GET request (displaying the login form)
            return render(request, 'login.html')



@login_required
def logout_user(request):
    request.session.flush()
    request.session.set_expiry(0)
    logout(request)
    messages.success(request, "Vous vous êtes déconnecté.")
    response = redirect('login_user')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


def apropos(request):
    current_tab="apropos"
    return render(request,'apropos.html',{
        'current_tab':current_tab
    })


def contacteznous(request):
     current_tab="contact"
     return render(request,'contacteznous.html',{
          'current_tab':current_tab
     })
 
 
 
 
def afficher_ouvrage(request,foo):
    ouvrage=Ouvrage.objects.get(ISBN=foo)
    print(ouvrage)
    if is_Staff(request) :
        return render(request,'afficher_ouvrage_staff.html',{
            'ouvrage':ouvrage
        })
    else :
        return render(request,'afficher_ouvrage.html',{
        'ouvrage':ouvrage
    })
    



# def register_user(request):
#     form = SignUpForm()
#     if request.method == "POST":
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             #user = form.save()
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password1']
#             email=form.cleaned_data['email']
#             nom=form.cleaned_data['nom']
#             prenom=form.cleaned_data['prenom']
#             telephone=form.cleaned_data['telephone']
#             image_data = request.POST.get('image')  
#             role=request.POST.get('role')
#             #email, username, password, nom, prenom, telephone,role='UTILISATEUR',**extra_fields):
#             if role == 'UTILISATEUR':
#                 user = Utilisateur.objects.create_user(email,username,password,nom,prenom,telephone,'UTILISATEUR')
#             elif role == 'BIBLIOTHECAIRE':
#                 user = Bibliothecaire.objects.create_user(email,username,password,nom,prenom,telephone,'BIBLIOTHECAIRE')
#             elif role == 'ADMINSUP':
#                 user = AdminSup.objects.create_superuser(email,username,password,nom,prenom,telephone,'ADMINSUP')
        
#             user.save()
#             user = authenticate(request, email=email, password=password)
#             print(user)
#             if user is not None:
                
#                 login(request, user)
#                 messages.success(request, "Vous vous êtes inscrit avec succès.")
#                 return redirect('home') 
#             else:
#                 messages.error(request, "Erreur dans l'authentification")
#                 return redirect('home') 
#                 #messages.error(request, "Échec de l'authentification de l'utilisateur après l'inscription.")
#         else:
            
#             for field, errors in form.errors.items():
#                 for error in errors:
#                     messages.error(request, f"Erreur dans {field}: {error}")
#     return render(request, 'register.html', {'form': form})

class RegisterView(View):
    form_class = SignUpForm

    @method_decorator(sensitive_variables('request'))
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, 'register.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            #user = form.save()
            password = form.cleaned_data['password1']
            email=form.cleaned_data['email']
            nom=form.cleaned_data['nom']
            prenom=form.cleaned_data['prenom']
            telephone=form.cleaned_data['telephone']
            image_data = request.POST.get('image')  
            role='UTILISATEUR'
            user = Utilisateur.objects.create_user(email,password,nom,prenom,telephone,role,image_data)

            user.save()
            user = authenticate(request, email=email, password=password)
            print(user)
            if user is not None:
                login(request, user)
                messages.success(request, "Vous vous êtes inscrit avec succès.")
                return redirect('home') 
            else:
                messages.error(request, "Erreur dans l'authentification")
                return redirect('home') 
                #messages.error(request, "Échec de l'authentification de l'utilisateur après l'inscription.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans {field}: {error}")
        return render(request, 'register.html', {'form': form})
    

class RegisterAdminView(View):
    form_class = SignUpForm

    @method_decorator(sensitive_variables('request'))
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, 'register.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            nom = form.cleaned_data['nom']
            prenom = form.cleaned_data['prenom']
            telephone = form.cleaned_data['telephone']
            image_data = request.POST.get('image')
            role = 'ADMINSUP'  # Assuming this is the role based on your logic
            user = None
            if role == 'UTILISATEUR':
                user = Utilisateur.objects.create_user(email, password, nom, prenom, telephone, 'UTILISATEUR', image_data)
            elif role == 'ADMINSUP':
                # user = Bibliothecaire.objects.create_user(email, password, nom, prenom, telephone, 'BIBLIOTHECAIRE', image_data)
                # Assuming AdminSup.save(user) is not needed

                # Create superuser if needed
                user = PersonneManager.create_superuser(PersonneManager, email=email, nom=nom, prenom=prenom, password=password)
            
            # Authenticate and login user
            user = authenticate(request, email=email, password=password)
            if user is not None:
                user.save()
                login(request, user)
                messages.success(request, "Vous vous êtes inscrit avec succès.")
                return redirect('home')
            else:
                messages.error(request, "Erreur dans l'authentification")
                return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Erreur dans {field}: {error}")

        return render(request, 'register.html', {'form': form})


    
class GererReservations(View):

    @method_decorator(sensitive_variables('request'))
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated and not request.user.role=='UTILISATEUR':
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        try:
            reservations=Reservation.objects.filter(id_utilisateur=request.user.id)
            return render(request,'gerer_reservations.html',{
                "reservations":reservations
            })
        except Exception as e:
            messages.error(request,e)
            return render(request,"accueil.html")

class AnnulerReservations(View):

    @method_decorator(sensitive_variables('request'))
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated and not request.user.role=='UTILISATEUR':
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            if request.user.is_authenticated:
                ouvrage_isbn = request.POST.get('ouvrage_isbn')
                try:
                    ouvrage = Ouvrage.objects.get(ISBN=ouvrage_isbn)
                    # Assuming there can be multiple reservations for the same book
                    reservations = Reservation.objects.filter(ouvrage=ouvrage)
                    if reservations.exists():
                        # Delete all reservations for the given book
                        reservations.delete()
                        messages.success(request, "Les réservations ont été annulées avec succès.")
                        return redirect("gerer")
                    else:
                        messages.error(request, "Aucune réservation trouvée pour cet ouvrage.")
                except Ouvrage.DoesNotExist:
                    messages.error(request, "L'ouvrage n'a pas été trouvé.")
            else:
                messages.error(request, "Vous devez vous connecter d'abord.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', reversed('home')))



class GererEmptunts(View):

    @method_decorator(sensitive_variables('request'))
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated and not request.user.role=='UTILISATEUR':
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        emprunts=Emprunter.objects.filter(utilisateur=request.user)
        return render(request, 'emprunts_user.html', {
            'emprunts':emprunts
        })
    
    
class SignalerPerte(View):
        
    @method_decorator(sensitive_variables('request'))
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated and not request.user.role=='UTILISATEUR':
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
            if request.POST.get('action') == 'post':
                
                exemplaire_id = int(request.POST.get('exemplaire_id'))
                print(exemplaire_id)
                try:
                    exemplaire=Exemplaire.objects.get(id_ex=exemplaire_id)
                    user=Utilisateur.objects.get(id=request.user.id)
                    if user.signaler_perte(exemplaire):
                        messages.warning(request,"Votre Exemplaire est signlé perdu, Vous devez passer chez le bibliothécaire")
                        return redirect('home')
                    else:
                        messages.error(request,"Un prblème lore de signalisation de Perte")
                        return redirect('home')
                            
                except Ouvrage.DoesNotExist:
                    messages.error(request, 'L\'exemplaire spécifié n\'existe pas.')
                    return redirect('home')

class SignalerDeterioration(View):
    @method_decorator(sensitive_variables('request'))
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated and not request.user.role=='UTILISATEUR':
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
            if request.POST.get('action') == 'post':
                
                exemplaire_id = int(request.POST.get('exemplaire_id'))
                try:
                    exemplaire=Exemplaire.objects.get(id_ex=exemplaire_id)
                    user=Utilisateur.objects.get(id=request.user.id)
                    if user.signaler_deterioration(exemplaire):
                        messages.warning(request,"Votre Exemplaire est signlé détérioré , Vous devez passer chez le bibliothécaire")
                        print("done")
                        return redirect('home')
                    else:
                        messages.error(request,"Un prblème lore de signalisation de détériration ")
                        return redirect('home')
                            
                except Ouvrage.DoesNotExist:
                    messages.error(request, 'L\'exemplaire spécifié n\'existe pas.')
                    return redirect('home')
                
class UpdateUser(View):
    @method_decorator(sensitive_variables('request'))
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated :
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            current_user = Personne.objects.get(email=request.user.email)
            if request.user.role =="UTILISATEUR" :
                current_user = Utilisateur.objects.get(email=current_user.email)
            elif request.user.role =="BIBLIOTHECAIRE" :
                current_user = Bibliothecaire.objects.get(email=current_user.email)
            user_form = UpdateUserForm(instance=current_user)
            if is_Staff(request) :
                return render(request, "update_profile_staff.html", {'user_form': user_form})
            else :
                return render(request, "update_profile.html", {'user_form': user_form})
        else:
            messages.error(request, "Vous devez vous authentifier ")
            return redirect('home')
    
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            current_user = Personne.objects.get(email=request.user.email)
            if request.user.role =="UTILISATEUR" :
                current_user = Utilisateur.objects.get(email=current_user.email)
            elif request.user.role =="BIBLIOTHECAIRE" :
                current_user = Bibliothecaire.objects.get(email=current_user.email)
            user_form = UpdateUserForm(request.POST or None, instance=current_user)
            if user_form.is_valid():
                user_form.save()
                login(request, current_user)
                messages.success(request, "Profile est mis à jour")
                return redirect('home')
            if is_Staff(request) :
                return render(request, "update_profile_staff.html", {'user_form': user_form})
            else :
                return render(request, "update_profile.html", {'user_form': user_form})
        else:
            messages.error(request, "Vous devez vous authentifier ")
            return redirect('home')
        
class UpdatePswd(View):
    @method_decorator(sensitive_variables('request'))
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated :
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            current_user = Personne.objects.get(email=request.user.email)
            if request.user.role =="UTILISATEUR" :
                current_user = Utilisateur.objects.get(email=current_user.email)
            elif request.user.role =="BIBLIOTHECAIRE" :
                current_user = Bibliothecaire.objects.get(email=current_user.email)
            user_form = ChangePasswordForm(user=current_user)
            if is_Staff(request) :
                return render(request, "update_pswd_staff.html", {'form': user_form})
            else :
                return render(request, "update_pswd.html", {'form': user_form})
        else:
            messages.error(request, "Vous devez vous authentifier ")
            return redirect('home')
    
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            current_user=request.user
            if request.method =='POST':
                form=ChangePasswordForm(current_user,request.POST)
                
                # if the form valid
                
                if form.is_valid():
                    form.save()
                    messages.success(request,"Votre mot de passe est changé avec succès ")
                    login(request,current_user)
                    return redirect('home')
                else:
                    for error in form.errors.items:
                        messages.error(error)
                        return redirect('home')
            else:
                form=ChangePasswordForm(current_user)
                return render(request,'update_pswd.html',{
                    'form':form
                })
        else:
            messages.error(request,"You must be logged in ")
            return redirect('home')
        
@login_required
@require_POST
def prolonger_date_retour(request):
    id_emprunt = request.POST.get('id_emprunt')
    new_return_date_str = request.POST.get('new_return_date')
    
    emprunt = Emprunter.objects.get(id_emprunt=id_emprunt)
    max_allowed_return_date = (emprunt.date_retour + timedelta(days=6)).date()
    new_return_date = datetime.strptime(new_return_date_str, '%Y-%m-%d').date()
    
    if new_return_date > max_allowed_return_date:
        messages.warning(request,"Vous ne pouvez pas prolonger l'emprunt plus de 6 jours")
        return JsonResponse({'message': "Vous ne pouvez pas prolonger l'emprunt plus de 6 jours"})
    
    if emprunt.num_extensions>1:
        messages.warning(request,"Vous avez dépassé le nombre de prolongations autorisées")
        return JsonResponse({'message': "Vous avez dépassé le nombre de prolongations autorisées"})
    emprunt.num_extensions=emprunt.num_extensions+1
    emprunt.date_retour = new_return_date
    emprunt.save()
    
    # Create a notification for adherents
    biblios = Bibliothecaire.objects.all()
    message = f"L'utilisateur {request.user.email} a prolongé la date de retour pour l'emprunt {emprunt.id_emprunt} jusqu'au {new_return_date}"
    for biblio in biblios:
        Notification.objects.create(user=biblio, message=message)
    messages.success(request,f"La date de retour est prolongée avec succès jusqu'au {new_return_date}")
    return JsonResponse({'message': f"La date de retour est prolongée avec succès jusqu'au {new_return_date}"})




@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(read=False)
    return render(request, 'notifications.html', {'notifications': notifications})

@login_required
def mark_notification_as_read(request, notification_id):
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.read = True
        notification.save()
        return redirect('notifications_view')
    except Notification.DoesNotExist:
        messages.error(request, "Notification does not exist or you do not have permission to access it.")
        return redirect('notifications_view')
    except Exception as e:
        messages.error(request, str(e))
        return redirect('notifications_view')
    

@login_required
def exemplaires(request):
    print('katchaw')
    exemplaires = Exemplaire.objects.all()
    ouvrages = Ouvrage.objects.all()
    paginator = Paginator(exemplaires, 10)  # Show 10 categories per page

    page_number = request.GET.get('page')
    exemplaires_list = paginator.get_page(page_number)
    return render(request, 'exemplaires.html', {'exemplaires':exemplaires_list ,'ouvrages': ouvrages})