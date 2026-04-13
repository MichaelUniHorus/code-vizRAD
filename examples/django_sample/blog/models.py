"""Blog models showing Django pattern."""

from django.db import models


class Post(models.Model):
    """Blog post model."""

    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey('User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    """Comment model."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey('User', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
