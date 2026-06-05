from django.shortcuts import render, get_object_or_404, redirect
from .models import News, Category, NewsView, NewsComment
from music.models import Song
from django.core.paginator import Paginator
from taggit.models import Tag
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from django.db.models import Count, Q, F
import random
from .forms import NewsCommentForm
from django.template.loader import render_to_string
from django.http import JsonResponse
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

def news_detail(request, slug):
    last_week = timezone.now() - timedelta(days=7)
    news = get_object_or_404(News.objects.prefetch_related('category', 'tags'), slug=slug)

    # Process the content through the utility once
    article_content = insert_dynamic_ads(news.content)
    
    # Increment views
    News.objects.filter(id=news.id).update(views=F('views') + 1)
    NewsView.objects.create(news=news)

    # trending now
    trending_news = (
        News.objects.public().filter(date_published__gte=last_week)
        .exclude(id=news.id)
        .order_by('-views')[:5]
    )

    recent_songs = Song.objects.all().order_by('-release_date')[:4]

    all_categories = Category.objects.annotate(
        news_count=Count('news')
        ).order_by('-news_count')[:10]
    
    # Optimized Related News
    related_news = (
        News.objects.public().filter(category__in=news.category.all())
        .exclude(id=news.id)
        .order_by('-date_published') 
        .distinct()[:6]
    )

    # COMMENT SYSTEM 
    if request.method == 'POST':
        form = NewsCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.news = news

            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent_id = parent_id

            comment.save()
            response = redirect(request.path)
            
            response.set_cookie(
                'last_commenter_name',
                comment.name,
                max_age=60 * 60 * 24 * 30
            )
            return response
    else:
        last_name = request.COOKIES.get('last_commenter_name')
        form = NewsCommentForm(initial={'name': last_name} if last_name else None)

    # Pagination & Comments (Top-level only)
    comments_qs = (
        NewsComment.objects
        .filter(news=news, parent__isnull=True, is_approved=True)
        .prefetch_related('replies') 
        .order_by('-created_at')
    )

    paginator = Paginator(comments_qs, 2)
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


def entertainment(request):
    now = timezone.now()
    last_caching = now - timedelta(hours=12)  # Window for "Trending" calculation
    strict_caching = now - timedelta(days=14) # How far back to look for top news

    # Featured news
    featured_entertainment = News.objects.public().filter(
        category__name='Entertainment', 
        is_featured=True
    ).order_by('-date_published').first()

    sponsored_feature = News.objects.sponsored().filter(category__name='Entertainment').first()    
    
    # TOP RANKING fetching 6 through helper function
    top_pool = get_top_ranking('Entertainment', 'top_entertainment', last_caching, strict_caching)

    # filtering sponsored post
    if sponsored_feature:
        top_entertainment = [n for n in top_pool if n.id != sponsored_feature.id][:4]
    else:
        top_entertainment = top_pool[:5]

    # 5. LATEST NEWS (SIDEBAR) LOGIC
    latest_pool = News.objects.public().filter(
        category__name='Entertainment', 
        is_featured=False
    ).order_by('-date_published')[:6]

    if sponsored_feature:
        latest_entertainment = [n for n in latest_pool if n.id != sponsored_feature.id][:5]
    else:
        latest_entertainment = latest_pool[:5]

    # Prevent news from top section to show in news list
    used_ids = [n.id for n in top_entertainment]
    used_ids += [n.id for n in latest_entertainment]
    
    if featured_entertainment:
        used_ids.append(featured_entertainment.id)
    if sponsored_feature:
        used_ids.append(sponsored_feature.id)
    
    # Main news list of the category
    news_list = News.objects.public().filter(
        category__name='Entertainment', 
        is_featured=False,
        is_sponsored=False 
    ).exclude(id__in=used_ids).order_by('-date_published')
    
    # Random from other categories
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

    # PAGINATION
    paginator = Paginator(news_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'featured_entertainment': featured_entertainment,
        'sponsored_feature': sponsored_feature,
        'top_entertainment': top_entertainment,
        'latest_entertainment': latest_entertainment,
        'page_obj': page_obj,
        'mini_featured_news': mini_featured_news,
        'current_category': 'Entertainment',
    }
    return render(request, 'news/entertainment.html', context)


def politics(request):
    now = timezone.now()
    last_caching = now - timedelta(hours=12)
    strict_caching = now - timedelta(days=14)

    # Featured news
    featured_political = News.objects.public().filter(
        category__name='Politics', 
        is_featured=True
    ).order_by('-date_published').first()

    # sponsored post
    sponsored_feature = News.objects.sponsored().filter(category__name='Politics').first()    

    
    # TOP RANKING fetching 6 through helper function
    top_pool = get_top_ranking('Politics', 'top_political', last_caching, strict_caching)

    # filtering sponsored post
    if sponsored_feature:
        top_political = [n for n in top_pool if n.id != sponsored_feature.id][:4]
    else:
        top_political = top_pool[:5]

    # Latest Political
    latest_pool = News.objects.public().filter(
        category__name='Politics', 
        is_featured=False,
    ).order_by('-date_published')[:6]

    if sponsored_feature:
        latest_political = [n for n in latest_pool if n.id != sponsored_feature.id][:5]
    else:
        latest_political = latest_pool[:5]

    # Prevent news from top section to news list
    used_ids = [n.id for n in top_political]
    used_ids += [n.id for n in latest_political]
    
    if featured_political:
        used_ids.append(featured_political.id)
    if sponsored_feature:
        used_ids.append(sponsored_feature.id)
    
    # Main news list of the category
    news_list = News.objects.public().filter(
        category__name='Politics', 
        is_featured=False,
        is_sponsored=False
    ).exclude(id__in=used_ids).order_by('-date_published')
    
    # Random from other categories
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

    # PAGINATION
    paginator = Paginator(news_list, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'featured_political': featured_political,
        'sponsored_feature': sponsored_feature,
        'top_political': top_political,
        'latest_political': latest_political,
        'page_obj': page_obj,
        'mini_featured_news': mini_featured_news,
        'current_category': 'Politics',
    }
    return render(request, 'news/politics.html', context)
# ---------------------------------------------------------------------------


def lifestyle(request):
    now = timezone.now()
    last_caching = now - timedelta(hours=12)
    strict_caching = now - timedelta(days=14)

    # Featured news
    featured_lifestyle = News.objects.public().filter(
        category__name='Lifestyle', 
        is_featured=True
    ).order_by('-date_published').first()

    # sponsored post
    sponsored_feature = News.objects.sponsored().filter(category__name='Lifestyle').first()    

    
    # TOP RANKING fetching 6 through helper function
    top_pool = get_top_ranking('Lifestyle', 'top_lifestyle', last_caching, strict_caching)

    # filtering sponsored post
    if sponsored_feature:
        top_lifestyle = [n for n in top_pool if n.id != sponsored_feature.id][:4]
    else:
        top_lifestyle = top_pool[:5]

    # Latest Lifestyle News
    latest_pool = News.objects.public().filter(
        category__name='Lifestyle', 
        is_featured=False,
    ).order_by('-date_published')[:6]

    if sponsored_feature:
        latest_lifestyle = [n for n in latest_pool if n.id != sponsored_feature.id][:5]
    else:
        latest_lifestyle = latest_pool[:5]

    # Prevent news from top section to news list
    used_ids = [n.id for n in top_lifestyle]
    used_ids += [n.id for n in latest_lifestyle]
    
    if featured_lifestyle:
        used_ids.append(featured_lifestyle.id)
    if sponsored_feature:
        used_ids.append(sponsored_feature.id)
    
    # Main news list of the category
    news_list = News.objects.public().filter(
        category__name='Lifestyle', 
        is_featured=False,
        is_sponsored=False
    ).exclude(id__in=used_ids).order_by('-date_published')
    
    # Random from other categories
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

    # PAGINATION
    paginator = Paginator(news_list, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'featured_lifestyle': featured_lifestyle,
        'sponsored_feature': sponsored_feature,
        'top_lifestyle': top_lifestyle,
        'latest_lifestyle': latest_lifestyle,
        'page_obj': page_obj,
        'mini_featured_news': mini_featured_news,
        'current_category': 'Lifestyle',
    }
    return render(request, 'news/lifestyle.html', context)

# -------------------------------------------------------------------

def technology(request):
    now = timezone.now()
    last_caching = now - timedelta(hours=12)
    strict_caching = now - timedelta(days=14)

    # Featured news
    featured_technology = News.objects.public().filter(
        category__name='Technology', 
        is_featured=True
    ).order_by('-date_published').first()

    # sponsored post
    sponsored_feature = News.objects.sponsored().filter(category__name='Technology').first()
    
    # TOP RANKING fetching 6 through helper function
    top_pool = get_top_ranking('Technology', 'top_technology', last_caching, strict_caching)

    # filtering sponsored post
    if sponsored_feature:
        top_technology = [n for n in top_pool if n.id != sponsored_feature.id][:4]
    else:
        top_technology = top_pool[:5]

    # Latest Tech News
    latest_pool = News.objects.public().filter(
        category__name='Technology', 
        is_featured=False,
    ).order_by('-date_published')[:6]

    if sponsored_feature:
        latest_technology = [n for n in latest_pool if n.id != sponsored_feature.id][:5]
    else:
        latest_technology = latest_pool[:5]

    # Prevent news from top section to news list
    used_ids = [n.id for n in top_technology]
    used_ids += [n.id for n in latest_technology]
    
    if featured_technology:
        used_ids.append(featured_technology.id)
    if sponsored_feature:
        used_ids.append(sponsored_feature.id)
    
    # Main news list of the category
    news_list = News.objects.public().filter(
        category__name='Technology', 
        is_featured=False,
        is_sponsored=False
    ).exclude(id__in=used_ids).order_by('-date_published')
    
    # Random from other categories
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

    # PAGINATION
    paginator = Paginator(news_list, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'featured_technology': featured_technology,
        'sponsored_feature': sponsored_feature,
        'top_technology': top_technology,
        'latest_technology': latest_technology,
        'page_obj': page_obj,
        'mini_featured_news': mini_featured_news,
        'current_category': 'Technology',
    }
    return render(request, 'news/technology.html', context)

def music_news(request):
    now = timezone.now()
    last_caching = now - timedelta(hours=12)
    strict_caching = now - timedelta(days=14)

    # Featured news
    featured_music_news = News.objects.public().filter(
        category__name='Music News', 
        is_featured=True
    ).order_by('-date_published').first()

    # sponsored post
    sponsored_feature = News.objects.sponsored().filter(category__name='Music News').first()
    
    # TOP RANKING fetching 6 through helper function
    top_pool = get_top_ranking('Music News', 'top_music_news', last_caching, strict_caching)

    # filtering sponsored post
    if sponsored_feature:
        top_music_news = [n for n in top_pool if n.id != sponsored_feature.id][:4]
    else:
        top_music_news = top_pool[:5]

    # Latest Music News
    latest_pool = News.objects.public().filter(
        category__name='Music News', 
        is_featured=False,
    ).order_by('-date_published')[:6]

    if sponsored_feature:
        latest_music_news = [n for n in latest_pool if n.id != sponsored_feature.id][:5]
    else:
        latest_music_news = latest_pool[:5]

    # Prevent news from top section to news list
    used_ids = [n.id for n in top_music_news]
    used_ids += [n.id for n in latest_music_news]
    
    if featured_music_news:
        used_ids.append(featured_music_news.id)
    if sponsored_feature:
        used_ids.append(sponsored_feature.id)
    
    # Main news list of the category
    news_list = News.objects.public().filter(
        category__name='Music News', 
        is_featured=False,
        is_sponsored=False
    ).exclude(id__in=used_ids).order_by('-date_published')
    
    # Random from other categories
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

    # PAGINATION
    paginator = Paginator(news_list, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'featured_music_news': featured_music_news,
        'sponsored_feature': sponsored_feature,
        'top_music_news': top_music_news,
        'latest_music_news': latest_music_news,
        'page_obj': page_obj,
        'mini_featured_news': mini_featured_news,
        'current_category': 'Music News',
    }
    return render(request, 'news/music_news.html', context)
# --------------------------------------------------------------------


def sport(request):
    now = timezone.now()
    last_caching = now - timedelta(hours=12)
    strict_caching = now - timedelta(days=14)

    # Featured news
    featured_sport = News.objects.public().filter(
        category__name='Sports', 
        is_featured=True
    ).order_by('-date_published').first()

    # sponsored post
    sponsored_feature = News.objects.sponsored().filter(category__name='Sports').first()
    
    # TOP RANKING fetching 6 through helper function
    top_pool = get_top_ranking('Sports', 'top_sport', last_caching, strict_caching)

    # filtering sponsored post
    if sponsored_feature:
        top_sport = [n for n in top_pool if n.id != sponsored_feature.id][:4]
    else:
        top_sport = top_pool[:5]

    # Latest Sport News
    latest_pool = News.objects.public().filter(
        category__name='Sports', 
        is_featured=False,
    ).order_by('-date_published')[:6]

    if sponsored_feature:
        latest_sport = [n for n in latest_pool if n.id != sponsored_feature.id][:5]
    else:
        latest_sport = latest_pool[:5]

    # Prevent news from top section to news list
    used_ids = [n.id for n in top_sport]
    used_ids += [n.id for n in latest_sport]
    
    if featured_sport:
        used_ids.append(featured_sport.id)
    if sponsored_feature:
        used_ids.append(sponsored_feature.id)
    
    # Main news list of the category
    news_list = News.objects.public().filter(
        category__name='Sports', 
        is_featured=False,
        is_sponsored=False
    ).exclude(id__in=used_ids).order_by('-date_published')
    
    # Random from other categories
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

    # PAGINATION
    paginator = Paginator(news_list, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'featured_sport': featured_sport,
        'sponsored_feature': sponsored_feature,
        'top_sport': top_sport,
        'latest_sport': latest_sport,
        'page_obj': page_obj,
        'mini_featured_news': mini_featured_news,
        'current_category': 'Sport',
    }
    return render(request, 'news/sport_news.html', context)
# -----------------------------------------------------------------------

def event(request):
    now = timezone.now()
    last_caching = now - timedelta(hours=12)
    strict_caching = now - timedelta(days=14)

    # Featured news
    featured_event = News.objects.public().filter(
        category__name='Events', 
        is_featured=True
    ).order_by('-date_published').first()

    # sponsored post
    sponsored_feature = News.objects.sponsored().filter(category__name='Events').first()
    
    # TOP RANKING fetching 6 through helper function
    top_pool = get_top_ranking('Events', 'top_event', last_caching, strict_caching)

    # filtering sponsored post
    if sponsored_feature:
        top_event = [n for n in top_pool if n.id != sponsored_feature.id][:4]
    else:
        top_event = top_pool[:5]

    # Latest Event
    latest_pool = News.objects.public().filter(
        category__name='Events', 
        is_featured=False,
    ).order_by('-date_published')[:6]

    if sponsored_feature:
        latest_event = [n for n in latest_pool if n.id != sponsored_feature.id][:5]
    else:
        latest_event = latest_pool[:5]

    # Prevent news from top section to news list
    used_ids = [n.id for n in top_event]
    used_ids += [n.id for n in latest_event]
    
    if featured_event:
        used_ids.append(featured_event.id)
    if sponsored_feature:
        used_ids.append(sponsored_feature.id)
    
    # Main news list of the category
    news_list = News.objects.public().filter(
        category__name='Events', 
        is_featured=False,
        is_sponsored=False
    ).exclude(id__in=used_ids).order_by('-date_published')
    
    # Random from other categories
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

    # PAGINATION
    paginator = Paginator(news_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'featured_event': featured_event,
        'sponsored_feature': sponsored_feature,
        'top_event': top_event,
        'latest_event': latest_event,
        'page_obj': page_obj,
        'mini_featured_news': mini_featured_news,
        'current_category': 'Event',
    }
    return render(request, 'news/event.html', context)
# ------------------------------------------------------------------------


def education(request):
    now = timezone.now()
    last_caching = now - timedelta(hours=12)
    strict_caching = now - timedelta(days=14)

    # Featured news
    featured_education = News.objects.public().filter(
        category__name='Education', 
        is_featured=True
    ).order_by('-date_published').first()

    # sponsored post
    sponsored_feature = News.objects.sponsored().filter(category__name='Education').first()
    
    # TOP RANKING fetching 6 through helper function
    top_pool = get_top_ranking('Education', 'top_education', last_caching, strict_caching)

    # filtering sponsored post
    if sponsored_feature:
        top_education = [n for n in top_pool if n.id != sponsored_feature.id][:4]
    else:
        top_education = top_pool[:5]

    # Latest Education
    latest_pool = News.objects.public().filter(
        category__name='Education', 
        is_featured=False,
    ).order_by('-date_published')[:6]

    if sponsored_feature:
        latest_education = [n for n in latest_pool if n.id != sponsored_feature.id][:5]
    else:
        latest_education = latest_pool[:5]

    # Prevent news from top section to news list
    used_ids = [n.id for n in top_education]
    used_ids += [n.id for n in latest_education]
    
    if featured_education:
        used_ids.append(featured_education.id)
    if sponsored_feature:
        used_ids.append(sponsored_feature.id)
    
    # Main news list of the category
    news_list = News.objects.public().filter(
        category__name='Education', 
        is_featured=False,
        is_sponsored=False
    ).exclude(id__in=used_ids).order_by('-date_published')

    # Mini-Featured Random from Latest 20
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

    # Pagination
    paginator = Paginator(news_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'featured_education': featured_education,
        'sponsored_feature': sponsored_feature,
        'top_education': top_education,
        'latest_education': latest_education,
        'page_obj': page_obj,
        'mini_featured_news': mini_featured_news,
        'current_category': 'Education',
    }
    return render(request, 'news/education.html', context)
# -----------------------------------------------------------------------


def opinion(request):
    last_caching = timezone.now() - timedelta(hours=12)
    strict_caching = timezone.now() - timedelta(days=14) 
    
    featured_opinion = News.objects.public().filter(
        category__name='Opinion', 
        is_featured=True
    ).order_by('-date_published').first()
    
    # Top Opinion
    top_opinion = get_top_ranking('Opinion', 'top_opinion', last_caching, strict_caching)

    # Latest News
    latest_opinion = News.objects.public().filter(
        category__name='Opinion', 
        is_featured=False
    ).order_by('-date_published')[:5]

    # News card
    used_ids = [n.id for n in top_opinion]
    used_ids += [n.id for n in latest_opinion]
    
    if featured_opinion:
        used_ids.append(featured_opinion.id)
    
    news_list = News.objects.public().filter(
        category__name='Opinion', 
        is_featured=False
    ).exclude(id__in=used_ids).order_by('-date_published')
    
    # 5 random from the 20 LATEST other news
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

    # Pagination
    paginator = Paginator(news_list, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'featured_opinion': featured_opinion,
        'top_opinion': top_opinion,
        'latest_opinion': latest_opinion,
        'page_obj': page_obj,
        'mini_featured_news': mini_featured_news,
        'current_category': 'Opinion',
    }
    return render(request, 'news/opinion.html', context)