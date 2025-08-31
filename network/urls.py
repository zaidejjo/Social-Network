
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("profile/<str:username>/follow", views.toggle_follow,name="toggle_follow"),
    path("following", views.following, name="following"),
    path("post/<int:post_id>", views.post_api, name="post_api"),
    path("api/posts/<int:post_id>/like/", views.like_api, name="like_api"),


]
