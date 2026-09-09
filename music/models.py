from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q


# ============================================================
# BASE MODEL
# ============================================================

class TimeStampedModel(models.Model):
    """
    Abstract base model providing creation and update timestamps.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# ============================================================
# GENRE
# ============================================================

class Genre(TimeStampedModel):
    """
    Music genre/category.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    slug = models.SlugField(
        max_length=120,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(
                fields=["is_active", "name"],
            ),
        ]

    def __str__(self):
        return self.name


# ============================================================
# ARTIST
# ============================================================

class Artist(TimeStampedModel):
    """
    Artist/performer profile used throughout VibeNation.

    IMPORTANT:
    Artists are catalog/editorial entities only.
    They do NOT have Django user accounts.

    A VibeNation user can follow an Artist through ArtistFollow,
    but the Artist itself is not a User.
    """

    name = models.CharField(
        max_length=200,
    )

    slug = models.SlugField(
        max_length=220,
        unique=True,
    )

    bio = models.TextField(
        blank=True,
    )

    profile_image = models.ImageField(
        upload_to="artists/profile/",
        blank=True,
        null=True,
    )

    banner_image = models.ImageField(
        upload_to="artists/banners/",
        blank=True,
        null=True,
    )

    country = models.CharField(
        max_length=100,
        blank=True,
    )

    website_url = models.URLField(
        blank=True,
    )

    instagram_url = models.URLField(
        blank=True,
    )

    x_url = models.URLField(
        blank=True,
    )

    youtube_url = models.URLField(
        blank=True,
    )

    spotify_url = models.URLField(
        blank=True,
    )

    apple_music_url = models.URLField(
        blank=True,
    )

    is_verified = models.BooleanField(
        default=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    # Fast-read follower counter.
    # Source of truth remains ArtistFollow.
    followers_count = models.PositiveBigIntegerField(
        default=0,
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(
                fields=["name"],
            ),
            models.Index(
                fields=["is_active", "name"],
            ),
            models.Index(
                fields=["is_verified", "name"],
            ),
        ]

    def __str__(self):
        return self.name


# ============================================================
# ALBUM
# ============================================================

class Album(TimeStampedModel):
    """
    Album, EP, mixtape, compilation, etc.

    VibeNation does not host downloadable audio.
    """

    class ReleaseType(models.TextChoices):
        ALBUM = "album", "Album"
        EP = "ep", "EP"
        MIXTAPE = "mixtape", "Mixtape"
        COMPILATION = "compilation", "Compilation"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    title = models.CharField(
        max_length=250,
    )

    slug = models.SlugField(
        max_length=280,
        unique=True,
    )

    artists = models.ManyToManyField(
        Artist,
        related_name="albums",
    )

    release_type = models.CharField(
        max_length=20,
        choices=ReleaseType.choices,
        default=ReleaseType.ALBUM,
    )

    artwork = models.ImageField(
        upload_to="albums/artwork/",
        blank=True,
        null=True,
    )

    release_date = models.DateField(
        blank=True,
        null=True,
    )

    description = models.TextField(
        blank=True,
    )

    # --------------------------------------------------------
    # Editorial review
    # --------------------------------------------------------

    editorial_review = models.TextField(
        blank=True,
    )

    editorial_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="reviewed_albums",
    )

    reviewed_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    # --------------------------------------------------------
    # Official listening destinations
    # --------------------------------------------------------

    spotify_url = models.URLField(
        blank=True,
    )

    apple_music_url = models.URLField(
        blank=True,
    )

    youtube_url = models.URLField(
        blank=True,
    )

    audiomack_url = models.URLField(
        blank=True,
    )

    boomplay_url = models.URLField(
        blank=True,
    )

    # --------------------------------------------------------
    # Publishing
    # --------------------------------------------------------

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    published_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    is_featured = models.BooleanField(
        default=False,
    )

    # --------------------------------------------------------
    # Engagement
    # --------------------------------------------------------

    favorites_count = models.PositiveBigIntegerField(
        default=0,
    )

    ratings_count = models.PositiveBigIntegerField(
        default=0,
    )

    class Meta:
        ordering = [
            "-release_date",
            "-created_at",
        ]
        indexes = [
            models.Index(
                fields=["status", "-release_date"],
            ),
            models.Index(
                fields=["is_featured", "-release_date"],
            ),
            models.Index(
                fields=["release_type", "status"],
            ),
            models.Index(
                fields=["status", "-published_at"],
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(
                        status="published",
                        published_at__isnull=False,
                    )
                    | ~Q(status="published")
                ),
                name="album_published_requires_date",
            ),
        ]

    def __str__(self):
        return self.title


# ============================================================
# SONG
# ============================================================

class Song(TimeStampedModel):
    """
    Song metadata and editorial/discovery information.

    VibeNation does not host downloadable audio.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    title = models.CharField(
        max_length=250,
    )

    slug = models.SlugField(
        max_length=280,
        unique=True,
    )

    artists = models.ManyToManyField(
        Artist,
        related_name="songs",
    )

    featured_artists = models.ManyToManyField(
        Artist,
        related_name="featured_songs",
        blank=True,
    )

    album = models.ForeignKey(
        Album,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="songs",
    )

    genres = models.ManyToManyField(
        Genre,
        related_name="songs",
        blank=True,
    )

    artwork = models.ImageField(
        upload_to="songs/artwork/",
        blank=True,
        null=True,
    )

    release_date = models.DateField(
        blank=True,
        null=True,
    )

    duration_seconds = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    description = models.TextField(
        blank=True,
    )

    # --------------------------------------------------------
    # Editorial review
    # --------------------------------------------------------

    editorial_review = models.TextField(
        blank=True,
    )

    editorial_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
    )

    production_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
    )

    lyrics_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
    )

    vocals_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
    )

    replay_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
    )

    cultural_impact_score = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(10),
        ],
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="reviewed_songs",
    )

    reviewed_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    # --------------------------------------------------------
    # Official listening destinations
    # --------------------------------------------------------

    spotify_url = models.URLField(
        blank=True,
    )

    apple_music_url = models.URLField(
        blank=True,
    )

    youtube_url = models.URLField(
        blank=True,
    )

    audiomack_url = models.URLField(
        blank=True,
    )

    boomplay_url = models.URLField(
        blank=True,
    )

    # --------------------------------------------------------
    # Publishing
    # --------------------------------------------------------

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    published_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    is_featured = models.BooleanField(
        default=False,
    )

    # --------------------------------------------------------
    # Engagement
    # --------------------------------------------------------

    favorites_count = models.PositiveBigIntegerField(
        default=0,
    )

    ratings_count = models.PositiveBigIntegerField(
        default=0,
    )

    class Meta:
        ordering = [
            "-release_date",
            "-created_at",
        ]
        indexes = [
            models.Index(
                fields=["status", "-release_date"],
            ),
            models.Index(
                fields=["is_featured", "-release_date"],
            ),
            models.Index(
                fields=["album", "status"],
            ),
            models.Index(
                fields=["status", "-published_at"],
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(
                        status="published",
                        published_at__isnull=False,
                    )
                    | ~Q(status="published")
                ),
                name="song_published_requires_date",
            ),
        ]

    def __str__(self):
        return self.title

    @property
    def duration_display(self):
        if self.duration_seconds is None:
            return None

        minutes, seconds = divmod(
            self.duration_seconds,
            60,
        )

        return f"{minutes}:{seconds:02d}"


# ============================================================
# ALBUM TRACK
# ============================================================

class AlbumTrack(TimeStampedModel):
    """
    Explicit relationship between an album and its songs.

    Preserves official track order.
    """

    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name="tracklist",
    )

    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name="album_track_entries",
    )

    track_number = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
        ],
    )

    class Meta:
        ordering = ["track_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["album", "track_number"],
                name="unique_album_track_number",
            ),
            models.UniqueConstraint(
                fields=["album", "song"],
                name="unique_song_per_album",
            ),
        ]

    def __str__(self):
        return (
            f"{self.album.title} - "
            f"{self.track_number}. "
            f"{self.song.title}"
        )


# ============================================================
# SONG RATING
# ============================================================

class SongRating(TimeStampedModel):
    """
    One community rating per user for a song.

    Rating scale: 0.5 - 5.0 stars.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="song_ratings",
    )

    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name="ratings",
    )

    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[
            MinValueValidator(0.5),
            MaxValueValidator(5),
        ],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "song"],
                name="unique_user_song_rating",
            ),
            models.CheckConstraint(
                condition=Q(
                    rating__in=[
                        0.5,
                        1.0,
                        1.5,
                        2.0,
                        2.5,
                        3.0,
                        3.5,
                        4.0,
                        4.5,
                        5.0,
                    ]
                ),
                name="song_rating_half_star",
            ),
        ]
        indexes = [
            models.Index(
                fields=["song", "-created_at"],
            ),
            models.Index(
                fields=["user", "-created_at"],
            ),
        ]

    def __str__(self):
        return f"{self.user} rated {self.song} {self.rating}/5"


# ============================================================
# ALBUM RATING
# ============================================================

class AlbumRating(TimeStampedModel):
    """
    One community rating per user for an album/EP.

    Rating scale: 0.5 - 5.0 stars.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="album_ratings",
    )

    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name="ratings",
    )

    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[
            MinValueValidator(0.5),
            MaxValueValidator(5),
        ],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "album"],
                name="unique_user_album_rating",
            ),
            models.CheckConstraint(
                condition=Q(
                    rating__in=[
                        0.5,
                        1.0,
                        1.5,
                        2.0,
                        2.5,
                        3.0,
                        3.5,
                        4.0,
                        4.5,
                        5.0,
                    ]
                ),
                name="album_rating_half_star",
            ),
        ]
        indexes = [
            models.Index(
                fields=["album", "-created_at"],
            ),
            models.Index(
                fields=["user", "-created_at"],
            ),
        ]

    def __str__(self):
        return f"{self.user} rated {self.album} {self.rating}/5"


# ============================================================
# EDITORIAL ARTICLE
# ============================================================

class EditorialArticle(TimeStampedModel):
    """
    Long-form editorial content written by VibeNation staff.

    An article may concern a song, artist, album/EP,
    or a combination of related music entities.
    """

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    title = models.CharField(
        max_length=300,
    )

    slug = models.SlugField(
        max_length=330,
        unique=True,
    )

    excerpt = models.TextField(
        max_length=500,
        blank=True,
    )

    content = models.TextField()

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="editorial_articles",
    )

    song = models.ForeignKey(
        Song,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="editorial_articles",
    )

    artist = models.ForeignKey(
        Artist,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="editorial_articles",
    )

    album = models.ForeignKey(
        Album,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="editorial_articles",
    )

    genres = models.ManyToManyField(
        Genre,
        blank=True,
        related_name="editorial_articles",
    )

    # --------------------------------------------------------
    # Publishing
    # --------------------------------------------------------

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    published_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    is_featured = models.BooleanField(
        default=False,
    )

    # --------------------------------------------------------
    # Engagement
    # --------------------------------------------------------

    views_count = models.PositiveBigIntegerField(
        default=0,
    )

    likes_count = models.PositiveBigIntegerField(
        default=0,
    )

    comments_count = models.PositiveBigIntegerField(
        default=0,
    )

    class Meta:
        ordering = [
            "-published_at",
            "-created_at",
        ]
        indexes = [
            models.Index(
                fields=["status", "-published_at"],
            ),
            models.Index(
                fields=["author", "-created_at"],
            ),
            models.Index(
                fields=["song", "status"],
            ),
            models.Index(
                fields=["artist", "status"],
            ),
            models.Index(
                fields=["album", "status"],
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(
                        status="published",
                        published_at__isnull=False,
                    )
                    | ~Q(status="published")
                ),
                name="article_published_requires_date",
            ),
        ]

    def __str__(self):
        return self.title


# ============================================================
# COMMUNITY POST
# ============================================================

class CommunityPost(TimeStampedModel):
    """
    User-generated social/community post.

    The actual music reference is stored in CommunityPostTarget.

    The post itself remains independent from the music catalog.
    """

    class Status(models.TextChoices):
        PUBLISHED = "published", "Published"
        HIDDEN = "hidden", "Hidden"
        REMOVED = "removed", "Removed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="community_posts",
    )

    content = models.TextField(
        max_length=5000,
    )

    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(0.5),
            MaxValueValidator(5),
        ],
    )

    # --------------------------------------------------------
    # Engagement
    # --------------------------------------------------------

    views_count = models.PositiveBigIntegerField(
        default=0,
    )

    likes_count = models.PositiveBigIntegerField(
        default=0,
    )

    comments_count = models.PositiveBigIntegerField(
        default=0,
    )

    # --------------------------------------------------------
    # Moderation
    # --------------------------------------------------------

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PUBLISHED,
    )

    is_edited = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["user", "-created_at"],
            ),
            models.Index(
                fields=["status", "-created_at"],
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(rating__isnull=True)
                    | Q(
                        rating__in=[
                            0.5,
                            1.0,
                            1.5,
                            2.0,
                            2.5,
                            3.0,
                            3.5,
                            4.0,
                            4.5,
                            5.0,
                        ]
                    )
                ),
                name="community_post_half_star_rating",
            ),
        ]

    def __str__(self):
        return f"{self.user} - post {self.pk}"


# ============================================================
# COMMUNITY POST TARGET
# ============================================================

class CommunityPostTarget(TimeStampedModel):
    """
    Stable music reference attached to a community post.

    A target references exactly ONE of:

        1. VibeNation Song
        2. VibeNation Album
        3. VibeNation Artist
        4. External music catalog item

    External metadata is snapshotted here when the post is created.

    This means the post remains renderable even if an external
    provider later changes or removes its catalog result.

    No GenericForeignKey is used.
    """

    class TargetType(models.TextChoices):
        SONG = "song", "Song"
        ALBUM = "album", "Album"
        ARTIST = "artist", "Artist"
        EXTERNAL = "external", "External"

    class ExternalProvider(models.TextChoices):
        ITUNES = "itunes", "iTunes / Apple Music"
        SPOTIFY = "spotify", "Spotify"
        MUSICBRAINZ = "musicbrainz", "MusicBrainz"
        OTHER = "other", "Other"

    class ExternalContentType(models.TextChoices):
        SONG = "song", "Song"
        ALBUM = "album", "Album"
        ARTIST = "artist", "Artist"

    post = models.OneToOneField(
        CommunityPost,
        on_delete=models.CASCADE,
        related_name="target",
    )

    target_type = models.CharField(
        max_length=20,
        choices=TargetType.choices,
    )

    # --------------------------------------------------------
    # Internal VibeNation targets
    # --------------------------------------------------------

    song = models.ForeignKey(
        Song,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="community_post_targets",
    )

    album = models.ForeignKey(
        Album,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="community_post_targets",
    )

    artist = models.ForeignKey(
        Artist,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="community_post_targets",
    )

    # --------------------------------------------------------
    # External catalog identity
    # --------------------------------------------------------

    external_provider = models.CharField(
        max_length=30,
        choices=ExternalProvider.choices,
        blank=True,
    )

    external_content_type = models.CharField(
        max_length=20,
        choices=ExternalContentType.choices,
        blank=True,
    )

    external_id = models.CharField(
        max_length=255,
        blank=True,
    )

    # --------------------------------------------------------
    # External metadata snapshot
    # --------------------------------------------------------

    title = models.CharField(
        max_length=300,
        blank=True,
    )

    artist_name = models.CharField(
        max_length=500,
        blank=True,
    )

    album_name = models.CharField(
        max_length=300,
        blank=True,
    )

    artwork_url = models.URLField(
        max_length=1000,
        blank=True,
    )

    preview_url = models.URLField(
        max_length=1000,
        blank=True,
    )

    spotify_url = models.URLField(
        max_length=1000,
        blank=True,
    )

    apple_music_url = models.URLField(
        max_length=1000,
        blank=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(
                fields=["target_type"],
            ),
            models.Index(
                fields=[
                    "external_provider",
                    "external_content_type",
                    "external_id",
                ],
            ),
            models.Index(
                fields=[
                    "external_provider",
                    "external_id",
                ],
            ),
        ]

        constraints = [
            models.CheckConstraint(
                condition=(
                    (
                        Q(
                            target_type="song",
                            song__isnull=False,
                            album__isnull=True,
                            artist__isnull=True,
                            external_provider="",
                            external_content_type="",
                            external_id="",
                        )
                    )
                    |
                    (
                        Q(
                            target_type="album",
                            song__isnull=True,
                            album__isnull=False,
                            artist__isnull=True,
                            external_provider="",
                            external_content_type="",
                            external_id="",
                        )
                    )
                    |
                    (
                        Q(
                            target_type="artist",
                            song__isnull=True,
                            album__isnull=True,
                            artist__isnull=False,
                            external_provider="",
                            external_content_type="",
                            external_id="",
                        )
                    )
                    |
                    (
                        Q(
                            target_type="external",
                            song__isnull=True,
                            album__isnull=True,
                            artist__isnull=True,
                            external_provider__gt="",
                            external_content_type__gt="",
                            external_id__gt="",
                            title__gt="",
                        )
                    )
                ),
                name="valid_community_post_target",
            ),
        ]

    def __str__(self):
        return (
            f"Target for post "
            f"{self.post_id} ({self.target_type})"
        )


# ============================================================
# EDITORIAL ARTICLE LIKE
# ============================================================

class EditorialArticleLike(TimeStampedModel):
    """
    One like per user per editorial article.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="editorial_article_likes",
    )

    article = models.ForeignKey(
        EditorialArticle,
        on_delete=models.CASCADE,
        related_name="likes",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "article"],
                name="unique_user_article_like",
            ),
        ]
        indexes = [
            models.Index(
                fields=["article", "-created_at"],
            ),
            models.Index(
                fields=["user", "-created_at"],
            ),
        ]

    def __str__(self):
        return f"{self.user} liked article {self.article_id}"


# ============================================================
# COMMUNITY POST LIKE
# ============================================================

class CommunityPostLike(TimeStampedModel):
    """
    One like per user per community post.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="community_post_likes",
    )

    post = models.ForeignKey(
        CommunityPost,
        on_delete=models.CASCADE,
        related_name="likes",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                name="unique_user_post_like",
            ),
        ]
        indexes = [
            models.Index(
                fields=["post", "-created_at"],
            ),
            models.Index(
                fields=["user", "-created_at"],
            ),
        ]

    def __str__(self):
        return f"{self.user} liked post {self.post_id}"


# ============================================================
# EDITORIAL COMMENT
# ============================================================

class EditorialComment(TimeStampedModel):
    """
    Comment/reply attached to an editorial article.

    parent=None:
        top-level comment

    parent=<comment>:
        nested reply

    Unlimited nesting is supported.
    """

    class Status(models.TextChoices):
        PUBLISHED = "published", "Published"
        HIDDEN = "hidden", "Hidden"
        REMOVED = "removed", "Removed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="editorial_comments",
    )

    article = models.ForeignKey(
        EditorialArticle,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="replies",
    )

    content = models.TextField(
        max_length=3000,
    )

    # --------------------------------------------------------
    # Engagement
    # --------------------------------------------------------

    views_count = models.PositiveBigIntegerField(
        default=0,
    )

    likes_count = models.PositiveBigIntegerField(
        default=0,
    )

    replies_count = models.PositiveBigIntegerField(
        default=0,
    )

    # --------------------------------------------------------
    # Moderation
    # --------------------------------------------------------

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PUBLISHED,
    )

    is_edited = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(
                fields=[
                    "article",
                    "parent",
                    "status",
                    "created_at",
                ],
            ),
            models.Index(
                fields=[
                    "parent",
                    "status",
                    "created_at",
                ],
            ),
            models.Index(
                fields=[
                    "user",
                    "-created_at",
                ],
            ),
        ]

    def __str__(self):
        return (
            f"{self.user} - "
            f"comment on article {self.article_id}"
        )


# ============================================================
# COMMUNITY POST COMMENT
# ============================================================

class CommunityPostComment(TimeStampedModel):
    """
    Comment/reply attached to a community post.

    parent=None:
        top-level comment

    parent=<comment>:
        nested reply

    Unlimited nesting is supported.
    """

    class Status(models.TextChoices):
        PUBLISHED = "published", "Published"
        HIDDEN = "hidden", "Hidden"
        REMOVED = "removed", "Removed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="community_post_comments",
    )

    post = models.ForeignKey(
        CommunityPost,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="replies",
    )

    content = models.TextField(
        max_length=3000,
    )

    # --------------------------------------------------------
    # Engagement
    # --------------------------------------------------------

    views_count = models.PositiveBigIntegerField(
        default=0,
    )

    likes_count = models.PositiveBigIntegerField(
        default=0,
    )

    replies_count = models.PositiveBigIntegerField(
        default=0,
    )

    # --------------------------------------------------------
    # Moderation
    # --------------------------------------------------------

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PUBLISHED,
    )

    is_edited = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(
                fields=[
                    "post",
                    "parent",
                    "status",
                    "created_at",
                ],
            ),
            models.Index(
                fields=[
                    "parent",
                    "status",
                    "created_at",
                ],
            ),
            models.Index(
                fields=[
                    "user",
                    "-created_at",
                ],
            ),
        ]

    def __str__(self):
        return (
            f"{self.user} - "
            f"comment on post {self.post_id}"
        )


# ============================================================
# EDITORIAL COMMENT LIKE
# ============================================================

class EditorialCommentLike(TimeStampedModel):
    """
    One like per user per editorial comment/reply.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="editorial_comment_likes",
    )

    comment = models.ForeignKey(
        EditorialComment,
        on_delete=models.CASCADE,
        related_name="likes",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "comment"],
                name="unique_user_editorial_comment_like",
            ),
        ]
        indexes = [
            models.Index(
                fields=["comment", "-created_at"],
            ),
            models.Index(
                fields=["user", "-created_at"],
            ),
        ]

    def __str__(self):
        return (
            f"{self.user} liked "
            f"editorial comment {self.comment_id}"
        )


# ============================================================
# COMMUNITY POST COMMENT LIKE
# ============================================================

class CommunityPostCommentLike(TimeStampedModel):
    """
    One like per user per community comment/reply.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="community_comment_likes",
    )

    comment = models.ForeignKey(
        CommunityPostComment,
        on_delete=models.CASCADE,
        related_name="likes",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "comment"],
                name="unique_user_community_comment_like",
            ),
        ]
        indexes = [
            models.Index(
                fields=["comment", "-created_at"],
            ),
            models.Index(
                fields=["user", "-created_at"],
            ),
        ]

    def __str__(self):
        return (
            f"{self.user} liked "
            f"community comment {self.comment_id}"
        )


# ============================================================
# EDITORIAL ARTICLE REPORT
# ============================================================

class EditorialArticleReport(TimeStampedModel):
    """
    User report against an editorial article.
    """

    class Reason(models.TextChoices):
        SPAM = "spam", "Spam"
        HARASSMENT = "harassment", "Harassment"
        HATE = "hate", "Hate Speech"
        SEXUAL = "sexual", "Sexual Content"
        MISINFORMATION = "misinformation", "Misinformation"
        COPYRIGHT = "copyright", "Copyright"
        OTHER = "other", "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="editorial_article_reports",
    )

    article = models.ForeignKey(
        EditorialArticle,
        on_delete=models.CASCADE,
        related_name="reports",
    )

    reason = models.CharField(
        max_length=30,
        choices=Reason.choices,
    )

    details = models.TextField(
        max_length=2000,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "article"],
                name="unique_user_article_report",
            ),
        ]
        indexes = [
            models.Index(
                fields=["article", "-created_at"],
            ),
            models.Index(
                fields=["reason", "-created_at"],
            ),
        ]

    def __str__(self):
        return (
            f"{self.user} reported "
            f"article {self.article_id}"
        )


# ============================================================
# COMMUNITY POST REPORT
# ============================================================

class CommunityPostReport(TimeStampedModel):
    """
    User report against a community post.
    """

    class Reason(models.TextChoices):
        SPAM = "spam", "Spam"
        HARASSMENT = "harassment", "Harassment"
        HATE = "hate", "Hate Speech"
        SEXUAL = "sexual", "Sexual Content"
        MISINFORMATION = "misinformation", "Misinformation"
        COPYRIGHT = "copyright", "Copyright"
        OTHER = "other", "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="community_post_reports",
    )

    post = models.ForeignKey(
        CommunityPost,
        on_delete=models.CASCADE,
        related_name="reports",
    )

    reason = models.CharField(
        max_length=30,
        choices=Reason.choices,
    )

    details = models.TextField(
        max_length=2000,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                name="unique_user_post_report",
            ),
        ]
        indexes = [
            models.Index(
                fields=["post", "-created_at"],
            ),
            models.Index(
                fields=["reason", "-created_at"],
            ),
        ]

    def __str__(self):
        return (
            f"{self.user} reported "
            f"post {self.post_id}"
        )


# ============================================================
# EDITORIAL COMMENT REPORT
# ============================================================

class EditorialCommentReport(TimeStampedModel):
    """
    User report against an editorial comment/reply.
    """

    class Reason(models.TextChoices):
        SPAM = "spam", "Spam"
        HARASSMENT = "harassment", "Harassment"
        HATE = "hate", "Hate Speech"
        SEXUAL = "sexual", "Sexual Content"
        MISINFORMATION = "misinformation", "Misinformation"
        OTHER = "other", "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="editorial_comment_reports",
    )

    comment = models.ForeignKey(
        EditorialComment,
        on_delete=models.CASCADE,
        related_name="reports",
    )

    reason = models.CharField(
        max_length=30,
        choices=Reason.choices,
    )

    details = models.TextField(
        max_length=2000,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "comment"],
                name="unique_user_editorial_comment_report",
            ),
        ]
        indexes = [
            models.Index(
                fields=["comment", "-created_at"],
            ),
            models.Index(
                fields=["reason", "-created_at"],
            ),
        ]

    def __str__(self):
        return (
            f"{self.user} reported "
            f"editorial comment {self.comment_id}"
        )


# ============================================================
# COMMUNITY POST COMMENT REPORT
# ============================================================

class CommunityPostCommentReport(TimeStampedModel):
    """
    User report against a community comment/reply.
    """

    class Reason(models.TextChoices):
        SPAM = "spam", "Spam"
        HARASSMENT = "harassment", "Harassment"
        HATE = "hate", "Hate Speech"
        SEXUAL = "sexual", "Sexual Content"
        MISINFORMATION = "misinformation", "Misinformation"
        OTHER = "other", "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="community_comment_reports",
    )

    comment = models.ForeignKey(
        CommunityPostComment,
        on_delete=models.CASCADE,
        related_name="reports",
    )

    reason = models.CharField(
        max_length=30,
        choices=Reason.choices,
    )

    details = models.TextField(
        max_length=2000,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "comment"],
                name="unique_user_community_comment_report",
            ),
        ]
        indexes = [
            models.Index(
                fields=["comment", "-created_at"],
            ),
            models.Index(
                fields=["reason", "-created_at"],
            ),
        ]

    def __str__(self):
        return (
            f"{self.user} reported "
            f"community comment {self.comment_id}"
        )


# ============================================================
# SONG FAVORITE
# ============================================================

class SongFavorite(TimeStampedModel):
    """
    Save/favorite a song.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_songs",
    )

    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name="favorites",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "song"],
                name="unique_user_song_favorite",
            ),
        ]
        indexes = [
            models.Index(
                fields=["song", "-created_at"],
            ),
            models.Index(
                fields=["user", "-created_at"],
            ),
        ]

    def __str__(self):
        return f"{self.user} saved {self.song}"


# ============================================================
# ALBUM FAVORITE
# ============================================================

class AlbumFavorite(TimeStampedModel):
    """
    Save/favorite an album or EP.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorite_albums",
    )

    album = models.ForeignKey(
        Album,
        on_delete=models.CASCADE,
        related_name="favorites",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "album"],
                name="unique_user_album_favorite",
            ),
        ]
        indexes = [
            models.Index(
                fields=["album", "-created_at"],
            ),
            models.Index(
                fields=["user", "-created_at"],
            ),
        ]

    def __str__(self):
        return f"{self.user} saved {self.album}"


# ============================================================
# ARTIST FOLLOW
# ============================================================

class ArtistFollow(TimeStampedModel):
    """
    User follows an Artist catalog entity.

    IMPORTANT:
    Artist is NOT a Django User and does NOT have an account.

    The user field is the VibeNation user doing the following.
    The artist field points to the VibeNation Artist record.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="artist_follows",
    )

    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name="followers",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "artist"],
                name="unique_user_artist_follow",
            ),
        ]
        indexes = [
            models.Index(
                fields=["artist", "-created_at"],
            ),
            models.Index(
                fields=["user", "-created_at"],
            ),
        ]

    def __str__(self):
        return f"{self.user} follows {self.artist}"


# ============================================================
# USER FOLLOW
# ============================================================

class UserFollow(TimeStampedModel):
    """
    User-to-user follow relationship.

    follower:
        User doing the following.

    following:
        User being followed.
    """

    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following_relationships",
    )

    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="follower_relationships",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"],
                name="unique_user_follow",
            ),
            models.CheckConstraint(
                condition=~Q(
                    follower=F("following")
                ),
                name="prevent_self_follow",
            ),
        ]
        indexes = [
            models.Index(
                fields=["follower", "-created_at"],
            ),
            models.Index(
                fields=["following", "-created_at"],
            ),
        ]

    def __str__(self):
        return (
            f"{self.follower} follows "
            f"{self.following}"
        )