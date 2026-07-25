from itertools import chain 
from django.conf import settings
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, Http404, FileResponse
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.db.models import Q, Count, Exists, OuterRef
from django.core.cache import cache
from django.utils import timezone

import re
import shutil
import os
from datetime import timedelta

from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView


from .utils.clean_tags import clean_mp3_tags
from taggit.models import Tag
from music.models import Song, DJ, MusicComment, SongView, Album, Artist
from music.forms import MusicCommentForm
from news.models import News
from utils.monitor_ip import monitor_and_filter_ip
from news.serializers import NewsCardSerializer

from music.serializers import (
    SongPageSerializer,
    SongCardSerializer,
    DJCardSerializer,
    DJPageSerializer,
    MusicCommentSerializer,
    MusicReplySerializer,
    AlbumCardSerializer,
    AlbumDetailSerializer,
    ArtistSerializer,
)

from music.utils.get_media import get_primary_media
from utils.security import get_cloudflare_ip

class MusicPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50

# NEWS HOMEPAGE
class MusicHomeAPIView(APIView):
    def get(self, request):
        # All songs
        all_songs = (
            Song.objects
            .prefetch_related(
                "artists"
            )
            .distinct()
        )

        # DJs
        all_djs = DJ.objects.all()[:21]

        # Gospel songs
        gospels = (
            Song.objects
            .filter(
                genres__name="Gospel",
                is_active=True
            )[:21]
        )

        # Newest songs
        newest_songs = (
            all_songs
            .order_by(
                "-release_date"
            )[:21]
        )

        # Trending songs
        one_week_ago = (
            timezone.now()
            -
            timedelta(days=7)
        )

        trending_now = cache.get(
            "trending_now"
        )

        if not trending_now:
            trending_now = (
                Song.objects
                .annotate(
                    recent_views=Count(
                        "song_views",
                        filter=Q(
                            song_views__timestamp__gte=one_week_ago
                        )
                    )
                )
                .order_by(
                    "-recent_views"
                )[:10]
            )

            cache.set(
                "trending_now",
                list(trending_now),
                1800
            )

        context = {
            "request": request
        }

        return Response({
            "newest_songs": SongCardSerializer(
                newest_songs,
                many=True,
                context=context
            ).data,

            "gospels": SongCardSerializer(
                gospels,
                many=True,
                context=context
            ).data,

            "trending": SongCardSerializer(
                trending_now,
                many=True,
                context=context
            ).data,

            "djs": DJCardSerializer(
                all_djs,
                many=True,
                context=context
            ).data,
        })

class LatestMusicAPIView(ListAPIView):
    serializer_class = SongCardSerializer
    pagination_class = MusicPagination

    def get_queryset(self):
        SongArtistBridge = Song.artists.through

        return (
            Song.objects
            .filter(
                Exists(
                    SongArtistBridge.objects.filter(
                        song_id=OuterRef("pk")
                    )
                ),
                is_active=True
            )
            .prefetch_related(
                "artists"
            )
            .order_by(
                "-release_date"
            )
        )

class GospelMusicAPIView(ListAPIView):
    serializer_class = SongCardSerializer
    pagination_class = MusicPagination

    def get_queryset(self):
        return (
            Song.objects
            .filter(
                genres__name="Gospel",
                is_active=True
            )
            .prefetch_related(
                "artists"
            )
            .order_by(
                "-release_date"
            )
        )

class MixtapeListAPIView(ListAPIView):
    serializer_class = DJCardSerializer
    pagination_class = MusicPagination

    def get_queryset(self):
        return (
            DJ.objects
            .all()
            .order_by(
                "-created_at"
            )
        )

class TrendingSongAPIView(APIView):
    def get(self, request):
        now = timezone.now()

        def get_trending(cache_key, days, limit=21):
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data

            time_threshold = now - timedelta(days=days)

            songs = (
                Song.objects
                .annotate(
                    recent_views=Count(
                        "song_views",
                        filter=Q(
                            song_views__timestamp__gte=time_threshold
                        )
                    )
                )
                .prefetch_related(
                    "artists"
                )
                .order_by(
                    "-recent_views"
                )[:limit]
            )

            cache.set(
                cache_key,
                list(songs),
                1800
            )
            return songs

        trending_now = get_trending(
            "trending_now",
            1
        )

        trending_week = get_trending(
            "trending_week",
            7
        )

        trending_month = get_trending(
            "trending_month",
            30
        )

        trending_songs = (
            Song.objects
            .prefetch_related(
                "artists"
            )
            .order_by(
                "-views"
            )[:40]
        )

        context = {
            "request": request
        }

        return Response({
            "trending_now": SongCardSerializer(
                trending_now,
                many=True,
                context=context
            ).data,

            "trending_week": SongCardSerializer(
                trending_week,
                many=True,
                context=context
            ).data,

            "trending_month": SongCardSerializer(
                trending_month,
                many=True,
                context=context
            ).data,

            "trending_songs": SongCardSerializer(
                trending_songs,
                many=True,
                context=context
            ).data,
        })

class AlbumListAPIView(ListAPIView):
    serializer_class = AlbumCardSerializer
    pagination_class = MusicPagination

    def get_queryset(self):
        return (
            Album.objects
            .prefetch_related(
                "artist"
            )
            .annotate(
                song_count=Count("songs")
            )
            .order_by(
                "-release_date"
            )
        )

class AlbumDetailAPIView(APIView):
    def get(self, request, slug):
        album = get_object_or_404(
            Album,
            slug=slug
        )

        songs = (
            Song.objects
            .filter(
                album=album,
                is_active=True
            )
            .distinct()
        )

        context = {
            "request": request
        }

        return Response({
            "album": AlbumDetailSerializer(
                album,
                context=context
            ).data,

            "songs": SongCardSerializer(
                songs,
                many=True,
                context=context
            ).data
        })


# ============================================================
# COMMENT PAGINATIONS
# ============================================================

class CommentPagination(LimitOffsetPagination):
    default_limit = settings.MUSIC_INITIAL_COMMENTS
    max_limit = 20


class ReplyPagination(LimitOffsetPagination):
    default_limit = settings.MUSIC_INITIAL_REPLIES


# ============================================================
# FULL DETAIL PAGE API INFRASTRUCTURE
# ============================================================
class BaseMusicDetailAPIView(APIView):
    """
    Shared logic for Song and DJ detail page APIs.
    """

    serializer_class = None

    def get_related_songs(self, obj):
        if isinstance(obj, Song):
            return (
                Song.objects
                .filter(genres__in=obj.genres.all())
                .exclude(id=obj.id)
                .prefetch_related(
                    "artists",
                    "genres",
                    "tags",
                )
                .distinct()[:12]
            )

        return (
            Song.objects
            .order_by("-release_date")
            .prefetch_related(
                "artists",
                "genres",
                "tags",
            )[:12]
        )

    def get_trending_songs(self):
        return (
            Song.objects
            .order_by("-views")
            .prefetch_related(
                "artists",
                "genres",
                "tags",
            )[:12]
        )

    def get_latest_songs(self):
        return (
            Song.objects
            .order_by("-release_date")
            .prefetch_related(
                "artists",
                "genres",
                "tags",
            )[:6]
        )

    def get_latest_djs(self):
        return (
            DJ.objects
            .order_by("-created_at")
            .prefetch_related(
                "artists",
                "genres",
            )[:6]
        )

    def build_context(self, request, obj):
        return {
            "request": request,
            "related_songs": self.get_related_songs(obj),
            "trending_songs": self.get_trending_songs(),
            "latest_songs": self.get_latest_songs(),
            "latest_djs": self.get_latest_djs(),
        }

class SongDetailAPIView(BaseMusicDetailAPIView):
    """
    Complete Song Page API.
    """

    def get(self, request, slug, *args, **kwargs):

        Song.objects.filter(
            slug=slug
        ).update(
            views=F("views") + 1
        )

        song = get_object_or_404(
            Song.objects.select_related(
                "album"
            ).prefetch_related(
                "artists",
                "genres",
                "tags",
            ),
            slug=slug,
        )

        try:
            ip = get_cloudflare_ip(request)

            if not SongView.objects.filter(
                song=song,
                ip_address=ip,
            ).exists():

                SongView.objects.create(
                    song=song,
                    ip_address=ip,
                )

        except Exception:
            pass

        serializer = SongPageSerializer(
            song,
            context=self.build_context(request, song),
        )

        return Response(serializer.data)

# ============================================================
# DJ DETAIL
# ============================================================

class DJDetailAPIView(BaseMusicDetailAPIView):
    """
    Complete DJ Page API.
    """

    def get(self, request, slug, *args, **kwargs):

        dj = get_object_or_404(
            DJ.objects.prefetch_related(
                "artists",
                "genres",
            ),
            slug=slug,
        )

        serializer = DJPageSerializer(
            dj,
            context=self.build_context(request, dj),
        )

        return Response(serializer.data)

# ============================================================
# ROOT COMMENTS
# ============================================================

@method_decorator(
    ratelimit(
        key=get_cloudflare_ip,
        rate="3/m",
        method="POST",
        block=False,
    ),
    name="post",
)
class MusicCommentCreateAPIView(APIView):
    permission_classes = [AllowAny]

    """
    Create a new music comment or reply.
    """

    def post(self, request, slug, *args, **kwargs):

        # ==========================================
        # Locate music
        # ==========================================

        song = Song.objects.filter(slug=slug).first()
        dj = None

        if not song:
            dj = get_object_or_404(
                DJ,
                slug=slug,
            )

        is_staff = (
            request.user.is_authenticated
            and request.user.is_staff
        )

        # ==========================================
        # Rate limit
        # ==========================================

        if not is_staff and getattr(request, "limited", False):

            return JsonResponse(
                {
                    "status": "error",
                    "message": "🔥 Slow down! You are posting too fast.",
                },
                status=429,
            )

        # ==========================================
        # Honeypot
        # ==========================================

        if request.POST.get("user_website"):

            return JsonResponse(
                {
                    "status": "success",
                    "message": "Comment submitted successfully.",
                }
            )

        # ==========================================
        # IP blacklist
        # ==========================================

        if not is_staff:

            xff = request.META.get("HTTP_X_FORWARDED_FOR")

            client_ip = (
                xff.split(",")[0].strip()
                if xff
                else request.META.get("REMOTE_ADDR")
            )

            if monitor_and_filter_ip(
                client_ip,
                action_type="comment",
            ):

                return JsonResponse(
                    {
                        "status": "error",
                        "message": (
                            "🚫 Access Denied. "
                            "Your IP has been temporarily blocked."
                        ),
                    },
                    status=403,
                )

        # ==========================================
        # Block links
        # ==========================================

        content = request.POST.get("content", "")

        if (
            not is_staff
            and re.search(
                r"(https?://|www\.|<a\s+href|\[url\])",
                content,
                re.IGNORECASE,
            )
        ):

            return JsonResponse(
                {
                    "status": "error",
                    "message": "Links are not allowed in comments.",
                },
                status=400,
            )

        # ==========================================
        # Validate form
        # ==========================================

        form = MusicCommentForm(request.POST)

        if not form.is_valid():

            errors = ", ".join(

                f"{field}: {error[0]}"

                for field, error in form.errors.items()

            )

            return JsonResponse(
                {
                    "status": "error",
                    "message": errors,
                },
                status=400,
            )

        # ==========================================
        # Build comment
        # ==========================================

        comment = form.save(commit=False)

        if song:
            comment.song = song
        else:
            comment.dj = dj

        # ==========================================
        # Staff identity
        # ==========================================

        if is_staff:

            comment.user = request.user

            comment.name = (
                request.user.get_full_name()
                or request.user.username
            )

        else:

            forbidden = (
                "admin",
                "staff",
                "moderator",
                "editor",
                "boss",
                "vibenation",
            )

            if any(

                word in comment.name.lower()

                for word in forbidden

            ):

                comment.name = "Anonymous Fan"

        # ==========================================
        # Reply handling
        # ==========================================

        parent_id = request.POST.get("parent_id")

        if parent_id:

            query = MusicComment.objects.filter(id=parent_id)

            if song:
                query = query.filter(song=song)
            else:
                query = query.filter(dj=dj)

            parent = query.first()

            if parent:

                comment.parent = (
                    parent.parent
                    if parent.parent
                    else parent
                )

        # ==========================================
        # Save
        # ==========================================

        comment.save()

        # ==========================================
        # Response
        # ==========================================

        serializer = MusicCommentSerializer(comment)

        data = {
            "status": "success",
            "message": "Comment posted successfully.",
            "comment": serializer.data,
            "commenter_name": comment.name,
        }

        response = JsonResponse(
            data,
            status=201,
        )

        if not is_staff:

            response.set_cookie(
                "music_commenter_name",
                comment.name,
                max_age=60 * 60 * 24 * 30,
            )

        return response

class MusicCommentsChunkAPIView(APIView):
    """
    Returns root comments in chunks.
    Supports both Songs and DJs.
    """

    def get(self, request, *args, **kwargs):

        slug = kwargs["slug"]

        root_comments = None
        song = None
        dj = None

        song = Song.objects.filter(
            slug=slug
        ).first()

        if song:

            root_comments = (
                song.comments
                .filter(
                    parent__isnull=True,
                    is_approved=True,
                )
                .order_by("-created_at")
            )

        else:

            dj = get_object_or_404(
                DJ,
                slug=slug,
            )

            root_comments = (
                dj.comments
                .filter(
                    parent__isnull=True,
                    is_approved=True,
                )
                .order_by("-created_at")
            )

        paginator = CommentPagination()

        total_comments_count = MusicComment.objects.filter(
            Q(song=song) | Q(dj=dj)
        ).count()

        if request.query_params.get("offset") is None:
            paginator.default_limit = settings.MUSIC_INITIAL_COMMENTS
        else:
            paginator.default_limit = settings.MUSIC_COMMENTS_PER_LOAD

        page = paginator.paginate_queryset(
            root_comments,
            request
        )

        serializer = MusicCommentSerializer(
            page,
            many=True,
        )

        return Response(
            {
                "results": serializer.data,
                "has_more": paginator.get_next_link() is not None,
                "total_comments_count": total_comments_count
            },
            status=status.HTTP_200_OK,
        )


# ============================================================
# REPLIES
# ============================================================

class MusicRepliesChunkAPIView(APIView):
    """
    Returns flattened replies.
    """

    def get(self, request, comment_id, *args, **kwargs):

        parent_comment = get_object_or_404(
            MusicComment,
            id=comment_id,
        )

        all_replies = parent_comment.get_all_replies()

        paginator = ReplyPagination()

        if request.query_params.get("offset") is None:
            paginator.default_limit = settings.MUSIC_INITIAL_REPLIES
        else:
            paginator.default_limit = settings.MUSIC_REPLIES_PER_LOAD

        page = paginator.paginate_queryset(
            all_replies,
            request,
        )

        serializer = MusicReplySerializer(
            page,
            many=True,
        )

        loaded = paginator.offset + len(page)

        remaining = max(
            len(all_replies) - loaded,
            0,
        )

        return Response(
            {
                "results": serializer.data,
                "total_count": len(all_replies),
                "remaining_count": remaining,
                "has_more": remaining > 0,
            },
            status=status.HTTP_200_OK,
        )

# =====================================
# SONG SEARCH
# =====================================
class SearchAPIView(APIView):
    def get(self, request):
        query = request.GET.get("q", "").strip()
        if not query:
            return Response({
                "query": query,
                "songs": [],
                "albums": [],
                "artists": [],
                "news": []
            })

        # Songs search
        songs_queryset = (
            Song.objects
            .filter(
                Q(title__icontains=query) |
                Q(artists__name__icontains=query)
            )
            .select_related(
                "album"
            )
            .prefetch_related(
                "artists"
            )
            .distinct()
            .order_by(
                "-release_date"
            )
        )

        # Albums search
        album_matches = (
            Album.objects
            .filter(
                Q(title__icontains=query) |
                Q(artist__name__icontains=query)
            )
            .prefetch_related(
                "artist"
            )
            .distinct()
            .order_by(
                "-release_date"
            )
        )

        # Songs inside matched albums
        album_songs = (
            Song.objects
            .filter(
                album__in=album_matches
            )
            .select_related(
                "album"
            )
            .prefetch_related(
                "artists"
            )
            .distinct()
        )

        all_songs = (
            songs_queryset | album_songs
        ).distinct().order_by(
            "-release_date"
        )

        # News
        news_results = (
            News.objects
            .public()
            .filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__name__icontains=query)
            )
            .prefetch_related(
                "tags"
            )
            .distinct()
            .order_by(
                "-date_published"
            )
        )

        artists = (
            Artist.objects
            .filter(
                name__icontains=query
            )[:10]
        )

        context = {
            "request": request
        }

        return Response({
            "query": query,

            "songs": SongCardSerializer(
                all_songs,
                many=True,
                context=context
            ).data,

            "albums": AlbumCardSerializer(
                album_matches,
                many=True,
                context=context
            ).data,

            "artists": ArtistSerializer(
                artists,
                many=True,
                context=context
            ).data,

            "news": NewsCardSerializer(
                news_results,
                many=True,
                context=context
            ).data,
        })

class DownloadSongAPIView(APIView):
    def get(self, request, slug):
        song = get_object_or_404(
            Song,
            slug=slug
        )

        if not song.audio_file or not os.path.exists(song.audio_file.path):
            raise Http404("Audio file not found.")

        original_path = song.audio_file.path
        artist_names = ", ".join(
            [artist.name for artist in song.artists.all()]
        )

        download_name = (
            f"{song.title} - {artist_names} | VibeNationhq.com.mp3"
        )

        temp_dir = os.path.join(
            settings.MEDIA_ROOT,
            "temp_downloads"
        )

        os.makedirs(
            temp_dir,
            exist_ok=True
        )

        temp_path = os.path.join(
            temp_dir,
            f"dl_{song.id}_{os.path.basename(original_path)}"
        )

        shutil.copy2(
            original_path,
            temp_path
        )

        try:
            logo_path = os.path.join(
                settings.STATICFILES_DIRS[0],
                "images",
                "VibeNation_cover.jpg"
            )

            clean_mp3_tags(
                temp_path,
                song.title,
                artist_names,
                logo_path
            )

            file_handle = open(
                temp_path,
                "rb"
            )

            response = FileResponse(
                file_handle,
                as_attachment=True,
                filename=download_name
            )

            def cleanup():
                file_handle.close()

                if os.path.exists(temp_path):
                    os.remove(temp_path)


            response.close = cleanup

            Song.objects.filter(
                id=song.id
            ).update(
                download=F("download") + 1
            )
            return response

        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            print(f"Download Error: {e}")
            raise Http404(
                "Something went wrong."
            )

class SongsByTagAPIView(ListAPIView):
    serializer_class = SongCardSerializer
    pagination_class = MusicPagination
    def get_queryset(self):
        self.tag = get_object_or_404(
            Tag,
            slug=self.kwargs["tag_slug"]
        )

        return (
            Song.objects
            .filter(
                tags=self.tag,
                is_active=True
            )
            .select_related("album")
            .prefetch_related("artists", "tags")
            .order_by("-release_date")
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            page,
            many=True
        )

        return self.get_paginated_response({
            "tag": {
                "name": self.tag.name,
                "slug": self.tag.slug,
            },
            "songs": serializer.data,
        })