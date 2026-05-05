from PIL import Image
import io
import os
from django.core.files.base import ContentFile
from django.utils.text import slugify

def handle_webp_compression(image_field, title, max_width=1200):
    """
    Fixed version to prevent deep/nested folders using os.path.basename.
    """
    if not image_field:
        return None
        
    img = Image.open(image_field)
    
    # Resize
    if img.width > max_width:
        new_height = int((max_width / img.width) * img.height)
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

    # Convert to RGB
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Compress to WebP
    output = io.BytesIO()
    img.save(output, format='WebP', quality=60)
    output.seek(0)

    # --- THE CRITICAL FIX ---
    clean_filename = slugify(title)
    new_name = f"{clean_filename}.webp"
    
    return ContentFile(output.read(), name=new_name)