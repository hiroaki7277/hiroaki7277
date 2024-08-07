from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import SignUpForm, UserProfileForm, PostForm, CommentForm
from .models import Profile, Post, Comment, Like
from django.contrib.auth import logout
from django.shortcuts import render
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Post, Comment, Like
import logging
from .models import Profile
from .decorators import check_department_and_position


User = get_user_model()
logger = logging.getLogger(__name__)


def home(request):
    logger.error('Rendering home.html template')
    return render(request, 'portal/home.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'アカウントを有効化してください'
            message = render_to_string('portal/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            send_mail(mail_subject, message, 'noreply@yourcompany.com', [to_email])
            return render(request, 'portal/signup_email_sent.html')
    else:
        form = SignUpForm()
    return render(request, 'portal/signup.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'portal/account_activated.html')
    else:
        return render(request, 'portal/activation_invalid.html')

def logout_view(request):
    logout(request)
    return redirect('portal:home')  # または 'portal:login'

@login_required
def profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('portal:profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'portal/profile.html', {'form': form})

@login_required
def chat_room(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
        return redirect('portal:chat_room')

    form = PostForm()
    posts = Post.objects.all().order_by('-created_at')
    comments = Comment.objects.filter(post__in=posts).order_by('created_at')
    comment_form = CommentForm()
    return render(request, 'portal/chat_room.html', {
        'posts': posts,
        'comments': comments,
        'form': form,
        'comment_form': comment_form
    })

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    return redirect('portal:chat_room')


@login_required
def add_reply(request, post_id, parent_id):
    post = get_object_or_404(Post, id=post_id)
    parent_comment = get_object_or_404(Comment, id=parent_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.parent = parent_comment
            comment.save()
    return redirect('portal:chat_room')


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
    return JsonResponse({'likes_count': post.like_set.count()})


@login_required
@require_POST
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return JsonResponse({'error': '権限がありません。'}, status=403)

    try:
        data = json.loads(request.body)
        content = data.get('content')
    except json.JSONDecodeError:
        content = request.POST.get('content')

    if content:
        post.content = content
        post.save()
        return JsonResponse({'success': True, 'content': post.content})

    return JsonResponse({'error': '無効なリクエストです。'}, status=400)

@require_POST
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return JsonResponse({'error': '権限がありません。'}, status=403)

    post.delete()
    return JsonResponse({'success': True})


@login_required
@require_POST
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return JsonResponse({'error': '権限がありません。'}, status=403)

    try:
        data = json.loads(request.body)
        content = data.get('content')
    except json.JSONDecodeError:
        content = request.POST.get('content')

    if content:
        comment.content = content
        comment.save()
        return JsonResponse({'success': True, 'content': comment.content})

    return JsonResponse({'error': '無効なリクエストです。'}, status=400)


@login_required
@require_POST
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return JsonResponse({'error': '権限がありません。'}, status=403)

    post.delete()
    return JsonResponse({'success': True})


@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return JsonResponse({'error': '権限がありません。'}, status=403)

    comment.delete()
    return JsonResponse({'success': True})


@login_required
def like_item(request, item_type, item_id):
    # この関数は Ajax リクエストを処理するだけになります
    # 実際のいいね処理は WebSocket で行われます
    return JsonResponse({'success': True})
