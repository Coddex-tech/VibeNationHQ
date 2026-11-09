'use client';

import { useEffect, useRef, useState } from 'react';
import { Pause, Play, Volume2 } from 'lucide-react';

type SongPreviewPlayerProps = {
  previewUrl: string | null;
  title: string;
};

function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) {
    return '0:00';
  }

  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);

  return `${minutes}:${String(remainingSeconds).padStart(2, '0')}`;
}

export default function SongPreviewPlayer({
  previewUrl,
  title,
}: SongPreviewPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);

  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [playbackError, setPlaybackError] = useState(false);

  useEffect(() => {
    const audio = audioRef.current;

    return () => {
      audio?.pause();
    };
  }, [previewUrl]);

  async function togglePlayback() {
    const audio = audioRef.current;

    if (!audio || !previewUrl) return;

    setPlaybackError(false);

    if (!audio.paused) {
      audio.pause();
      return;
    }

    try {
      await audio.play();
    } catch {
      setPlaybackError(true);
      setIsPlaying(false);
    }
  }

  function handleSeek(value: string) {
    const audio = audioRef.current;

    if (!audio || !Number.isFinite(audio.duration)) return;

    const nextTime = Number(value);

    audio.currentTime = nextTime;
    setCurrentTime(nextTime);
  }

  if (!previewUrl) {
    return (
      <div className="flex items-center gap-3 rounded-2xl border border-white/[0.08] bg-white/[0.025] px-4 py-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-white/[0.05] text-neutral-500">
          <Volume2 className="h-4 w-4" />
        </div>

        <div className="min-w-0">
          <p className="text-sm font-medium text-neutral-300">
            Preview unavailable
          </p>
          <p className="mt-0.5 text-xs text-neutral-500">
            Use an official streaming link to listen to the song.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-white/[0.09] bg-white/[0.035] p-4">
      <audio
        ref={audioRef}
        src={previewUrl}
        preload="metadata"
        onLoadedMetadata={(event) => {
          const audio = event.currentTarget;

          setDuration(
            Number.isFinite(audio.duration) ? audio.duration : 0,
          );
        }}
        onDurationChange={(event) => {
          const audio = event.currentTarget;

          setDuration(
            Number.isFinite(audio.duration) ? audio.duration : 0,
          );
        }}
        onTimeUpdate={(event) => {
          setCurrentTime(event.currentTarget.currentTime);
        }}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onEnded={() => {
          setIsPlaying(false);
          setCurrentTime(0);
        }}
        onError={() => {
          setIsPlaying(false);
          setPlaybackError(true);
        }}
      />

      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={togglePlayback}
          aria-label={isPlaying ? `Pause ${title}` : `Play ${title} preview`}
          className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-[#008f83] text-white transition hover:bg-[#00a294] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#39cbb9] focus-visible:ring-offset-2 focus-visible:ring-offset-[#101619]"
        >
          {isPlaying ? (
            <Pause className="h-4 w-4" fill="currentColor" />
          ) : (
            <Play className="ml-0.5 h-4 w-4" fill="currentColor" />
          )}
        </button>

        <div className="min-w-0 flex-1">
          <div className="mb-2 flex items-center justify-between gap-3">
            <p className="truncate text-xs font-semibold text-neutral-200">
              {isPlaying ? 'Now playing preview' : 'Listen to a preview'}
            </p>

            <span className="shrink-0 text-[11px] tabular-nums text-neutral-500">
              {formatTime(currentTime)} / {formatTime(duration)}
            </span>
          </div>

          <input
            type="range"
            min={0}
            max={duration || 1}
            step={0.1}
            value={Math.min(currentTime, duration || 0)}
            onChange={(event) => handleSeek(event.target.value)}
            aria-label="Seek song preview"
            disabled={!duration}
            className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-white/10 accent-[#25bdae] disabled:cursor-default"
          />

          {playbackError && (
            <p role="status" className="mt-2 text-xs text-amber-300">
              This preview couldn't be played. Try an official listening link.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}