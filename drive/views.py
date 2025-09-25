import asyncio
import json
from datetime import datetime
from os import getenv
from dotenv import load_dotenv

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse, StreamingHttpResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse
import requests

from cloudinary.uploader import upload as cloud_upload
from .cloudinary_config import cloudinary  # or just import to run the config


from .discord_integration import send_file_to_discord
from .models import File, Share, User
from .utils import file_iterator

load_dotenv()


def index(request):
    if request.user.is_authenticated:
        user_files = File.objects.filter(user=request.user).order_by("-uploaded_at")
        return render(request, "drive/index.html", {"files": user_files})
    return render(request, "drive/index.html")


def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if not len(username) or not len(password):
            return render(request, "drive/login.html", {"message": "Username and password are required!", "username": username})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "drive/login.html", {"message": "Invalid Credentials!", "username": username})

    return render(request, "drive/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("index"))

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        if not all([username, email, password, confirmation]):
            return render(request, "drive/register.html", {"message": "All fields are required!", "username": username, "email": email})

        if password != confirmation:
            return render(request, "drive/register.html", {"message": "Passwords must match!", "username": username, "email": email})

        try:
            validate_password(password)
        except ValidationError as e:
            return render(request, "drive/register.html", {"errors": e.messages, "username": username, "email": email})

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
        except IntegrityError:
            return render(request, "drive/register.html", {"message": "Username already taken!"})
        else:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))

    return render(request, "drive/register.html")


@login_required(login_url="/login")
def upload(request):
    if request.method == "POST" and request.FILES:
        for file in request.FILES.getlist("files"):
            try:
                result = cloud_upload(file, folder=f"user_uploads/user_{request.user.id}")
                file_url = result.get("secure_url")

                f = File(
                    user=request.user,
                    name=file.name,
                    size=file.size,
                    type=file.content_type,
                    path=file_url,
                    access_permissions="Private",
                )
                f.save()

                # Discord integration
                send_file_to_discord(file, request.user.username)

            except Exception as e:
                return render(request, "drive/upload.html", {"error": f"{e}"})

        return HttpResponseRedirect(reverse("index"))

    return render(request, "drive/upload.html")



@login_required(login_url="/login")
def download(request, id):
    try:
        file = File.objects.get(pk=id)
    except File.DoesNotExist:
        return render(request, "drive/404.html", status=404)

    if file.user == request.user or file.access_permissions == "Everyone":
        try:
            # Stream file from Cloudinary
            r = requests.get(file.path, stream=True)
            response = HttpResponse(r.raw, content_type=file.type)
            response['Content-Disposition'] = f'attachment; filename="{file.name}"'
            return response
        except Exception as e:
            return render(request, "drive/404.html", {"error": f"Couldn't open file: {e}"})
    else:
        return render(request, "drive/403.html", status=403)


@login_required(login_url="/login")
def shared_with_me(request):
    return render(request, "drive/shared_with_me.html", {"shared_files": Share.objects.filter(receiver=request.user)})


@login_required(login_url="/login")
def shared(request):
    return render(request, "drive/shared.html", {"shared_files": File.objects.filter(sharing_status=True, user=request.user).order_by("-uploaded_at")})


@login_required(login_url="/login")
def file(request, id):
    if request.method == "DELETE":
        if file := File.objects.filter(pk=id).first():
            if file.user != request.user:
                return JsonResponse({"error": "FORBIDDEN"}, status=403)
            try:
                file.delete()
            except Exception as e:
                return JsonResponse({"error": f"Server Error: {e}"}, status=500)
            else:
                return HttpResponseRedirect(reverse("index"))

        return JsonResponse({"error": "Not Found"}, status=404)

    try:
        file = File.objects.get(pk=id)
    except File.DoesNotExist:
        return render(request, "drive/404.html", status=404)

    if request.user != file.user:
        return render(request, "drive/403.html", status=403)

    return render(request, "drive/file.html", {"file": file})


def shared_with(request, id):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "FORBIDDEN"}, status=403)
    try:
        file = File.objects.get(pk=id)
    except File.DoesNotExist:
        return JsonResponse({"error": "NOT FOUND"}, status=404)

    if request.user != file.user:
        return JsonResponse({"error": "FORBIDDEN"}, status=403)

    usernames = []
    if shared := Share.objects.filter(file=file).first():
        for user in shared.receiver.all():
            usernames.append(user.username)

    return JsonResponse({"usernames": usernames}, status=200)


def manage_access(request, id):
    if request.method in ["PUT", "DELETE", "POST"]:
        body = json.loads(request.body)
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Forbidden"}, status=403)

        try:
            file = File.objects.get(pk=id)
        except File.DoesNotExist:
            return JsonResponse({"error": "NOT FOUND"}, status=404)

        if file.user != request.user:
            return JsonResponse({"error": "Forbidden"}, status=403)

    if request.method == "PUT":
        permission = body.get("permission")
        permissions = ["Private", "Restricted", "Everyone"]
        if permission is None or permission not in permissions:
            return JsonResponse({"error": "Value Error"}, status=400)

        if permission == "Private":
            Share.objects.filter(file=file).delete()
            file.access_permissions = permission
            file.sharing_status = False
            file.save()
            return JsonResponse({"message": "Not Shared"}, status=200)

        elif permission == "Restricted":
            if username := body.get("username"):
                if username == request.user.username:
                    return JsonResponse({"error": "It's your own file."}, status=400)
                try:
                    receiver = User.objects.get(username=username)
                except User.DoesNotExist:
                    return JsonResponse({"error": "Username not found!"}, status=404)
                share, created = Share.objects.get_or_create(file=file, sender=request.user)
                if receiver in share.receiver.all():
                    return JsonResponse({"error": "Already Shared!"}, status=200)
                share.receiver.add(receiver)
            file.access_permissions = permission
            file.sharing_status = True
            file.save()
            return JsonResponse({"message": permission}, status=200)

        elif permission == "Everyone":
            file.access_permissions = permission
            file.sharing_status = True
            file.save()
            return JsonResponse({"message": permission}, status=200)

        return JsonResponse({"error": "Server ERROR"}, status=500)

    elif request.method == "DELETE":
        username = body.get("username")
        user = User.objects.filter(username=username).first()
        share = Share.objects.filter(file=file).first()
        if user and share and user in share.receiver.all():
            share.receiver.remove(user)
            return JsonResponse({"message": f"Access Permissions for {username} removed!"}, status=200)
        return JsonResponse({"error": "Invalid input!"}, status=404)

    return JsonResponse({"error": "POST method required"}, status=400)


@login_required(login_url="/login")
def manage_account(request):
    if request.method == "POST":
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        confirmation = request.POST["confirmation"]

        if not all([current_password, new_password, confirmation]):
            return render(request, "drive/manage_account.html", {"message": "All fields are required!"})

        if new_password != confirmation:
            return render(request, "drive/manage_account.html", {"message": "New passwords must match!"})

        if not request.user.check_password(current_password):
            return render(request, "drive/manage_account.html", {"message": "Current password is incorrect!"})

        try:
            validate_password(new_password, user=request.user)
        except ValidationError as e:
            return render(request, "drive/manage_account.html", {"errors": e.messages})

        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        return HttpResponseRedirect(reverse("index"))

    return render(request, "drive/manage_account.html")


@login_required(login_url="/login")
def delete_account(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation_text = request.POST["confirmation_text"]

        if confirmation_text != "Delete my account!":
            return render(request, "drive/manage_account.html", {"errors": ['Confirmation text does not match. Please type "Delete my account!" exactly.']})

        user = authenticate(request, username=username, password=password)
        if user is not None and user.email == email:
            user.delete()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "drive/manage_account.html", {"errors": ["Invalid credentials. Please try again."]})

    return HttpResponseRedirect(reverse("manage_account"))

@login_required(login_url="/login")
def accessible_files(request):
    # Public files (everyone)
    public_files = File.objects.filter(access_permissions="Everyone").exclude(user=request.user)

    # Files shared specifically with the current user
    restricted_files = File.objects.filter(
        access_permissions="Restricted",
        share__receiver=request.user
    )

    # Combine the querysets
    all_files = public_files | restricted_files
    all_files = all_files.order_by("-uploaded_at")  # latest first

    return render(request, "drive/accessible_files.html", {"files": all_files})



def ping(request):
    return JsonResponse({"msg": "pong", "info": "server is running"})
