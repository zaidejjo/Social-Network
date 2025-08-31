from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render,redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
import json
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Count



from .models import User, Post, Follow
from .forms import PostForm


def index(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.user = request.user
            new_post.save()
            return redirect("index")
    else:
        form = PostForm()

    # جميع البوستات مع عدد اللايكات
    all_posts = Post.objects.annotate(likes_count=Count('likes')).order_by('-timestamp')

    paginator = Paginator(all_posts, 10)  # 10 بوستات لكل صفحة
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    # المعرفات التي أعجب بها المستخدم حالياً
    liked_post_ids = []
    if request.user.is_authenticated:
        liked_post_ids = request.user.liked_posts.values_list('id', flat=True)

    return render(request, "network/index.html", {
        "form": form,
        "posts": posts,
        "liked_post_ids": liked_post_ids,  # لعرض القلب الأحمر إذا أعجب المستخدم بالبوست
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def profile(request, username):
    profile_user = get_object_or_404(User, username=username)

    posts = Post.objects.filter(user=profile_user).order_by('-timestamp')

    followers_count = profile_user.followers.count()
    following_count = profile_user.following.count()

    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()

    context = {
        "profile_user": profile_user,
        "posts": posts,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following
    }
    return render(request, "network/profile.html", context)

@login_required
def toggle_follow(request, username):
    profile_user = get_object_or_404(User, username=username)

    if request.user == profile_user:
        return redirect('profile', username=username)
    
    follow = Follow.objects.filter(follower=request.user, following=profile_user)
    if follow.exists():
        follow.delete()
    else:
        Follow.objects.create(follower=request.user, following=profile_user)
    return redirect('profile', username=username)

@login_required
def following(request):
    following_user = request.user.following.values_list("following", flat=True)

    qs = Post.objects.filter(user__in=following_user).order_by('-timestamp')
    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "posts": posts
    })

@login_required
@require_http_methods(["GET", "PUT"])
def post_api(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == "GET":
        return JsonResponse({
            "id": post.id,
            "user": post.user.username,
            "content": post.content,
            "timestamp": post.timestamp,
            "likes_count": post.likes.count()
        })
    
    if post.user != request.user:
        return JsonResponse({"error":"Not allowed"}, status=403)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest("invalid JSON")
    
    new_content = data.get("content", "").strip()
    if not new_content:
        return JsonResponse({"error": "Content cannot be empty."}, status=400)
    
    post.content = new_content
    post.save()
    return JsonResponse({"message":"Updated", "content": post.content})

from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required


@login_required
def like_api(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    post = get_object_or_404(Post, id=post_id)
    user = request.user

    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True

    return JsonResponse({"liked": liked, "likes_count": post.likes.count()})