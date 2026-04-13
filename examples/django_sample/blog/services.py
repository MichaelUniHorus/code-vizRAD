"""Business logic layer."""

from blog.models import Post, Comment


class PostService:
    """Service for post operations."""

    def get_popular_posts(self, limit: int = 10):
        """Get most commented posts."""
        return Post.objects.annotate(
            comment_count=models.Count('comment')
        ).order_by('-comment_count')[:limit]

    def create_comment(self, post_id: int, author_id: int, text: str):
        """Create comment on post."""
        post = Post.objects.get(id=post_id)
        Comment.objects.create(
            post=post,
            author_id=author_id,
            text=text,
        )
