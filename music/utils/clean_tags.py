from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, COMM
import os

def clean_mp3_tags(file_path, title, artist, logo_path):
    audio = MP3(file_path, ID3=ID3)
    audio.delete()  # remove old tags

    # Add basic tags
    audio["TIT2"] = TIT2(encoding=3, text=title)
    audio["TPE1"] = TPE1(encoding=3, text=artist)
    audio["COMM"] = COMM(encoding=3, lang='eng', text='Uploaded by VibeNation')

    # Embed cover art with dynamic MIME type based on file extension
    with open(logo_path, "rb") as albumart:
        ext = os.path.splitext(logo_path)[1].lower()
        mime_type = "image/png" if ext == ".png" else "image/jpeg"

        audio.tags.add(
            APIC(
                encoding=3,
                mime=mime_type,
                type=3,
                desc='Cover',
                data=albumart.read()
            )
        )

    # Force ID3v2.3 tags so players display cover correctly
    audio.tags.update_to_v23()
    audio.save(v2_version=3)
