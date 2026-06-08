from django.db import models
from django.conf import settings

class BaseComment(models.Model):
    # Secure Auth Link — ONLY populated for logged-in backend staff
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_auth_comments"
    )
    
    # Self-referential link handling your premium deep-nesting threads
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )

    # Legacy visitor text field fallback
    name = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['created_at'] # Clean ascending order for conversational flows

    @property
    def display_name(self):
        if self.user and self.user.is_staff:
            return self.user.get_full_name() or self.user.username
        return self.name or "Anonymous Fan"

    @property
    def root_comment(self):
        obj = self
        while obj.parent:
            obj = obj.parent
        return obj

    @property
    def is_verified_staff(self):
        return bool(self.user and self.user.is_staff)

    @property
    def replying_to(self):
        """Looks up parent tier context dynamically checking identity states"""
        if self.parent:
            return self.parent.display_name
        return None

    def get_all_replies(self):
        """
        Your custom flattening algorithm. Aggregates deep child reply vectors 
        into a unified, linear array structure for clean one-level UI indentation.
        """
        all_replies = []

        def collect(comment):
            for reply in comment.replies.all().order_by('created_at'):
                all_replies.append(reply)
                collect(reply)
        collect(self)
        return all_replies

    def __str__(self):
        return self.content[:30]