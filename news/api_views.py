import random

from django.utils import timezone
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.cache import cache
from django.db.models import Q, Count, F

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

from datetime import timedelta

from collections import defaultdict
from news.models import News, Category, NewsComment
from music.models import Song
from taggit.models import Tag
from news.serializers import (
    NewsDetailSerializer,
    NewsCommentSerializer,
    NewsReplySerializer,
    CategorySerializer,
    NewsHomeSerializer,
    NewsCardSerializer
)

# ================== HELPER FUNCTION =================
def get_top_ranking(category_name, cache_key, last_caching, strict_caching):
    cached_data = cache.get(cache_key)

    current_check = News.objects.public().filter(
        category__name=category_name,
        is_featured=False,
        is_sponsored=False,
        date_published__gte=strict_caching
    ).annotate(
        recent_views=Count(
            'views_log',
            filter=Q(
                views_log__created_at__gte=last_caching
            )
        )
    ).order_by(
        '-recent_views',
        '-views',
        '-date_published'
    )[:6]

    new_ranking = list(current_check)

    if not cached_data or (
        new_ranking and new_ranking[0].recent_views > 0
    ):
        cached_data = new_ranking
        cache.set(cache_key, cached_data, None)

    return cached_data
# =========== END OF HELPER FUNCTION ==============

class NewsPagination(PageNumberPagination):
    page_size = 10

class NewsHomeAPIView(APIView):
    permission_classes = [AllowAny]
    """
    Fetching the News Home contents
    """
    def get(self, request):
        now = timezone.now()

        last_caching = now - timedelta(hours=12)
        strict_caching = now - timedelta(days=1444)

        # Fetch Songs & Featured Blocks
        latest_songs = (
            Song.objects
            .prefetch_related('artists')
            .all()
            .order_by('-release_date')[:12]
        )

        global_featured = (
            News.objects
            .public()
            .filter(is_featured=True)
            .order_by('-date_published')
            .first()
        )

        sponsored_feature = (
            News.objects
            .sponsored()
            .first()
        )

        # Top News Cache
        top_news_pool = cache.get(
            'top_news_pool'
        )

        current_ranking_query = (
            News.objects
            .public()
            .filter(
                is_featured=False,
                is_sponsored=False,
                date_published__gte=strict_caching
            )
            .annotate(
                recent_views=Count(
                    'views_log',
                    filter=Q(
                        views_log__created_at__gte=last_caching
                    )
                )
            )
            .order_by(
                '-recent_views',
                '-views',
                '-date_published'
            )[:10]
        )

        new_ranking = list(current_ranking_query)

        if not top_news_pool or (
            new_ranking and new_ranking[0].recent_views > 0
        ):
            top_news_pool = new_ranking
            cache.set(
                'top_news_pool',
                top_news_pool,
                None
            )

        if sponsored_feature:
            top_news = [
                n for n in top_news_pool
                if n.id != sponsored_feature.id
            ][:4]
        else:
            top_news = top_news_pool[:5]

        # Latest News
        latest_pool = (
            News.objects
            .public()
            .filter(is_featured=False)
            .order_by('-date_published')[:6]
        )

        if sponsored_feature:
            latest_news = [
                n for n in latest_pool
                if n.id != sponsored_feature.id
            ][:5]
        else:
            latest_news = latest_pool[:5]

        # Category Feeds
        target_categories = [
            'Sports',
            'Opinion',
            'Education',
            'Foreign News',
            'Events',
            'Music News',
            'Celebrity Gossip',
            'Technology',
            'Lifestyle',
            'Politics',
            'Entertainment'
        ]

        all_category_news = (
            News.objects
            .public()
            .filter(
                category__name__in=target_categories,
                is_featured=False
            )
            .prefetch_related('category')
            .order_by('-date_published')
            .distinct()
        )

        news_by_cat = defaultdict(list)

        for article in all_category_news:
            for cat in article.category.all():
                if (
                    cat.name in target_categories
                    and article not in news_by_cat[cat.name]
                ):
                    news_by_cat[cat.name].append(article)

        # Serializer Context
                # Serializer Context
        ctx = {
            "request": request
        }


        homepage_data = {

            # Hero blocks
            "global_featured": global_featured,

            "sponsored_feature": sponsored_feature,

            "top_news": top_news,

            "latest_news": latest_news,


            # Music feeds
            "latest_songs": latest_songs,

            # Category feeds
            "categorized_feeds": {
                "sports":
                    news_by_cat['Sports'][:5],

                "opinion":
                    news_by_cat['Opinion'][:10],

                "education":
                    news_by_cat['Education'][:5],

                "foreign_news":
                    news_by_cat['Foreign News'][:5],

                "events":
                    news_by_cat['Events'][:10],

                "music_news":
                    news_by_cat['Music News'][:5],

                "celebrity_gossip":
                    news_by_cat['Celebrity Gossip'][:5],

                "technology":
                    news_by_cat['Technology'][:5],

                "lifestyle":
                    news_by_cat['Lifestyle'][:10],

                "politics":
                    news_by_cat['Politics'][:5],

                "entertainment":
                    news_by_cat['Entertainment'][:5],
            }
        }
        serializer = NewsHomeSerializer(
            homepage_data,
            context=ctx
        )

        return Response(serializer.data)


class NewsHomeAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        now = timezone.now()
        last_caching = now - timedelta(hours=12)
        strict_caching = now - timedelta(days=1444)

        # Featured News
        global_featured = (
            News.objects
            .public()
            .filter(is_featured=True)
            .order_by("-date_published")
            .first()
        )

        # Sponsored News
        sponsored_feature = (
            News.objects
            .sponsored()
            .first()
        )

        # Top News
        top_news_pool = cache.get("top_news_pool")

        current_ranking_query = (
            News.objects
            .public()
            .filter(
                is_featured=False,
                is_sponsored=False,
                date_published__gte=strict_caching,
            )
            .annotate(
                recent_views=Count(
                    "views_log",
                    filter=Q(
                        views_log__created_at__gte=last_caching
                    ),
                )
            )
            .order_by(
                "-recent_views",
                "-views",
                "-date_published",
            )[:10]
        )

        new_ranking = list(current_ranking_query)

        if (
            not top_news_pool
            or (
                new_ranking
                and new_ranking[0].recent_views > 0
            )
        ):
            top_news_pool = new_ranking
            cache.set(
                "top_news_pool",
                top_news_pool,
                None,
            )

        if sponsored_feature:
            top_news = [
                article
                for article in top_news_pool
                if article.id != sponsored_feature.id
            ][:4]
        else:
            top_news = top_news_pool[:5]

        # Latest News
        latest_pool = (
            News.objects
            .public()
            .filter(is_featured=False)
            .order_by("-date_published")[:6]
        )

        if sponsored_feature:
            latest_news = [
                article
                for article in latest_pool
                if article.id != sponsored_feature.id
            ][:5]
        else:
            latest_news = latest_pool[:5]

        # Categories
        target_categories = [
            "Sports",
            "Opinion",
            "Education",
            "Foreign News",
            "Events",
            "Music News",
            "Celebrity Gossip",
            "Technology",
            "Lifestyle",
            "Politics",
            "Entertainment",
        ]

        all_category_news = (
            News.objects
            .public()
            .filter(
                category__name__in=target_categories,
                is_featured=False,
            )
            .prefetch_related("category")
            .order_by("-date_published")
            .distinct()
        )

        news_by_cat = defaultdict(list)

        for article in all_category_news:
            for category in article.category.all():
                if (
                    category.name in target_categories
                    and article not in news_by_cat[category.name]
                ):
                    news_by_cat[category.name].append(article)

        payload = {
            "global_featured": global_featured,
            "sponsored_feature": sponsored_feature,
            "top_news": top_news,
            "latest_news": latest_news,
            "categorized_feeds": {
                "sports": news_by_cat["Sports"][:7],
                "opinion": news_by_cat["Opinion"][:10],
                "education": news_by_cat["Education"][:7],
                "foreign_news": news_by_cat["Foreign News"][:7],
                "events": news_by_cat["Events"][:7],
                "music_news": news_by_cat["Music News"][:8],
                "celebrity_gossip": news_by_cat["Celebrity Gossip"][:7],
                "technology": news_by_cat["Technology"][:7],
                "lifestyle": news_by_cat["Lifestyle"][:10],
                "politics": news_by_cat["Politics"][:7],
                "entertainment": news_by_cat["Entertainment"][:7],
            },
        }

        serializer = NewsHomeSerializer(
            payload,
            context={"request": request},
        )

        return Response(serializer.data)
    

class CategoryNewsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, slug):
        last_week = timezone.now() - timedelta(days=7)

        category = get_object_or_404(
            Category,
            slug=slug
        )

        # Base queryset
        news_list_qs = (
            News.objects
            .public()
            .filter(
                category=category,
                is_published=True
            )
            .distinct()
            .order_by("-date_published")
        )

        # Exclude first article from trending
        first_article_id = None

        if news_list_qs.exists():
            first_article_id = news_list_qs.first().id

        # Trending sidebar
        trending_news_qs = (
            News.objects
            .public()
            .filter(
                is_published=True,
                date_published__gte=last_week
            )
        )

        if first_article_id:
            trending_news_qs = trending_news_qs.exclude(
                id=first_article_id
            )

        trending_news = trending_news_qs.order_by(
            "-views"
        )[:5]

        # Categories widget
        all_categories = (
            Category.objects
            .exclude(slug="")
            .annotate(
                news_count=Count("news")
            )
            .order_by("-news_count")[:10]
        )

        # Pagination
        paginator = NewsPagination()

        paginated_queryset = paginator.paginate_queryset(
            news_list_qs,
            request
        )

        ctx = {
            "request": request
        }

        return Response({
            "category": {
                "name": category.name,
                "slug": category.slug,
            },

            "trending_news": NewsCardSerializer(
                trending_news,
                many=True,
                context=ctx,
            ).data,

            "all_categories": CategorySerializer(
                all_categories,
                many=True,
                context=ctx,
            ).data,

            "paginated_grid": {
                "count": paginator.page.paginator.count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "current_page": paginator.page.number,
                "total_pages": paginator.page.paginator.num_pages,

                "results": NewsCardSerializer(
                    paginated_queryset,
                    many=True,
                    context=ctx,
                ).data,
            },
        })


class NewsByTagAPIView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = NewsCardSerializer
    pagination_class = NewsPagination

    def get_tag(self):
        if not hasattr(self, "_tag"):
            self._tag = get_object_or_404(
                Tag,
                slug=self.kwargs.get("slug")
            )
        return self._tag

    def get_queryset(self):
        tag = self.get_tag()

        return (
            News.objects
            .public()
            .filter(tags=tag)
            .prefetch_related("category")
            .order_by("-date_published")
        )

    def list(self, request, *args, **kwargs):
        response = super().list(
            request,
            *args,
            **kwargs
        )

        tag = self.get_tag()

        return Response({
            "tag": {
                "name": tag.name,
                "slug": tag.slug,
            },
            "paginated_grid": response.data
        })

class CategoryHomeAPIView(APIView):
    permission_classes = [AllowAny]

    category_name = None
    cache_key = None
    has_sponsored = True

    def get(self, request):
        now = timezone.now()

        last_caching = now - timedelta(hours=12)
        strict_caching = now - timedelta(days=1444)

        # Featured article
        featured = (
            News.objects
            .public()
            .filter(
                category__name=self.category_name,
                is_featured=True
            )
            .order_by("-date_published")
            .first()
        )

        # Sponsored article
        if self.has_sponsored:
            sponsored = (
                News.objects
                .sponsored()
                .filter(
                    category__name=self.category_name
                )
                .first()
            )
        else:
            sponsored = None

        # Top ranking cache
        top_pool = get_top_ranking(
            self.category_name,
            self.cache_key,
            last_caching,
            strict_caching
        )

        if sponsored:
            top_news = [
                n for n in top_pool
                if n.id != sponsored.id
            ][:4]
        else:
            top_news = top_pool[:5]

        # Latest news
        latest_pool = (
            News.objects
            .public()
            .filter(
                category__name=self.category_name,
                is_featured=False
            )
            .order_by("-date_published")[:6]
        )

        if sponsored:
            latest_news = [
                n for n in latest_pool
                if n.id != sponsored.id
            ][:5]
        else:
            latest_news = latest_pool[:5]

        # Prevent duplicate articles
        used_ids = (
            [n.id for n in top_news] +
            [n.id for n in latest_news]
        )

        if featured:
            used_ids.append(featured.id)

        if sponsored:
            used_ids.append(sponsored.id)

        # Main grid queryset
        news_queryset = (
            News.objects
            .public()
            .filter(
                category__name=self.category_name,
                is_featured=False,
                is_sponsored=False
            )
            .exclude(
                id__in=used_ids
            )
            .order_by("-date_published")
        )

        # Random discovery news
        other_news_pool = list(
            News.objects
            .public()
            .exclude(
                category__name=self.category_name
            )
            .order_by("-date_published")[:20]
            .values_list(
                "id",
                flat=True
            )
        )

        if other_news_pool:
            sample_ids = random.sample(
                other_news_pool,
                min(
                    len(other_news_pool),
                    5
                )
            )

            mini_featured = (
                News.objects
                .public()
                .filter(
                    id__in=sample_ids
                )
                .prefetch_related(
                    "category"
                )
            )
        else:
            mini_featured = []

        # Pagination
        paginator = NewsPagination()
        paginated_queryset = paginator.paginate_queryset(
            news_queryset,
            request
        )

        ctx = {
            "request": request
        }

        return Response({
            "category": {
                "name": self.category_name
            },

            "featured":
                NewsDetailSerializer(
                    featured,
                    context=ctx
                ).data
                if featured else None,

            "sponsored":
                NewsCardSerializer(
                    sponsored,
                    context=ctx
                ).data
                if sponsored else None,

            "top_news":
                NewsCardSerializer(
                    top_news,
                    many=True,
                    context=ctx
                ).data,

            "latest_news":
                NewsCardSerializer(
                    latest_news,
                    many=True,
                    context=ctx
                ).data,

            "mini_featured_news":
                NewsCardSerializer(
                    mini_featured,
                    many=True,
                    context=ctx
                ).data,

            "paginated_grid": {
                "count":
                    paginator.page.paginator.count,

                "next":
                    paginator.get_next_link(),

                "previous":
                    paginator.get_previous_link(),

                "current_page":
                    paginator.page.number,

                "total_pages":
                    paginator.page.paginator.num_pages,

                "results":
                    NewsCardSerializer(
                        paginated_queryset,
                        many=True,
                        context=ctx
                    ).data
            }
        })

class EntertainmentAPIView(CategoryHomeAPIView):
    category_name = "Entertainment"
    cache_key = "top_entertainment"

class PoliticsAPIView(CategoryHomeAPIView):
    category_name = "Politics"
    cache_key = "top_political"

class LifestyleAPIView(CategoryHomeAPIView):
    category_name = "Lifestyle"
    cache_key = "top_lifestyle"

class TechnologyAPIView(CategoryHomeAPIView):
    category_name = "Technology"
    cache_key = "top_technology"

class MusicNewsAPIView(CategoryHomeAPIView):
    category_name = "Music News"
    cache_key = "top_music_news"

class SportsAPIView(CategoryHomeAPIView):
    category_name = "Sports"
    cache_key = "top_sport"

class EventsAPIView(CategoryHomeAPIView):
    category_name = "Events"
    cache_key = "top_event"

class EducationAPIView(CategoryHomeAPIView):
    category_name = "Education"
    cache_key = "top_education"

class OpinionAPIView(CategoryHomeAPIView):
    category_name = "Opinion"
    cache_key = "top_opinion"
    has_sponsored = False

# =======================
# NEWS DETAILS
# =======================
class CommentPagination(LimitOffsetPagination):
    default_limit = settings.NEWS_COMMENTS_PER_LOAD  # Load comments in chunks of 5
    max_limit = 20

class ArticleCommentsChunkAPIView(APIView):
    """
    Returns top-level root comments for an article in chunks using limit/offset.
    """
    def get(self, request, slug, *args, **kwargs):
        news_item = get_object_or_404(News, slug=slug)
        root_comments = news_item.comments.filter(parent__isnull=True, is_approved=True).order_by('-created_at')
        
        print(settings.NEWS_COMMENTS_PER_LOAD)
        print(type(settings.NEWS_COMMENTS_PER_LOAD))
        paginator = CommentPagination()
        paginated_qs = paginator.paginate_queryset(root_comments, request)
        serializer = NewsCommentSerializer(paginated_qs, many=True)
        
        return Response({
            "results": serializer.data,
            "has_more": paginator.get_next_link() is not None
        }, status=status.HTTP_200_OK)

class ReplyPagination(LimitOffsetPagination):
    default_limit = settings.NEWS_REPLIES_PER_LOAD  # Load replies in chunks of 5

class CommentRepliesChunkAPIView(APIView):
    """
    Returns nested replies for a specific root comment block in chunks safely.
    """
    def get(self, request, comment_id, *args, **kwargs):
        # 1. Safely check if the target parent comment even exists
        parent_comment = get_object_or_404(NewsComment, id=comment_id)

        # Use the SAME flattened algorithm used by the initial page render
        all_replies = parent_comment.get_all_replies()

        total_count = len(all_replies)

        paginator = ReplyPagination()
        paginated_replies = paginator.paginate_queryset(all_replies, request)

        serializer = NewsReplySerializer(
            paginated_replies,
            many=True
        )
        
        return Response({
            "results": serializer.data,
            "total_count": total_count,
            "has_more": paginator.get_next_link() is not None
        }, status=status.HTTP_200_OK)

class NewsDetailAPIView(APIView):
    """
    Returns complete decoupled article details by slug.
    Also increments the view counter on request execution.
    """
    def get(self, request, slug, *args, **kwargs):
        last_week = timezone.now() - timedelta(days=7)
        # Atomic-style update tracking view count incrementation
        from django.db.models import F
        News.objects.filter(slug=slug).update(views=F('views') + 1)
        
        news_item = get_object_or_404(
            News.objects.prefetch_related('category', 'tags'), 
            slug=slug
        )

        trending_news = (
        News.objects.public()
        .filter(date_published__gte=last_week)
        .exclude(id=news_item.id)
        .order_by('-views')[:5]
        ) # FOR MARQUEE

        # related_news = (
        # News.objects.public()
        # .filter(category__in=News.category.all())
        # .exclude(id=news_item.id)
        # .order_by('-date_published')
        # .distinct()[:6]
        # )
        
        # Track individual view session model entry if desired
        from news.models import NewsView
        NewsView.objects.create(news=news_item)
        
        serializer = NewsDetailSerializer(news_item, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class SidebarDataAPIView(APIView):
    """
    Combines 'Most Read' trending news and 'Explore Topics' category metrics
    into a single efficient JSON response context.
    """
    def get(self, request, *args, **kwargs):
        last_week = timezone.now() - timedelta(days=7)
        
        # 1. Top 5 Most Read articles within 7 days
        trending_qs = (
            News.objects.public()
            .filter(date_published__gte=last_week)
            .order_by('-views')[:5]
        )
        
        # 2. Top 10 categories ordered by content weight
        categories_qs = Category.objects.annotate(
            news_count=Count('news')
        ).order_by('-news_count')[:10]
        
        trending_data = NewsCardSerializer(trending_qs, many=True, context={'request': request}).data
        categories_data = CategorySerializer(categories_qs, many=True).data
        
        return Response({
            "trending_news": trending_data,
            "all_categories": categories_data
        }, status=status.HTTP_200_OK)


class RecentSongsAPIView(APIView):
    """
    Returns the 4 most recently dropped songs to hydrate the layout mini-grid.
    """
    def get(self, request, *args, **kwargs):
        recent_songs = Song.objects.all().order_by('-release_date')[:4]
        
        # We manually serialize this to decouple it perfectly for the client framework layout
        songs_payload = []
        for song in recent_songs:
            cover_url = ""
            if hasattr(song, 'original_cover') and song.original_cover:
                cover_url = request.build_absolute_uri(song.original_cover.url)
            elif hasattr(song, 'cover_image') and song.cover_image:
                cover_url = request.build_absolute_uri(song.cover_image.url)
                
            artists_list = [artist.name for artist in song.artists.all()] if hasattr(song, 'artists') else []
            
            songs_payload.append({
                "id": song.id,
                "title": song.title,
                "slug": song.slug,
                "cover_url": cover_url,
                "artists": artists_list,
                "absolute_url": f"/music/{song.slug}/"  # Fallback client path mapping
            })
            
        return Response(songs_payload, status=status.HTTP_200_OK)