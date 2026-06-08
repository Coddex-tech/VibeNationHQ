from django.db.models import Q, Count, F, Exists, OuterRef
from django.http import FileResponse, Http404
from django.core.paginator import Paginator
from django.conf import settings
from .utils.get_media import get_primary_media, attach_media
from .utils.clean_tags import clean_mp3_tags
from django.shortcuts import render, get_object_or_404, redirect
from .models import Song, DJ, Album, Artist, SongView, MusicComment
from django.contrib.contenttypes.models import ContentType
from news.models import News
import shutil
import os
import re
from .forms import MusicCommentForm
from taggit.models import Tag
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache
from django.template.loader import render_to_string
from utils.security import get_cloudflare_ip
from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse

# ==================================================================
# MUSIC HOMEPAGE
# ==================================================================
def music(request):
    # Fetch all songs with artists prefetched to avoid duplication
    all_songs = Song.objects.prefetch_related('artists').distinct()
    all_djs = DJ.objects.all()[:21]
    gospels = Song.objects.filter(genres__name="Gospel")[:21]

    # newest songs
    newest_songs = all_songs.order_by('-release_date')[:21]

    # Trending songs based on views
    one_week_ago = timezone.now() - timedelta(days=7)
    trending_now = cache.get('trending_now')
    if not trending_now:
        # Count recent views only within the last 7 days
        trending_now = Song.objects.annotate(
            recent_views=Count('song_views', filter=Q(song_views__timestamp__gte=one_week_ago))
        ).order_by('-recent_views')[:10]

        # Cache for 30 minutes (1800 seconds)
        cache.set('trending_now', list(trending_now), 1800) # 7 days in seconds

    # ATTACHING MEDIA WITH HELPER FUNCTION
    newest_songs = attach_media(newest_songs)
    gospels = attach_media(gospels)
    trending = attach_media(trending_now)
    all_djs = attach_media(all_djs)

    context = {
        "newest_songs": newest_songs,
        "gospels": gospels,
        "trending": trending_now,
        "djs": all_djs,
    }

    return render(request, "music/music.html", context)
# -----------------------------------------------------------------------

# =======================================================================
# LATEST SONG CATEGORY
# =======================================================================
def latest_music(request):
    SongArtistBridge = Song.artists.through
    all_songs = Song.objects.filter(
        Exists(SongArtistBridge.objects.filter(song_id=OuterRef('pk')))
    ).prefetch_related('artists').order_by('-release_date')
    newest_songs = all_songs.order_by('-release_date') # all song

    # paginate: 20 songs per page
    paginator = Paginator(newest_songs, 20)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    page_obj = attach_media(page_obj)    
    
    context = {
        "page_obj": page_obj,
    }
    return render(request, "music/latest_music.html", context)
# ----------------------------- ------------------------------------------


# =======================================================================
# GOSPEL CATEGORY
# =======================================================================
def gospel(request):
    all_gospels = Song.objects.filter(
        genres__name="Gospel"
    ).prefetch_related('artists').order_by('-release_date')

    paginator = Paginator(all_gospels, 10)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    page_obj = attach_media(page_obj)
    context = {
        "page_obj": page_obj,
    }
    return render(request, "music/gospel_music.html", context)
# -----------------------------------------------------------------------


# =======================================================================
# MIXTAPE CATEGORY
# =======================================================================
def mixtape(request):
    newest_djs = DJ.objects.all().order_by('-created_at')

    paginator = Paginator(newest_djs, 10)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    page_obj = attach_media(page_obj)
    
    context = {
        "page_obj": page_obj,
    }
    return render(request, "music/mixtape.html", context)
# -----------------------------------------------------------------------


# =======================================================================
# TRENDING SONG
# =======================================================================
def trending_song(request):
    now = timezone.now()

    def get_trending(cache_key, days, limit=21):
        data = cache.get(cache_key)

        if not data:
            time_threshold = now - timedelta(days=days)

            data = list(
                Song.objects.annotate(
                    recent_views=Count(
                        'song_views',
                        filter=Q(song_views__timestamp__gte=time_threshold)
                    )
                )
                .prefetch_related('artists')
                .order_by('-recent_views')[:limit]
            )

            # Attach unified media
            data = attach_media(data)

            # Cache processed objects
            cache_duration = 800 if days == 1 else 1800
            cache.set(cache_key, data, cache_duration)

        return data

    trending_songs = Song.objects.prefetch_related(
        'artists'
    ).order_by('-views')[:40]

    trending_songs = attach_media(trending_songs)

    context = {
        'trending_now': get_trending('trending_now', 1),
        'trending_week': get_trending('trending_week', 7),
        'trending_month': get_trending('trending_month', 30),
        'trending_songs': trending_songs,
    }
    return render(request, "music/trending.html", context)
# -----------------------------------------------------------------------

def album(request):
    all_albums = Album.objects.prefetch_related('artist').annotate(
        song_count=Count('songs')
    ).order_by('-release_date')

    paginator = Paginator(all_albums, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
    }
    return render(request, "music/albums.html", context)
# ----------------------------------------------------------------------------------

def album_detail(request, slug):
    album = get_object_or_404(Album, slug=slug)
    songs = Song.objects.filter(album=album).distinct()  # ensures no duplicates
    return render(request, 'music/album_detail.html', {'album': album, 'songs': songs})



# =======================================================================
# AFRICAN MUSIC
# =======================================================================
def african_music(request):
    all_africas = Song.objects.filter(
        category="Africa"
    ).prefetch_related('artists').order_by('-release_date')

    paginator = Paginator(all_africas, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    page_obj = attach_media(page_obj)

    context = {
        "page_obj": page_obj,
    }
    return render(request, "music/african_music.html", context)
# -----------------------------------------------------------------------
    




# =======================================================================
# SONG DETAIL PAGE
# =======================================================================
@ratelimit(key=get_cloudflare_ip, rate='3/m', method='POST', block=False)
def song_detail(request, slug):
    obj = Song.objects.filter(slug=slug).select_related('album').prefetch_related('artists').first()
    is_dj = False

    if not obj:
        obj = DJ.objects.filter(slug=slug).prefetch_related('artists').first()
        is_dj = True

    if not obj:
        raise Http404("Not found")

    if not is_dj:
        Song.objects.filter(id=obj.id).update(views=F('views') + 1)
        try:
            from .utils import get_cloudflare_ip as get_client_ip
            ip = get_client_ip(request)
            if not SongView.objects.filter(song=obj, ip_address=ip).exists():
                SongView.objects.create(song=obj, ip_address=ip)
        except:
            pass

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    # ====== COMMENT ========== 
    if request.method == 'POST':
        is_staff = request.user.is_authenticated and request.user.is_staff

        # Rate Limit
        if not is_staff:
            was_limited = getattr(request, 'limited', False)
            if was_limited:
                if is_ajax:
                    return JsonResponse({"status": "error", "message": "🔥 Slow down! You are posting too fast."}, status=429)
                return redirect(request.path)

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
                if is_ajax:
                    return JsonResponse({"status": "error", "message": "Links are not allowed in comments."}, status=400)
                return redirect(request.path)

        form = MusicCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)

            if not is_dj:
                comment.song = obj
            else:
                comment.dj = obj

            # ===== IDENTITY RULE =====
            if is_staff:
                comment.user = request.user
                comment.name = request.user.get_full_name() or request.user.username
            else:
                forbidden_flags = ["admin", "vibenation", "staff", "moderator", "editor", "boss"]
                if any(flag in str(comment.name).lower() for flag in forbidden_flags):
                    comment.name = "Anonymous Fan"
            # ===============================

            parent_id = request.POST.get('parent_id')

            if parent_id:
                try:
                    parent_comment = MusicComment.objects.get(id=parent_id)

                    if parent_comment.parent_id:
                        comment.parent_id = parent_comment.parent_id
                    else:
                        comment.parent_id = parent_comment.id
                except Exception:
                    comment.parent_id = parent_id

            comment.save()

            html_content = None

            if comment.parent_id:
                html_content = render_to_string(
                    'music/partials/music_reply.html',
                    {'reply': comment},
                    request=request
                )
            else:
                html_content = render_to_string(
                    'music/partials/music_comment.html',
                    {'comment': comment},
                    request=request
                )

            # =============== JSON RESPONSE =============
            response = JsonResponse({
                "status": "success",
                "message": "Comment posted successfully!",
                "html": html_content,
                "root_id": comment.root_comment.id,
                "commenter_name": comment.name,
            })

            # COOKIE
            if not is_staff:
                response.set_cookie(
                    'music_commenter_name',
                    comment.name,
                    max_age=60 * 60 * 24 * 30
                )

            return response

        else:
            if is_ajax:
                error_messages = ", ".join([f"{field}: {errors[0]}" for field, errors in form.errors.items()])
                return JsonResponse({"status": "error", "message": error_messages}, status=400)

    # ================= GET REQUEST ======================
    if request.user.is_authenticated and request.user.is_staff:
        form = MusicCommentForm()
    else:
        last_name = request.COOKIES.get('music_commenter_name', '')
        form = MusicCommentForm(initial={'name': last_name} if last_name else None)

    # ===== CONTENT =====
    if not is_dj and obj.genres:
        genre_songs = Song.objects.filter(genres__in=obj.genres.all()).exclude(id=obj.id).prefetch_related('artists', 'genres')[:12]
    else:
        genre_songs = Song.objects.all().order_by('-release_date').prefetch_related('artists')[:12]

    trending_songs = Song.objects.all().order_by('-views').prefetch_related('artists')[:12]

    comment_filter = {'parent__isnull': True, 'is_approved': True}
    if not is_dj:
        comment_filter['song'] = obj
    else:
        comment_filter['dj'] = obj

    music_comments = MusicComment.objects.filter(**comment_filter).prefetch_related('replies').order_by('-created_at')[:10]

    display_title = obj.dj_name if is_dj else obj.title

    context = {
        'song': obj,
        'artists': obj.artists.all(),
        "media": get_primary_media(obj), # For media
        'music_comments': music_comments,
        'form': form,
        'is_dj': is_dj,
        'genre_songs': genre_songs,
        'trending_songs': trending_songs,
        'page_title': f"{display_title} | VibeNation",
    }
    return render(request, 'music/song_detail.html', context)
# ======================================================================================

COMMENTS_PER_LOAD = 5
REPLIES_PER_LOAD = 3

# --- LOAD MAIN COMMENTS ---
def load_more_music_comments(request, song_id):
    offset = int(request.GET.get('offset', 0))
    song = get_object_or_404(Song, id=song_id)

    all_parents = MusicComment.objects.filter(
        song=song, 
        parent__isnull=True, 
        is_approved=True
    ).order_by('-created_at')

    next_batch = all_parents[offset : offset + COMMENTS_PER_LOAD]
    
    html_output = ""
    for comment in next_batch:
        html_output += render_to_string(
            'music/partials/music_comment.html', 
            {'comment': comment}, 
            request=request
        )

    return JsonResponse({
        'html': html_output,
        'has_more': all_parents.count() > (offset + COMMENTS_PER_LOAD)
    })


# --- LOAD NESTED REPLIES ---
def load_more_music_replies(request, comment_id):
    offset = int(request.GET.get('offset', 0))
    comment = get_object_or_404(MusicComment, id=comment_id)
    
    # Get the flattened list from your model's helper method
    all_replies = comment.get_all_replies()
    
    # Slice for the next batch
    replies = all_replies[offset : offset + REPLIES_PER_LOAD]

    # Render only the inner reply items
    html = render_to_string(
        'music/partials/music_reply_list.html', 
        {'replies': replies},
        request=request
    )

    return JsonResponse({
        'html': html,
        'has_more': len(all_replies) > (offset + REPLIES_PER_LOAD)
    })
# ========================================================================

    
# ========================================================================
# SEARCH BAR RESULT
# ========================================================================
def search(request):
    query = request.GET.get('q', '').strip()
    
    if not query:
        return render(request, 'music/search_results.html', {'query': query})

    songs_queryset = Song.objects.filter(
        Q(title__icontains=query) |
        Q(artists__name__icontains=query)
    ).select_related('album').prefetch_related('artists').distinct().order_by('-release_date')

    # Album Search
    album_matches = Album.objects.filter(
        Q(title__icontains=query) |
        Q(artist__name__icontains=query)
    ).prefetch_related('artist').distinct().order_by('-release_date')

    # Merge songs from matching albums 
    album_songs = Song.objects.filter(album__in=album_matches).select_related('album').prefetch_related('artists').distinct()
    
    # Final Merge & Ordering
    all_songs = (songs_queryset | album_songs).distinct().order_by('-release_date')

    # News Search
    news_results = News.objects.public().filter(
        Q(title__icontains=query) |
        Q(content__icontains=query) |
        Q(tags__name__icontains=query)
    ).prefetch_related('tags').distinct().order_by('-date_published')

    # Pagination
    songs_page = Paginator(all_songs, 12).get_page(request.GET.get('page'))
    albums_page = Paginator(album_matches, 12).get_page(request.GET.get('albums_page'))
    news_page = Paginator(news_results, 12).get_page(request.GET.get('news_page'))
    
    # Artist results
    artists = Artist.objects.filter(name__icontains=query)[:10]

    songs_page = attach_media(songs_page)

    context = {
        'query': query,
        'page_obj': songs_page,
        'albums_page_obj': albums_page,
        'artists': artists,
        'news_page_obj': news_page
    }

    return render(request, 'music/search_results.html', context)


# ========================================================================
# DOWNLOAD COUNT
# ========================================================================
def download_song(request, slug):
    song = get_object_or_404(Song, slug=slug)

    if not song.audio_file or not os.path.exists(song.audio_file.path):
        raise Http404("Audio file not found.")

    original_path = song.audio_file.path
    artist_names = ", ".join([artist.name for artist in song.artists.all()])
    download_name = f"{song.title} - {artist_names} | VibeNationhq.com.mp3"

    # Create temporary directory
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_downloads')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Unique name for the temp file to avoid collisions between users
    temp_path = os.path.join(temp_dir, f"dl_{song.id}_{os.path.basename(original_path)}")
    shutil.copy2(original_path, temp_path)

    try:
        # Embed Branding
        logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'images', 'VibeNation_cover.jpg')
        clean_mp3_tags(temp_path, song.title, artist_names, logo_path)

        # We wrap the file so that os.remove is called ONLY after the file is sent
        file_handle = open(temp_path, 'rb')
        response = FileResponse(file_handle, as_attachment=True, filename=download_name)
        
        # This is the "Magic Trick": we attach a custom closer to the response
        def cleanup():
            file_handle.close()
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
        response.closed_callback = cleanup # Custom attribute or use a middleware/wrapper
        
        #  Increment count
        Song.objects.filter(id=song.id).update(download=F('download') + 1)
        
        return response

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        print(f"Download Error: {e}")
        raise Http404("Something went wrong.")
# ------------------------------------------------------------------------

# Song tag
def songs_by_tag(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)

    songs_list = Song.objects.filter(tags=tag)\
        .select_related('album')\
        .prefetch_related('artists', 'tags')\
        .order_by('-release_date')

    paginator = Paginator(songs_list, 20)
    page_number = request.GET.get('page')
    songs = paginator.get_page(page_number)

    songs = attach_media(songs)
    return render(request, 'music/songs_by_tag.html', {
        'tag': tag,
        'songs': songs
    })
# ------------------------------------------------------------------------

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

def service(request):
    return render(request, "service.html")

def privacy(request):
    return render(request, "privacy.html")

def dmca(request):
    return render(request, "dmca.html")

def advertise(request):
    return render(request, "advertise.html")