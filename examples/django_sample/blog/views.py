"""Blog views showing Django pattern."""

from django.shortcuts import render
from django.http import HttpResponse
from blog.models import Post, Comment
from blog.services import PostService
from blog.forms import PostForm


def post_list(request):
    """List all posts."""
    posts = Post.objects.all()
    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, post_id):
    """Show single post with comments."""
    post = Post.objects.get(id=post_id)
    comments = post.comment_set.all()
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
    })


def create_post(request):
    """Create new post."""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm()
    return render(request, 'blog/post_form.html', {'form': form})
