from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .utils import profanity_censor, is_nsfw, blur_image
from .models import *
from .forms import *

import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
from PIL import Image
from io import BytesIO
import numpy as np
from django.core.files.base import ContentFile
# ---------Homepage----------#
@login_required
def home(request):
    posts = Post.objects.all().order_by('?')[:5]
    comment_form = CommentForm()
    users = CustomUser.objects.exclude(id=request.user.id).order_by('?')[:6]
    unread_notifications = Notification.objects.filter(user = request.user, is_read = False).exclude(created_by = request.user)
    count = unread_notifications.count()
    

    context = {
        'posts' : posts,
        'comment_form' : comment_form,
        'users' : users,
        'count' : count,
    }
    return render(request, 'home.html', context)
# ---------Homepage End----------#

def serialize_comment(comment):
    return {
        'pk': comment.pk,
        'author_username': comment.author.username,
        'user_image': comment.author.image.url if comment.author.image else None,
        'censored_text': comment.censored_text,
    }

# -----------Add Comment----------------------#
def add_comment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.author = request.user
            new_comment.post_id = post_id
            new_comment.censored_text = profanity_censor(new_comment.text)
            new_comment.save()
            
            comments = post.comments.all()
            serialized_comments = [serialize_comment(comment) for comment in comments]
            return JsonResponse({'comments': serialized_comments})
        else:
            errors = comment_form.errors.as_json()
            return JsonResponse({'errors': errors}, status=400)        
        
    else:
        return JsonResponse({'error' : 'Invalid Request'}, status = 405)
#-----------------Add Comment End---------------------------#

# -------------Login View------------#
def login_page(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        print("Email: ", email)
        print("Password: ", password)
        

        user = authenticate(email = email, password = password)
        print(user)
        if user is not None:
            login(request, user)
            return redirect('home')
        else: 
            messages.info(request, 'Invalid Email or Password')
            return redirect('login')
    else:
        return render(request, 'login.html')

 
# -------------Login View End------------#

# ----------Logout--------------#
@login_required
def logout_page(request):
    logout(request)
    return redirect('login')

# ----------Logout End--------------#


# -------------Register View------------#

def register_page(request):

    User = get_user_model()

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password')

        print("Email: ", email)
        print("Password: ", pass1)

        
        if User.objects.filter(username = username).exists():
            messages.info(request, "Username already exists!")
            return redirect('register')
        elif User.objects.filter(email = email):
            messages.info(request, "Email already exists.")
            return redirect('register')
        else:
            User.objects.create_user(username=username, email=email, password=pass1)
            messages.success(request, f"User {username} successfully registered")
            return redirect('login')
    return render(request, 'register.html')
# -------------Register View End------------#


# ---------------Profile Page---------------------#
@login_required
def profile_page(request, pk):
    user = get_object_or_404(CustomUser, id=pk)
    posts = Post.objects.filter(author = user)
    following = Follow.objects.filter(follower = request.user, following = user)
    if following:
        is_following = True
    else:
        is_following = False
    context = {
        "posts" : posts,
        'user' : user,
        'is_following' : is_following
    }
    return render(request, "profile.html", context)

# ---------------Profile Page End---------------------#

#------------------Create Post-----------------#
@login_required
def create_post(request):
    user = request.user
    if request.method == "POST":
        create_post = CreatePostForm(request.POST, request.FILES)
        if create_post.is_valid():
            new_post = create_post.save(commit=False)
            new_post.author = request.user

            if 'image' in request.FILES:
                image_file = request.FILES['image']
                image_data = image_file.read()
                img = Image.open(BytesIO(image_data))  
                img = img.convert('RGB')
                img_array  =np.array(img)
                if is_nsfw(img_array):
                    blurred_img_array = blur_image(img_array)
                    print(blurred_img_array)
                    blurred_img = Image.fromarray(blurred_img_array.astype('uint8'))
                    print(blurred_img)
                    buffer = BytesIO()
                    blurred_img.save(buffer, format='JPEG')
                    blurred_image_name = f"blurred_{image_file.name}"
                    new_post.blurred_image.save(blurred_image_name, ContentFile(buffer.getvalue()), save=False)

            new_post.save()
            return redirect('profile', user.id)
    else:
        create_post = CreatePostForm()


    context = {
        'create_post' : create_post
    }
    return render(request, 'create_post.html', context)

#------------------Create Post End-----------------#


#------------------Edit Post--------------------------#

def edit_post(request, postid):
    post = get_object_or_404(Post, id = postid)
    if request.method == "POST":
        form = EditPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('profile', request.user.id)
    else:
        form = EditPostForm(instance=post)

    context = {
        'post' : post,
        'form' : form
    }
    return render(request, 'edit_post.html', context)


#------------------Edit Post End--------------------------#


#------------------Delete Post-----------------#
def delete_post(request, postid):
    if request.method == "POST":
        post = get_object_or_404(Post, id = postid)
        post.delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})



#------------------Delete Post End-----------------#


#------------------Like Counter----------------#
@login_required
def like_count(request):
    user = request.user
    if request.method == "POST":
        postid = request.POST.get('id')
        print("User = ", user.username)
        print("postid = ",postid)
        post = get_object_or_404(Post, id=postid)
        liked_user = post.author
        likes_user = get_object_or_404(CustomUser, email = user)
        likes_who = likes_user.first_name
        print("Previous like = ",post.likes.count())
        if not user in post.likes.all():
            post.likes.add(user)
            message = 'Post liked successfully.'
            liked = True
            message = f'{likes_who} likes your post'
            Notification.objects.create(user = liked_user, message=message, created_by = request.user)
        else:
            post.likes.remove(user)
            message = 'Post unliked successfully.'
            liked = False
            message = f'{likes_who} unlikes your post'
            Notification.objects.create(user = liked_user, message=message, created_by = request.user)
        print("After like = ",post.likes.count())
        
        post.save()

        return JsonResponse({'message':message, 'liked': liked})
    return JsonResponse({"error": "Invalid Request"})
#------------------Like Counter End----------------#


#--------------Notification-----------------------------#
@login_required
def notification(request):
    '''
    Notification Page View
    '''
    unread_notification = Notification.objects.filter(user = request.user, is_read=False).exclude(created_by = request.user)
    read_notifications = Notification.objects.filter(user = request.user, is_read=True).exclude(created_by = request.user)
    count = unread_notification.count()
    
    context = {
        'unread_notification' : unread_notification,
        'count' : count,
        'read_notifications' : read_notifications,
        }
    return render(request, 'notification.html', context)


#--------------Notification End-----------------------------#

#---------------Remove Notification----------------#
@login_required
def remove_notification(request, id):
    if request.method == "POST":
        notification = get_object_or_404(Notification, id=id)
        notification.delete()
        return redirect("notification")
    
#---------------Remove Notification End----------------#

#--------------Notification Mark As Read----------------#
@login_required
def mark_as_read(request, id):
    if request.method == "POST":
        notification = get_object_or_404(Notification, id=id)
        notification.is_read = True
        notification.save()
        return JsonResponse({"success" : "Notification Marked as read.."})
    return JsonResponse({"error" : "Invalid Request"})

#--------------Notification Mark As Read End----------------#

#-------------Clear All UnRead Notifications---------------------#

def clear_all_unread_notifications(request):
    if request.method == "POST":
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
        unread_notifications.delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})

#-------------Clear All UnRead Notifications End---------------------#


#-------------Clear All Read Notifications---------------------#

def clear_all_read_notifications(request):
    if request.method == "POST":
        read_notifications = Notification.objects.filter(user = request.user, is_read = True)
        read_notifications.delete()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})

#-------------Clear All Read Notifications End---------------------#

#---------------------Follow User-----------------------------#

def follow_user(request, userid):
    if request.method == "POST":
        user_to_follow = get_object_or_404(CustomUser, id=userid)
        user = request.user
        
        follow_instance, created = Follow.objects.get_or_create(follower = user, following = user_to_follow)

        if created:
            Notification.objects.create(user = user_to_follow, message = f'{user.first_name} follows you!')
        else:
            follow_instance.delete()
            Notification.objects.create(user = user_to_follow, message = f'{user.first_name} unfollows you!')

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid Request'})

#---------------------Follow User End-----------------------------#

#--------------------Search Users---------------------------------#

def search_user(request, user):
    if request.method == "GET":
        users = CustomUser.objects.filter(username__startswith = user)
        users_list = list(users.values())
        return JsonResponse({'users' : users_list})
#--------------------Search Users End---------------------------------#

#--------------------Comment---------------------------------#

# def comment(request, post_id):
#     author = request.user
#     post = get_object_or_404(Post, id = post_id)
#     if request.method == "POST":
#         text = request.POST.get('text')

#         try:
#             comment = Comment(post = post, author = author, text = text)
#             comment.save()
#         except ValidationError as e:
#             context = {
#                 'post' : post,
#                 'error_message': str(e)
#             }
#             return JsonResponse(context)
#         return HttpResponse("Worked!!")


#--------------------Comment End---------------------------------#
