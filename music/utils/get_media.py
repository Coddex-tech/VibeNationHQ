def get_primary_media(obj):
    """
    Returns a unified media dict for ANY content type.
    """
    if hasattr(obj, "dj_cover") and obj.dj_cover:
        return {
            "type": "image",
            "url": obj.dj_cover.url,
            "alt": getattr(obj, "dj_name", "DJ Cover")
        }

    if hasattr(obj, "cover_image") and obj.cover_image:
        return {
            "type": "image",
            "url": obj.cover_image.url,
            "alt": getattr(obj, "title", "Cover")
        }

    if hasattr(obj, "original_cover") and obj.original_cover:
        return {
            "type": "image",
            "url": obj.original_cover.url,
            "alt": getattr(obj, "title", "Cover")
        }

    return {
        "type": "image",
        "url": "/static/images/Media_cover_placeholder.webp",
        "alt": "Default Cover"
    }

def attach_media(items):
    for obj in items:
        obj.media = get_primary_media(obj)
    return items