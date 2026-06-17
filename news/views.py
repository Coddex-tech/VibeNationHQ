from django.shortcuts import render, get_object_or_404, redirect
from .models import News, Category, NewsView, NewsComment
from music.models import Song
from django.core.paginator import Paginator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from taggit.models import Tag
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from django.db.models import Count, Q, F
from .serializers import NewsSerializer
import random
import re
from .forms import NewsCommentForm
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponseRedirect
from django_ratelimit.decorators import ratelimit
from utils.security import get_cloudflare_ip
from collections import defaultdict
from ads.utils import insert_dynamic_ads

# ============== HELPER FUNCTION ================
def get_top_ranking(category_name, cache_key, last_caching, strict_caching):
    cached_data = cache.get(cache_key)
    
    # Run the fresh check
    current_check = News.objects.public().filter(
        category__name=category_name, 
        is_featured=False,
        is_sponsored=False,
        date_published__gte=strict_caching
    ).annotate(
        recent_views=Count(
            'views_log', 
            filter=Q(views_log__created_at__gte=last_caching)
        )
    ).order_by('-recent_views', '-views', '-date_published')[:6]

    new_ranking = list(current_check)

    # Snapshot Logic
    if not cached_data or (new_ranking and new_ranking[0].recent_views > 0):
        cached_data = new_ranking
        cache.set(cache_key, cached_data, None)
    
    return cached_data
# ========= END OF HELPER FUNCTION ========

class NewsPagination(PageNumberPagination):
    page_size = 1

def homepage(request):
    now = timezone.now()
    last_caching = timezone.now() - timedelta(hours=12)
    strict_caching = timezone.now() - timedelta(days=1444)

    latest_songs = Song.objects.prefetch_related('artists').all().order_by('-release_date')[:12]
    global_featured = News.objects.public().filter(is_featured=True).order_by('-date_published').first()

    # SPONSORED POST
    sponsored_feature = News.objects.sponsored().first()
    
    # TOP NEWS
    top_news_pool = cache.get('top_news_pool')
    current_ranking_query = News.objects.public().filter(
        is_featured=False,
        is_sponsored=False,
        date_published__gte=strict_caching
    ).annotate(
        recent_views=Count('views_log', filter=Q(views_log__created_at__gte=last_caching))
    ).order_by('-recent_views', '-views', '-date_published')[:10]

    new_ranking = list(current_ranking_query)
    if not top_news_pool or (new_ranking and new_ranking[0].recent_views > 0):
        top_news_pool = new_ranking
        cache.set('top_news_pool', top_news_pool, None)

    if sponsored_feature:
        top_news = [n for n in top_news_pool if n.id != sponsored_feature.id][:4]
    else:
        top_news = top_news_pool[:5]

    # LATEST NEWS
    latest_pool = News.objects.public().filter(is_featured=False).order_by('-date_published')[:6]
    if sponsored_feature:
        latest_news = [n for n in latest_pool if n.id != sponsored_feature.id][:5]
    else:
        latest_news = latest_pool[:5]

    target_categories = [
        'Sports', 'Opinion', 'Education', 'Foreign News', 'Events', 
        'Music News', 'Celebrity Gossip', 'Technology', 'Lifestyle', 
        'Politics', 'Entertainment'
    ]

    all_category_news = News.objects.public().filter(
        category__name__in=target_categories,
        is_featured=False
    ).prefetch_related('category').order_by('-date_published').distinct()

    # Grouping logic for manyformany
    news_by_cat = defaultdict(list)
    for article in all_category_news:
        for cat in article.category.all():
            cat_name = cat.name
            if cat_name in target_categories:
                if article not in news_by_cat[cat_name]:
                    news_by_cat[cat_name].append(article)

    # TRENDING MUSIC
    one_week_ago = timezone.now() - timedelta(days=7)
    trending_now = cache.get('trending_now')
    if not trending_now:
        trending_now = Song.objects.annotate(
            recent_views=Count('song_views', filter=Q(song_views__timestamp__gte=one_week_ago))
        ).order_by('-recent_views')[:4]
        cache.set('trending_now', list(trending_now), 1800)

    context = {
        'latest_songs': latest_songs,
        'global_featured': global_featured,
        'sponsored_feature': sponsored_feature,
        'top_news': top_news,
        'latest_news': latest_news,
        'sport': news_by_cat['Sports'][:5],
        'opinion': news_by_cat['Opinion'][:10],
        'education': news_by_cat['Education'][:5],
        'foreign_news': news_by_cat['Foreign News'][:5],
        'events': news_by_cat['Events'][:10],
        'music_news': news_by_cat['Music News'][:5],
        'celebrity_gossip': news_by_cat['Celebrity Gossip'][:5],
        'technology': news_by_cat['Technology'][:5],
        'lifestyle': news_by_cat['Lifestyle'][:10],
        'politics': news_by_cat['Politics'][:5],
        'entertainment': news_by_cat['Entertainment'][:5],
        'now': now,
        'trending_music': trending_now,
    }
    return render(request, 'homepage.html', context)
# ----------------------------------------------------------------------||

def news_home(request):
    now = timezone.now()
    last_caching = timezone.now() - timedelta(hours=12)
    strict_caching = timezone.now() - timedelta(days=1444)

    global_featured = News.objects.public().filter(is_featured=True).order_by('-date_published').first()

    # SPONSORED POST
    sponsored_feature = News.objects.sponsored().first()
    
    # TOP NEWS
    top_news_pool = cache.get('top_news_pool')
    current_ranking_query = News.objects.public().filter(
        is_featured=False,
        is_sponsored=False,
        date_published__gte=strict_caching
    ).annotate(
        recent_views=Count('views_log', filter=Q(views_log__created_at__gte=last_caching))
    ).order_by('-recent_views', '-views', '-date_published')[:10]

    new_ranking = list(current_ranking_query)
    if not top_news_pool or (new_ranking and new_ranking[0].recent_views > 0):
        top_news_pool = new_ranking
        cache.set('top_news_pool', top_news_pool, None)

    if sponsored_feature:
        top_news = [n for n in top_news_pool if n.id != sponsored_feature.id][:4]
    else:
        top_news = top_news_pool[:5]

    # LATEST NEWS
    latest_pool = News.objects.public().filter(is_featured=False).order_by('-date_published')[:6]
    if sponsored_feature:
        latest_news = [n for n in latest_pool if n.id != sponsored_feature.id][:5]
    else:
        latest_news = latest_pool[:5]

    target_categories = [
        'Sports', 'Opinion', 'Education', 'Foreign News', 'Events', 
        'Music News', 'Celebrity Gossip', 'Technology', 'Lifestyle', 
        'Politics', 'Entertainment'
    ]

    all_category_news = News.objects.public().filter(
        category__name__in=target_categories,
        is_featured=False
    ).prefetch_related('category').order_by('-date_published').distinct()

    # Grouping logic for manyformany
    news_by_cat = defaultdict(list)
    for article in all_category_news:
        for cat in article.category.all():
            cat_name = cat.name
            if cat_name in target_categories:
                if article not in news_by_cat[cat_name]:
                    news_by_cat[cat_name].append(article)

    context = {
        'global_featured': global_featured,
        'sponsored_feature': sponsored_feature,
        'top_news': top_news,
        'latest_news': latest_news,
        'sport': news_by_cat['Sports'][:7],
        'opinion': news_by_cat['Opinion'][:10],
        'education': news_by_cat['Education'][:7],
        'foreign_news': news_by_cat['Foreign News'][:7],
        'events': news_by_cat['Events'][:7],
        'music_news': news_by_cat['Music News'][:8],
        'celebrity_gossip': news_by_cat['Celebrity Gossip'][:7],
        'technology': news_by_cat['Technology'][:7],
        'lifestyle': news_by_cat['Lifestyle'][:10],
        'politics': news_by_cat['Politics'][:7],
        'entertainment': news_by_cat['Entertainment'][:7],
        'now': now,
    }
    return render(request, 'news/news_home.html', context)
# ----------------------------------------------------------------------------||

def category_news(request, slug):
    last_week = timezone.now() - timedelta(days=7)
    category = get_object_or_404(Category, slug=slug)
    
    news_list_qs = News.objects.public().filter(
        category=category, 
        is_published=True
    ).distinct().order_by('-date_published') 

    first_article_id = None
    if news_list_qs.exists():
        first_article_id = news_list_qs.first().id

    # Pagination
    paginator = Paginator(news_list_qs, 10)
    page_number = request.GET.get('page')
    news_items = paginator.get_page(page_number)

    trending_news = News.objects.public().filter(
        is_published=True, 
        date_published__gte=last_week
    )

    if first_article_id:
        trending_news = trending_news.exclude(id=first_article_id)

    trending_news = trending_news.order_by('-views')[:5]

    all_categories = Category.objects.exclude(slug='').annotate(
        news_count=Count('news')
    ).order_by('-news_count')[:10]

    context = {
        'category': category,
        'news_items': news_items,
        'trending_news': trending_news,
        'all_categories': all_categories,
    }
    return render(request, 'news/category_list.html', context)


# ================================================================
# Enforces 3 comment submissions per minute based on their unique Cloudflare IP
@ratelimit(key=get_cloudflare_ip, rate='3/m', method='POST', block=False)
def news_detail(request, slug):
    last_week = timezone.now() - timedelta(days=7)
    News.objects.filter(slug=slug).update(views=F('views') + 1)
    news = get_object_or_404(News.objects.prefetch_related('category', 'tags'), slug=slug)

    article_content = insert_dynamic_ads(news.content)
    NewsView.objects.create(news=news)

    # ==================== COMMENT ==============
    if request.method == 'POST':

        is_staff = request.user.is_authenticated and request.user.is_staff

        # Rate Limit Guard
        if not is_staff:
            was_limited = getattr(request, 'limited', False)
            if was_limited:
                return JsonResponse({
                    "status": "error",
                    "message": "🔥 Slow down! You are posting too fast. Please wait a minute."
                }, status=429)

        # Honeypot
        honeypot_value = request.POST.get('user_website', '')
        if honeypot_value:
            return JsonResponse({
                "status": "success",
                "message": "Comment submitted successfully."
            })

        # AUTOMATED IP BLOCK INTEGRATION
        if not is_staff:
            # Resolve client IP matching your Cloudflare config strategy
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            client_ip = x_forwarded_for.split(',')[0].strip() if x_forwarded_for else request.META.get('REMOTE_ADDR')
            
            # Run cache monitor check
            from utils.monitor_ip import monitor_and_filter_ip
            if monitor_and_filter_ip(client_ip, action_type="comment"):
                return JsonResponse({
                    "status": "error",
                    "message": "🚫 Access Denied. Your IP footprint has been blacklisted for 24 hours due to spam behavior."
                }, status=403)

        # Link filter
        content_submitted = request.POST.get('content', '')
        if not is_staff:
            link_pattern = r'(https?://|www\.|<a\s+href|\[url\])'
            if re.search(link_pattern, content_submitted, re.IGNORECASE):
                return JsonResponse({
                    "status": "error",
                    "message": "Links are not allowed in comments."
                }, status=400)

        form = NewsCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.news = news

            # ================= IDENTITY RULE =================
            if is_staff:
                comment.user = request.user
                comment.name = request.user.get_full_name() or request.user.username
            else:
                forbidden_flags = ["admin", "vibenation", "staff", "moderator", "editor", "boss"]
                if any(flag in str(comment.name).lower() for flag in forbidden_flags):
                    comment.name = "Anonymous Fan"
            # ==========================================================

            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent_id = parent_id

            comment.save()

            # Render HTML
            if comment.parent_id:
                html_content = render_to_string(
                    'news/partials/news_reply.html',
                    {'reply': comment},
                    request=request
                )
            else:
                html_content = render_to_string(
                    'news/partials/news_comment.html',
                    {'comment': comment},
                    request=request
                )

            # ================= JSON RESPONSE =================
            response = JsonResponse({
                "status": "success",
                "message": "Comment posted successfully!",
                "html": html_content,
                "parent_id": comment.parent_id,
                "root_comment_id": comment.root_comment.id,
                "commenter_name": comment.name,
            })

            # COOKIE FIX
            if not is_staff:
                response.set_cookie(
                    'last_commenter_name',
                    comment.name,
                    max_age=60 * 60 * 24 * 30
                )

            return response

        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    "status": "error",
                    "errors": form.errors
                }, status=400)
            message.error(request, "There was an error with your comment submission")
            return HttpResponseRedirect(request.path)

    # ==================== GET REQUEST ====================
    if request.user.is_authenticated and request.user.is_staff:
        form = NewsCommentForm()
    else:
        last_name = request.COOKIES.get('last_commenter_name', '')
        form = NewsCommentForm(initial={'name': last_name} if last_name else None)

    # Sidebar data
    trending_news = (
        News.objects.public()
        .filter(date_published__gte=last_week)
        .exclude(id=news.id)
        .order_by('-views')[:5]
    )

    recent_songs = Song.objects.all().order_by('-release_date')[:4]

    all_categories = Category.objects.annotate(
        news_count=Count('news')
    ).order_by('-news_count')[:10]

    related_news = (
        News.objects.public()
        .filter(category__in=news.category.all())
        .exclude(id=news.id)
        .order_by('-date_published')
        .distinct()[:6]
    )

    comments_qs = (
        NewsComment.objects
        .filter(news=news, parent__isnull=True, is_approved=True)
        .prefetch_related('replies')
        .order_by('-created_at')
    )

    paginator = Paginator(comments_qs, 3)
    page_number = request.GET.get('page', 1)
    comments = paginator.get_page(page_number)

    context = {
        'news': news,
        'related_news': related_news,
        'trending_news': trending_news,
        'recent_songs': recent_songs,
        'all_categories': all_categories,
        'comments': comments,
        'form': form,
        'article_content': article_content,
    }

    return render(request, 'news/news_detail.html', context)
# ------------------------------------------------------------------------------


COMMENTS_PER_LOAD = 10
REPLIES_PER_LOAD = 3

def load_more_comments(request, news_id):
    offset = int(request.GET.get('offset', 0))
    news = get_object_or_404(News, id=news_id)

    all_parents = NewsComment.objects.filter(
        news=news, parent__isnull=True, is_approved=True
    ).order_by('-created_at')

    next_batch = all_parents[offset : offset + COMMENTS_PER_LOAD]
    
    html_output = ""
    for comment in next_batch:
        # FIXED PATH: news/partials/
        html_output += render_to_string(
            'news/partials/news_comment.html',
            {'comment': comment},
            request=request)

    return JsonResponse({
        'html': html_output,
        'has_more': all_parents.count() > (offset + COMMENTS_PER_LOAD)
    })
#=================================================================

def load_more_replies(request, comment_id):
    offset = int(request.GET.get('offset', 0))
    comment = get_object_or_404(NewsComment, id=comment_id)

    all_replies = comment.get_all_replies()
    replies = all_replies[offset : offset + REPLIES_PER_LOAD]

    # FIXED PATH: news/partials/
    html = render_to_string(
        'news/partials/reply_list.html',
        {'replies': replies},
        request=request
    )

    return JsonResponse({
        'html': html,
        'has_more': len(all_replies) > (offset + REPLIES_PER_LOAD)
    })



def news_by_tag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    news_qs = News.objects.public().filter(tags__in=[tag]).prefetch_related('category').order_by('-date_published')

    paginator = Paginator(news_qs, 10)
    page_number = request.GET.get('page')
    news_list = paginator.get_page(page_number)
    
    context = {
        'tag': tag, 
        'news_list': news_list,
        'page_title': f"News tagged: {tag.name} | VibeNation"
    }
    return render(request, 'news/news_by_tag.html', context)


@api_view(['GET'])
def entertainment(request):
    now = timezone.now()
    last_caching = now - timedelta(hours=12)
    strict_caching = now - timedelta(days=1444)

    # 1. Fetch Section Records
    featured_entertainment = News.objects.public().filter(
        category__name='Entertainment', 
        is_featured=True
    ).order_by('-date_published').first()

    sponsored_feature = News.objects.sponsored().filter(category__name='Entertainment').first()    
    top_pool = get_top_ranking('Entertainment', 'top_entertainment', last_caching, strict_caching)

    # 2. Extract Conditional Slices Based on Promotion States
    if sponsored_feature:
        top_entertainment = [n for n in top_pool if n.id != sponsored_feature.id][:4]
    else:
        top_entertainment = top_pool[:5]

    latest_pool = News.objects.public().filter(
        category__name='Entertainment', 
        is_featured=False
    ).order_by('-date_published')[:6]

    if sponsored_feature:
        latest_entertainment = [n for n in latest_pool if n.id != sponsored_feature.id][:5]
    else:
        latest_entertainment = latest_pool[:5]

    # 3. Deduplicate IDs
    used_ids = [n.id for n in top_entertainment] + [n.id for n in latest_entertainment]
    if featured_entertainment:
        used_ids.append(featured_entertainment.id)
    if sponsored_feature:
        used_ids.append(sponsored_feature.id)
    
    news_list_queryset = News.objects.public().filter(
        category__name='Entertainment', 
        is_featured=False,
        is_sponsored=False 
    ).order_by('-date_published')
    
    # 4. Handle Discovery Pool Slices
    other_news_pool = list(
        News.objects.public().exclude(category__name='Entertainment')
        .order_by('-date_published')[:20]
        .values_list('id', flat=True)
    )
    if other_news_pool:
        sample_ids = random.sample(other_news_pool, min(len(other_news_pool), 5))
        mini_featured_news = News.objects.public().filter(id__in=sample_ids).prefetch_related('category')
    else:
        mini_featured_news = []

    # 5. Process Pagination Blocks via Shared Pagination Config
    paginator = NewsPagination()
    paginated_queryset = paginator.paginate_queryset(news_list_queryset, request)

    serializer_context = {'request': request}
    return Response({
        "featured_entertainment": NewsSerializer(featured_entertainment, context=serializer_context).data if featured_entertainment else None,
        "sponsored_feature": NewsSerializer(sponsored_feature, context=serializer_context).data if sponsored_feature else None,
        "top_entertainment": NewsSerializer(top_entertainment, many=True, context=serializer_context).data,
        "latest_entertainment": NewsSerializer(latest_entertainment, many=True, context=serializer_context).data,
        "mini_featured_news": NewsSerializer(mini_featured_news, many=True, context=serializer_context).data,
        "paginated_grid": {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "current_page": paginator.page.number,
            "total_pages": paginator.page.paginator.num_pages,
            "results": NewsSerializer(paginated_queryset, many=True, context=serializer_context).data
        }
    })

def entertainment_frontend(request):
    return render(request, 'news/entertainment.html', {'current_category': 'Entertainment'})
# --------------------------------------------------------------------------------------------------------

@api_view(['GET'])
def politics(request):
    now = timezone.now()
    last_caching = now - timedelta(hours=12)
    strict_caching = now - timedelta(days=1444)

    # 1. Fetch Section Records
    featured_political = News.objects.public().filter(
        category__name='Politics', 
        is_featured=True
    ).order_by('-date_published').first()

    sponsored_feature = News.objects.sponsored().filter(category__name='Politics').first()    
    top_pool = get_top_ranking('Politics', 'top_political', last_caching, strict_caching)

    # 2. Extract Conditional Slices Based on Promotion States
    if sponsored_feature:
        top_political = [n for n in top_pool if n.id != sponsored_feature.id][:4]
    else:
        top_political = top_pool[:5]

    latest_pool = News.objects.public().filter(
        category__name='Politics', 
        is_featured=False
    ).order_by('-date_published')[:6]

    if sponsored_feature:
        latest_political = [n for n in latest_pool if n.id != sponsored_feature.id][:5]
    else:
        latest_political = latest_pool[:5]

    # 3. Deduplicate IDs to prevent clumping layout repetitions
    used_ids = [n.id for n in top_political] + [n.id for n in latest_political]
    if featured_political:
        used_ids.append(featured_political.id)
    if sponsored_feature:
        used_ids.append(sponsored_feature.id)
    
    # Base discovery list query feed
    news_list_queryset = News.objects.public().filter(
        category__name='Politics', 
        is_featured=False,
        is_sponsored=False 
    ).exclude(id__in=used_ids).order_by('-date_published')
    
    # 4. Handle Discovery Footer Slices
    other_news_pool = list(
        News.objects.public().exclude(category__name='Politics')
        .order_by('-date_published')[:20]
        .values_list('id', flat=True)
    )
    if other_news_pool:
        sample_ids = random.sample(other_news_pool, min(len(other_news_pool), 5))
        mini_featured_news = News.objects.public().filter(id__in=sample_ids).prefetch_related('category')
    else:
        mini_featured_news = []

    # 5. Process Pagination Slices Through the Paginator Instantiation
    paginator = NewsPagination()
    paginated_queryset = paginator.paginate_queryset(news_list_queryset, request)

    serializer_context = {'request': request}
    return Response({
        "featured_political": NewsSerializer(featured_political, context=serializer_context).data if featured_political else None,
        "sponsored_feature": NewsSerializer(sponsored_feature, context=serializer_context).data if sponsored_feature else None,
        "top_political": NewsSerializer(top_political, many=True, context=serializer_context).data,
        "latest_political": NewsSerializer(latest_political, many=True, context=serializer_context).data,
        "mini_featured_news": NewsSerializer(mini_featured_news, many=True, context=serializer_context).data,
        "paginated_grid": {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "current_page": paginator.page.number,
            "total_pages": paginator.page.paginator.num_pages,
            "results": NewsSerializer(paginated_queryset, many=True, context=serializer_context).data
        }
    })

def politics_frontend(request):
    """Serves the fast client-side skeleton layout directly to the user"""
    return render(request, 'news/politics.html', {'current_category': 'Politics'})
# ---------------------------------------------------------------------------

@api_view(['GET'])
def lifestyle(request):
    now = timezone.now()
    last_caching = now - timedelta(hours=12)
    strict_caching = now - timedelta(days=1444)

    # 1. Fetch Section Records
    featured_lifestyle = News.objects.public().filter(
        category__name='Lifestyle', 
        is_featured=True
    ).order_by('-date_published').first()

    sponsored_feature = News.objects.sponsored().filter(category__name='Lifestyle').first()    
    top_pool = get_top_ranking('Lifestyle', 'top_lifestyle', last_caching, strict_caching)

    # 2. Extract Slices based on promotion states
    if sponsored_feature:
        top_lifestyle = [n for n in top_pool if n.id != sponsored_feature.id][:4]
    else:
        top_lifestyle = top_pool[:5]

    latest_pool = News.objects.public().filter(
        category__name='Lifestyle', 
        is_featured=False
    ).order_by('-date_published')[:6]

    if sponsored_feature:
        latest_lifestyle = [n for n in latest_pool if n.id != sponsored_feature.id][:5]
    else:
        latest_lifestyle = latest_pool[:5]

    # 3. Deduplicate elements to keep layout clean
    used_ids = [n.id for n in top_lifestyle] + [n.id for n in latest_lifestyle]
    if featured_lifestyle:
        used_ids.append(featured_lifestyle.id)
    if sponsored_feature:
        used_ids.append(sponsored_feature.id)
    
    news_list_queryset = News.objects.public().filter(
        category__name='Lifestyle', 
        is_featured=False,
        is_sponsored=False 
    ).exclude(id__in=used_ids).order_by('-date_published')
    
    # 4. Handle Discovery Footer Slices
    other_news_pool = list(
        News.objects.public().exclude(category__name='Lifestyle')
        .order_by('-date_published')[:20]
        .values_list('id', flat=True)
    )
    if other_news_pool:
        sample_ids = random.sample(other_news_pool, min(len(other_news_pool), 5))
        mini_featured_news = News.objects.public().filter(id__in=sample_ids).prefetch_related('category')
    else:
        mini_featured_news = []

    # 5. Pipeline slices through DRF standard pagination instance
    paginator = NewsPagination()
    paginated_queryset = paginator.paginate_queryset(news_list_queryset, request)

    serializer_context = {'request': request}
    return Response({
        "featured_lifestyle": NewsSerializer(featured_lifestyle, context=serializer_context).data if featured_lifestyle else None,
        "sponsored_feature": NewsSerializer(sponsored_feature, context=serializer_context).data if sponsored_feature else None,
        "top_lifestyle": NewsSerializer(top_lifestyle, many=True, context=serializer_context).data,
        "latest_lifestyle": NewsSerializer(latest_lifestyle, many=True, context=serializer_context).data,
        "mini_featured_news": NewsSerializer(mini_featured_news, many=True, context=serializer_context).data,
        "paginated_grid": {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "current_page": paginator.page.number,
            "total_pages": paginator.page.paginator.num_pages,
            "results": NewsSerializer(paginated_queryset, many=True, context=serializer_context).data
        }
    })

def lifestyle_frontend(request):
    return render(request, 'news/lifestyle.html', {'current_category': 'Lifestyle'})
# -------------------------------------------------------------------

@api_view(['GET'])
def technology(request):
    now = timezone.now()
    last_caching = now - timedelta(hours=12)
    strict_caching = now - timedelta(days=1444)

    # 1. Gather Section Record Frameworks
    featured_technology = News.objects.public().filter(
        category__name='Technology', 
        is_featured=True
    ).order_by('-date_published').first()

    sponsored_feature = News.objects.sponsored().filter(category__name='Technology').first()    
    top_pool = get_top_ranking('Technology', 'top_technology', last_caching, strict_caching)

    # 2. Extract Data Slices Relative to Advertising States
    if sponsored_feature:
        top_technology = [n for n in top_pool if n.id != sponsored_feature.id][:4]
    else:
        top_technology = top_pool[:5]

    latest_pool = News.objects.public().filter(
        category__name='Technology', 
        is_featured=False
    ).order_by('-date_published')[:6]

    if sponsored_feature:
        latest_technology = [n for n in latest_pool if n.id != sponsored_feature.id][:5]
    else:
        latest_technology = latest_pool[:5]

    # 3. Prevent Duplications Across Interactive Blocks
    used_ids = [n.id for n in top_technology] + [n.id for n in latest_technology]
    if featured_technology:
        used_ids.append(featured_technology.id)
    if sponsored_feature:
        used_ids.append(sponsored_feature.id)
    
    news_list_queryset = News.objects.public().filter(
        category__name='Technology', 
        is_featured=False,
        is_sponsored=False 
    ).exclude(id__in=used_ids).order_by('-date_published')
    
    # 4. Handle Discovery Footer Slices
    other_news_pool = list(
        News.objects.public().exclude(category__name='Technology')
        .order_by('-date_published')[:20]
        .values_list('id', flat=True)
    )
    if other_news_pool:
        sample_ids = random.sample(other_news_pool, min(len(other_news_pool), 5))
        mini_featured_news = News.objects.public().filter(id__in=sample_ids).prefetch_related('category')
    else:
        mini_featured_news = []

    # 5. Hand over Main Grid Query to the DRF Paginator Engine
    paginator = NewsPagination()
    paginated_queryset = paginator.paginate_queryset(news_list_queryset, request)

    serializer_context = {'request': request}
    return Response({
        "featured_technology": NewsSerializer(featured_technology, context=serializer_context).data if featured_technology else None,
        "sponsored_feature": NewsSerializer(sponsored_feature, context=serializer_context).data if sponsored_feature else None,
        "top_technology": NewsSerializer(top_technology, many=True, context=serializer_context).data,
        "latest_technology": NewsSerializer(latest_technology, many=True, context=serializer_context).data,
        "mini_featured_news": NewsSerializer(mini_featured_news, many=True, context=serializer_context).data,
        "paginated_grid": {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "current_page": paginator.page.number,
            "total_pages": paginator.page.paginator.num_pages,
            "results": NewsSerializer(paginated_queryset, many=True, context=serializer_context).data
        }
    })

def technology_frontend(request):
    """Instantly hands off the static structural layout skeleton to the browser"""
    return render(request, 'news/technology.html', {'current_category': 'Technology'})

@api_view(['GET'])
def music_news(request):
    now = timezone.now()
    last_caching = now - timedelta(hours=12)
    strict_caching = now - timedelta(days=1444)

    # 1. Query Dataset Shells
    featured_music_news = News.objects.public().filter(
        category__name='Music News', 
        is_featured=True
    ).order_by('-date_published').first()

    sponsored_feature = News.objects.sponsored().filter(category__name='Music News').first()    
    top_pool = get_top_ranking('Music News', 'top_music_news', last_caching, strict_caching)

    # 2. Extract Display Windows
    if sponsored_feature:
        top_music_news = [n for n in top_pool if n.id != sponsored_feature.id][:4]
    else:
        top_music_news = top_pool[:5]

    latest_pool = News.objects.public().filter(
        category__name='Music News', 
        is_featured=False
    ).order_by('-date_published')[:6]

    if sponsored_feature:
        latest_music_news = [n for n in latest_pool if n.id != sponsored_feature.id][:5]
    else:
        latest_music_news = latest_pool[:5]

    # 3. Deduplicate Content IDs across sections
    used_ids = [n.id for n in top_music_news] + [n.id for n in latest_music_news]
    if featured_music_news:
        used_ids.append(featured_music_news.id)
    if sponsored_feature:
        used_ids.append(sponsored_feature.id)
    
    news_list_queryset = News.objects.public().filter(
        category__name='Music News', 
        is_featured=False,
        is_sponsored=False 
    ).exclude(id__in=used_ids).order_by('-date_published')
    
    # 4. Pull Footer Discovery Stories
    other_news_pool = list(
        News.objects.public().exclude(category__name='Music News')
        .order_by('-date_published')[:20]
        .values_list('id', flat=True)
    )
    if other_news_pool:
        sample_ids = random.sample(other_news_pool, min(len(other_news_pool), 5))
        mini_featured_news = News.objects.public().filter(id__in=sample_ids).prefetch_related('category')
    else:
        mini_featured_news = []

    # 5. Hand Over Main Feed Query to DRF Pagination Engine
    paginator = NewsPagination()
    paginated_queryset = paginator.paginate_queryset(news_list_queryset, request)

    serializer_context = {'request': request}
    return Response({
        "featured_music_news": NewsSerializer(featured_music_news, context=serializer_context).data if featured_music_news else None,
        "sponsored_feature": NewsSerializer(sponsored_feature, context=serializer_context).data if sponsored_feature else None,
        "top_music_news": NewsSerializer(top_music_news, many=True, context=serializer_context).data,
        "latest_music_news": NewsSerializer(latest_music_news, many=True, context=serializer_context).data,
        "mini_featured_news": NewsSerializer(mini_featured_news, many=True, context=serializer_context).data,
        "paginated_grid": {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "current_page": paginator.page.number,
            "total_pages": paginator.page.paginator.num_pages,
            "results": NewsSerializer(paginated_queryset, many=True, context=serializer_context).data
        }
    })

def music_news_frontend(request):
    """Instantly delivers the empty wireframe shell to keep transitions fast"""
    return render(request, 'news/music_news.html', {'current_category': 'Music News'})
# --------------------------------------------------------------------


@api_view(['GET'])
def sports(request):
    now = timezone.now()
    last_caching = now - timedelta(hours=12)
    strict_caching = now - timedelta(days=1444)

    # 1. Fetch Section Records
    featured_sport = News.objects.public().filter(
        category__name='Sports', 
        is_featured=True
    ).order_by('-date_published').first()

    sponsored_feature = News.objects.sponsored().filter(category__name='Sports').first()    
    top_pool = get_top_ranking('Sports', 'top_sport', last_caching, strict_caching)

    # 2. Extract Slices based on promotion states
    if sponsored_feature:
        top_sport = [n for n in top_pool if n.id != sponsored_feature.id][:4]
    else:
        top_sport = top_pool[:5]

    latest_pool = News.objects.public().filter(
        category__name='Sports', 
        is_featured=False
    ).order_by('-date_published')[:6]

    if sponsored_feature:
        latest_sport = [n for n in latest_pool if n.id != sponsored_feature.id][:5]
    else:
        latest_sport = latest_pool[:5]

    # 3. Deduplicate elements to keep layout clean
    used_ids = [n.id for n in top_sport] + [n.id for n in latest_sport]
    if featured_sport:
        used_ids.append(featured_sport.id)
    if sponsored_feature:
        used_ids.append(sponsored_feature.id)
    
    news_list_queryset = News.objects.public().filter(
        category__name='Sports', 
        is_featured=False,
        is_sponsored=False 
    ).exclude(id__in=used_ids).order_by('-date_published')
    
    # 4. Handle Discovery Footer Slices
    other_news_pool = list(
        News.objects.public().exclude(category__name='Sports')
        .order_by('-date_published')[:20]
        .values_list('id', flat=True)
    )
    if other_news_pool:
        sample_ids = random.sample(other_news_pool, min(len(other_news_pool), 5))
        mini_featured_news = News.objects.public().filter(id__in=sample_ids).prefetch_related('category')
    else:
        mini_featured_news = []

    # 5. Pipeline slices through DRF standard pagination instance
    paginator = NewsPagination()
    paginated_queryset = paginator.paginate_queryset(news_list_queryset, request)

    serializer_context = {'request': request}
    return Response({
        "featured_sport": NewsSerializer(featured_sport, context=serializer_context).data if featured_sport else None,
        "sponsored_feature": NewsSerializer(sponsored_feature, context=serializer_context).data if sponsored_feature else None,
        "top_sport": NewsSerializer(top_sport, many=True, context=serializer_context).data,
        "latest_sport": NewsSerializer(latest_sport, many=True, context=serializer_context).data,
        "mini_featured_news": NewsSerializer(mini_featured_news, many=True, context=serializer_context).data,
        "paginated_grid": {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "current_page": paginator.page.number,
            "total_pages": paginator.page.paginator.num_pages,
            "results": NewsSerializer(paginated_queryset, many=True, context=serializer_context).data
        }
    })

def sports_frontend(request):
    """Returns the single skeleton layout interface frame instantly"""
    return render(request, 'news/sport_news.html', {'current_category': 'Sports'})
# -----------------------------------------------------------------------

@api_view(['GET'])
def events(request):
    now = timezone.now()
    last_caching = now - timedelta(hours=12)
    strict_caching = now - timedelta(days=1444)

    # 1. Gather Section Record Frameworks
    featured_event = News.objects.public().filter(
        category__name='Events', 
        is_featured=True
    ).order_by('-date_published').first()

    sponsored_feature = News.objects.sponsored().filter(category__name='Events').first()    
    top_pool = get_top_ranking('Events', 'top_event', last_caching, strict_caching)

    # 2. Extract Data Slices Relative to Advertising States
    if sponsored_feature:
        top_event = [n for n in top_pool if n.id != sponsored_feature.id][:4]
    else:
        top_event = top_pool[:5]

    latest_pool = News.objects.public().filter(
        category__name='Events', 
        is_featured=False
    ).order_by('-date_published')[:6]

    if sponsored_feature:
        latest_event = [n for n in latest_pool if n.id != sponsored_feature.id][:5]
    else:
        latest_event = latest_pool[:5]

    # 3. Prevent Duplications Across Interactive Blocks
    used_ids = [n.id for n in top_event] + [n.id for n in latest_event]
    if featured_event:
        used_ids.append(featured_event.id)
    if sponsored_feature:
        used_ids.append(sponsored_feature.id)
    
    news_list_queryset = News.objects.public().filter(
        category__name='Events', 
        is_featured=False,
        is_sponsored=False 
    ).exclude(id__in=used_ids).order_by('-date_published')
    
    # 4. Handle Discovery Footer Slices
    other_news_pool = list(
        News.objects.public().exclude(category__name='Events')
        .order_by('-date_published')[:20]
        .values_list('id', flat=True)
    )
    if other_news_pool:
        sample_ids = random.sample(other_news_pool, min(len(other_news_pool), 5))
        mini_featured_news = News.objects.public().filter(id__in=sample_ids).prefetch_related('category')
    else:
        mini_featured_news = []

    # 5. Hand over Main Grid Query to the DRF Paginator Engine
    paginator = NewsPagination()
    paginated_queryset = paginator.paginate_queryset(news_list_queryset, request)

    serializer_context = {'request': request}
    return Response({
        "featured_event": NewsSerializer(featured_event, context=serializer_context).data if featured_event else None,
        "sponsored_feature": NewsSerializer(sponsored_feature, context=serializer_context).data if sponsored_feature else None,
        "top_event": NewsSerializer(top_event, many=True, context=serializer_context).data,
        "latest_event": NewsSerializer(latest_event, many=True, context=serializer_context).data,
        "mini_featured_news": NewsSerializer(mini_featured_news, many=True, context=serializer_context).data,
        "paginated_grid": {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "current_page": paginator.page.number,
            "total_pages": paginator.page.paginator.num_pages,
            "results": NewsSerializer(paginated_queryset, many=True, context=serializer_context).data
        }
    })

def events_frontend(request):
    """Instantly delivers the empty wireframe shell to keep transitions fast"""
    return render(request, 'news/event.html', {'current_category': 'Events'})
# ------------------------------------------------------------------------

@api_view(['GET'])
def education(request):
    now = timezone.now()
    last_caching = now - timedelta(hours=12)
    strict_caching = now - timedelta(days=1444)

    # 1. Query Dataset Shells
    featured_education = News.objects.public().filter(
        category__name='Education', 
        is_featured=True
    ).order_by('-date_published').first()

    sponsored_feature = News.objects.sponsored().filter(category__name='Education').first()    
    top_pool = get_top_ranking('Education', 'top_education', last_caching, strict_caching)

    # 2. Extract Display Windows
    if sponsored_feature:
        top_education = [n for n in top_pool if n.id != sponsored_feature.id][:4]
    else:
        top_education = top_pool[:5]

    latest_pool = News.objects.public().filter(
        category__name='Education', 
        is_featured=False
    ).order_by('-date_published')[:6]

    if sponsored_feature:
        latest_education = [n for n in latest_pool if n.id != sponsored_feature.id][:5]
    else:
        latest_education = latest_pool[:5]

    # 3. Deduplicate Content IDs across sections
    used_ids = [n.id for n in top_education] + [n.id for n in latest_education]
    if featured_education:
        used_ids.append(featured_education.id)
    if sponsored_feature:
        used_ids.append(sponsored_feature.id)
    
    news_list_queryset = News.objects.public().filter(
        category__name='Education', 
        is_featured=False,
        is_sponsored=False 
    ).exclude(id__in=used_ids).order_by('-date_published')
    
    # 4. Pull Footer Discovery Stories
    other_news_pool = list(
        News.objects.public().exclude(category__name='Education')
        .order_by('-date_published')[:20]
        .values_list('id', flat=True)
    )
    if other_news_pool:
        sample_ids = random.sample(other_news_pool, min(len(other_news_pool), 5))
        mini_featured_news = News.objects.public().filter(id__in=sample_ids).prefetch_related('category')
    else:
        mini_featured_news = []

    # 5. Hand Over Main Feed Query to DRF Pagination Engine
    paginator = NewsPagination()
    paginated_queryset = paginator.paginate_queryset(news_list_queryset, request)

    serializer_context = {'request': request}
    return Response({
        "featured_education": NewsSerializer(featured_education, context=serializer_context).data if featured_education else None,
        "sponsored_feature": NewsSerializer(sponsored_feature, context=serializer_context).data if sponsored_feature else None,
        "top_education": NewsSerializer(top_education, many=True, context=serializer_context).data,
        "latest_education": NewsSerializer(latest_education, many=True, context=serializer_context).data,
        "mini_featured_news": NewsSerializer(mini_featured_news, many=True, context=serializer_context).data,
        "paginated_grid": {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "current_page": paginator.page.number,
            "total_pages": paginator.page.paginator.num_pages,
            "results": NewsSerializer(paginated_queryset, many=True, context=serializer_context).data
        }
    })

def education_frontend(request):
    return render(request, 'news/education.html', {'current_category': 'Education'})
# -----------------------------------------------------------------------

@api_view(['GET'])
def opinion(request):
    last_caching = timezone.now() - timedelta(hours=12)
    strict_caching = timezone.now() - timedelta(days=1444) 
    
    # Gather Section Entities
    featured_opinion = News.objects.public().filter(
        category__name='Opinion', 
        is_featured=True
    ).order_by('-date_published').first()
    
    top_opinion = get_top_ranking('Opinion', 'top_opinion', last_caching, strict_caching)

    latest_opinion = News.objects.public().filter(
        category__name='Opinion', 
        is_featured=False
    ).order_by('-date_published')[:5]

    # Exclude Duplicate Records
    used_ids = [n.id for n in top_opinion] + [n.id for n in latest_opinion]
    if featured_opinion:
        used_ids.append(featured_opinion.id)
    
    news_list_queryset = News.objects.public().filter(
        category__name='Opinion', 
        is_featured=False
    ).exclude(id__in=used_ids).order_by('-date_published')
    
    # Handle Random Discovery Pool
    other_news_pool = list(
        News.objects.public().exclude(category__name='Opinion')
        .order_by('-date_published')[:20]
        .values_list('id', flat=True)
    )
    
    if other_news_pool:
        sample_ids = random.sample(other_news_pool, min(len(other_news_pool), 5))
        mini_featured_news = News.objects.public().filter(id__in=sample_ids).prefetch_related('category')
    else:
        mini_featured_news = []

    # Process Paginated Records via DRF Engine
    paginator = NewsPagination()
    paginated_queryset = paginator.paginate_queryset(news_list_queryset, request)

    # Build Final Serialized Payload
    serializer_context = {'request': request}
    return Response({
        "featured_opinion": NewsSerializer(featured_opinion, context=serializer_context).data if featured_opinion else None,
        "top_opinion": NewsSerializer(top_opinion, many=True, context=serializer_context).data,
        "latest_opinion": NewsSerializer(latest_opinion, many=True, context=serializer_context).data,
        "mini_featured_news": NewsSerializer(mini_featured_news, many=True, context=serializer_context).data,
        "paginated_grid": {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "current_page": paginator.page.number,
            "total_pages": paginator.page.paginator.num_pages,
            "results": NewsSerializer(paginated_queryset, many=True, context=serializer_context).data
        }
    })

def opinion_frontend(request):
    # Simply hands off the skeleton. Data is loaded asynchronously.
    return render(request, 'news/opinion.html', {'current_category': 'Opinion'})

@api_view(['GET'])
def news_by_tag(request, tag_slug):
    # Retrieve the tag metadata object
    tag = get_object_or_404(Tag, slug=tag_slug)
    
    # Query matching organic records
    news_list_queryset = (
        News.objects.public()
        .filter(tags=tag)
        .order_by('-date_published')
    )

    # Pass over to DRF Paginator Engine
    paginator = NewsPagination()
    paginator.page_size = 20 # Overriding default to match your original configuration constraint size of 20
    paginated_queryset = paginator.paginate_queryset(news_list_queryset, request)

    serializer_context = {'request': request}
    return Response({
        "tag": {
            "name": tag.name,
            "slug": tag.slug
        },
        "paginated_grid": {
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "current_page": paginator.page.number,
            "total_pages": paginator.page.paginator.num_pages,
            "results": NewsSerializer(paginated_queryset, many=True, context=serializer_context).data
        }
    })

def news_by_tag_frontend(request, tag_slug):
    return render(request, 'news/news_by_tag.html', {'tag_slug': tag_slug})