import Image from 'next/image';
import Link from 'next/link';

// Interface matching your Django DRF payload format
export interface Artist {
  id?: number | string;
  name: string;
}

export interface Song {
  id: number | string;
  title: string;
  slug?: string;
  cover_image?: string;
  genre?: string | { name: string };
  artists?: Artist[] | string;
}

interface SongCardProps {
  song: Song;
}

export default function SongCard({ song }: SongCardProps) {
  // Safely format artist names whether backend sends array of objects or string
  const artistNames = Array.isArray(song.artists)
    ? song.artists.map((a) => a.name).join(', ')
    : song.artists || 'Unknown Artist';

  // Extract genre cleanly
  const genreLabel = typeof song.genre === 'object' && song.genre !== null
    ? song.genre.name
    : song.genre || 'Music';

  const songUrl = `/music/${song.slug || song.id}`;

  return (
    <Link href={songUrl} className="group block w-full">
      <div className="relative flex items-center gap-4 p-3.5 sm:p-4 rounded-2xl border border-slate-200 dark:border-slate-800/80 bg-white dark:bg-slate-900 shadow-sm hover:shadow-md hover:border-teal-500/50 dark:hover:border-teal-500/40 transition-all duration-300">
        
        {/* Album Cover Art */}
        <div className="relative w-20 h-20 sm:w-24 sm:h-24 rounded-xl overflow-hidden shrink-0 bg-slate-100 dark:bg-slate-800 border border-slate-100 dark:border-slate-800">
          <Image
            src={song.cover_image || '/images/vn-default-cover.jpg'}
            alt={`${song.title} artwork`}
            fill
            sizes="(max-width: 640px) 80px, 96px"
            className="object-cover transition-transform duration-500 group-hover:scale-105"
          />
          
          {/* Subtle Hover Play Overlay */}
          <div className="absolute inset-0 bg-slate-950/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center backdrop-blur-[1px]">
            <div className="w-10 h-10 rounded-full bg-teal-500 text-slate-950 flex items-center justify-center shadow-lg transform translate-y-2 group-hover:translate-y-0 transition-all duration-300">
              <svg className="w-5 h-5 fill-current ml-0.5" viewBox="0 0 24 24">
                <path d="M8 5v14l11-7z" />
              </svg>
            </div>
          </div>
        </div>

        {/* Content Section */}
        <div className="flex-1 min-w-0 flex flex-col justify-center">
          
          {/* Category / Genre Badge */}
          <div className="mb-1.5">
            <span className="inline-block px-2.5 py-0.5 rounded-full border border-teal-500/30 bg-teal-500/10 text-teal-700 dark:text-teal-400 text-[11px] font-extrabold uppercase tracking-wider">
              {genreLabel}
            </span>
          </div>

          {/* Title & Artist */}
          <h3 className="text-base sm:text-lg font-black text-slate-950 dark:text-white leading-snug truncate group-hover:text-teal-600 dark:group-hover:text-teal-400 transition-colors">
            {song.title}
          </h3>
          
          <p className="text-sm font-medium text-slate-600 dark:text-slate-400 truncate mt-0.5">
            {artistNames}
          </p>
        </div>

      </div>
    </Link>
  );
}