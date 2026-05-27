'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Heart, MoreVertical, BookOpen } from 'lucide-react';
import { useState } from 'react';
import { booksApi } from '@/lib/api';
import { useMutation, useQueryClient } from '@tanstack/react-query';

interface BookCardProps {
  book: {
    id: string;
    title: string;
    author_name: string | null;
    cover_url: string | null;
    thumbnail_url: string | null;
    file_format: string;
    average_rating: number;
    total_reviews: number;
  };
  userBook?: {
    is_favorite: boolean;
    status: string;
    last_progress_percent: number;
  } | null;
  viewMode: 'grid' | 'list';
}

export function BookCard({ book, userBook, viewMode }: BookCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const queryClient = useQueryClient();

  const toggleFavorite = useMutation({
    mutationFn: () =>
      booksApi.updateLibrary(book.id, { is_favorite: !userBook?.is_favorite }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['library'] });
    },
  });

  const coverUrl = book.cover_url || book.thumbnail_url;

  if (viewMode === 'list') {
    return (
      <motion.div
        layout
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="group flex items-center gap-4 rounded-xl border border-border bg-card p-3 transition-all hover:border-primary/20 hover:shadow-lg"
      >
        <Link href={`/reader/${book.id}`} className="relative flex-shrink-0">
          <div className="h-20 w-14 overflow-hidden rounded-lg bg-muted">
            {coverUrl ? (
              <img
                src={coverUrl}
                alt={book.title}
                className="h-full w-full object-cover transition-transform group-hover:scale-105"
              />
            ) : (
              <div className="flex h-full items-center justify-center">
                <BookOpen className="h-5 w-5 text-muted-foreground" />
              </div>
            )}
          </div>
        </Link>

        <div className="flex-1 min-w-0">
          <Link href={`/reader/${book.id}`}>
            <h3 className="font-medium line-clamp-1 group-hover:text-primary transition-colors">
              {book.title}
            </h3>
          </Link>
          <p className="text-sm text-muted-foreground">{book.author_name || 'Unknown Author'}</p>
          <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
            <span className="rounded bg-muted px-1.5 py-0.5 uppercase">{book.file_format}</span>
            {userBook && (
              <span className="capitalize">{userBook.status}</span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1">
          <button
            onClick={() => toggleFavorite.mutate()}
            className={`rounded-lg p-2 transition-colors ${
              userBook?.is_favorite
                ? 'text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20'
                : 'text-muted-foreground hover:bg-muted'
            }`}
          >
            <Heart className={`h-4 w-4 ${userBook?.is_favorite ? 'fill-current' : ''}`} />
          </button>
          <button className="rounded-lg p-2 text-muted-foreground transition-colors hover:bg-muted">
            <MoreVertical className="h-4 w-4" />
          </button>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className="group relative"
    >
      <Link href={`/reader/${book.id}`}>
        <div className="relative aspect-[2/3] overflow-hidden rounded-xl bg-muted shadow-sm transition-all group-hover:shadow-xl group-hover:shadow-primary/5">
          {coverUrl ? (
            <img
              src={coverUrl}
              alt={book.title}
              className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
          ) : (
            <div className="flex h-full flex-col items-center justify-center gap-2 p-4 text-center">
              <BookOpen className="h-10 w-10 text-muted-foreground/50" />
              <span className="text-xs text-muted-foreground/50">{book.file_format.toUpperCase()}</span>
            </div>
          )}

          {/* Progress bar */}
          {userBook && userBook.last_progress_percent > 0 && (
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/20">
              <div
                className="h-full bg-primary transition-all"
                style={{ width: `${userBook.last_progress_percent}%` }}
              />
            </div>
          )}

          {/* Hover overlay */}
          <motion.div
            initial={false}
            animate={{ opacity: isHovered ? 1 : 0 }}
            className="absolute inset-0 flex flex-col justify-end bg-gradient-to-t from-black/70 via-black/20 to-transparent p-4"
          >
            <h3 className="text-sm font-semibold text-white line-clamp-2">{book.title}</h3>
            <p className="mt-0.5 text-xs text-white/70">{book.author_name || 'Unknown Author'}</p>
            {userBook && (
              <p className="mt-1 text-xs text-white/60">
                {Math.round(userBook.last_progress_percent)}% complete
              </p>
            )}
          </motion.div>
        </div>
      </Link>

      {/* Info below cover */}
      <div className="mt-2 px-0.5">
        <Link href={`/reader/${book.id}`}>
          <h3 className="text-sm font-medium line-clamp-1 group-hover:text-primary transition-colors">
            {book.title}
          </h3>
        </Link>
        <p className="mt-0.5 text-xs text-muted-foreground line-clamp-1">
          {book.author_name || 'Unknown Author'}
        </p>
      </div>

      {/* Favorite button */}
      <motion.button
        initial={false}
        animate={{ opacity: isHovered ? 1 : 0, scale: isHovered ? 1 : 0.8 }}
        onClick={() => toggleFavorite.mutate()}
        className={`absolute right-2 top-2 rounded-full p-1.5 backdrop-blur-sm transition-colors ${
          userBook?.is_favorite
            ? 'bg-red-500/80 text-white'
            : 'bg-black/40 text-white hover:bg-black/60'
        }`}
      >
        <Heart className={`h-3.5 w-3.5 ${userBook?.is_favorite ? 'fill-current' : ''}`} />
      </motion.button>
    </motion.div>
  );
}
