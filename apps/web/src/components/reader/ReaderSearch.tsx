'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Search, ChevronRight, Loader2 } from 'lucide-react';

interface ReaderSearchProps {
  open: boolean;
  onClose: () => void;
  bookId: string;
}

export function ReaderSearch({ open, onClose, bookId }: ReaderSearchProps) {
  const [query, setQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<any[]>([]);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setIsSearching(true);
    // In production: search within book content
    setTimeout(() => {
      setResults([]);
      setIsSearching(false);
    }, 500);
  };

  return (
    <AnimatePresence>
      {open && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-black/20"
            onClick={onClose}
          />
          <motion.aside
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed left-0 top-0 bottom-0 z-50 w-96 border-r border-border bg-card/95 backdrop-blur-xl shadow-2xl"
          >
            <div className="flex items-center justify-between border-b border-border px-4 py-3">
              <h2 className="font-semibold">Search in Book</h2>
              <button
                onClick={onClose}
                className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-muted"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="p-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="Search for words or phrases..."
                  className="w-full rounded-lg border border-input bg-background py-2 pl-10 pr-4 text-sm outline-none transition-all focus:border-primary focus:ring-2 focus:ring-primary/20"
                  autoFocus
                />
              </div>
            </div>

            <div className="overflow-y-auto px-4 pb-4">
              {isSearching ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                </div>
              ) : results.length === 0 && query ? (
                <p className="text-center text-sm text-muted-foreground py-8">
                  No results found for &quot;{query}&quot;
                </p>
              ) : results.length > 0 ? (
                <div className="space-y-2">
                  {results.map((result, i) => (
                    <button
                      key={i}
                      className="flex w-full items-start gap-3 rounded-lg border border-border p-3 text-left transition-colors hover:border-primary/20 hover:bg-muted/50"
                    >
                      <ChevronRight className="mt-0.5 h-4 w-4 flex-shrink-0 text-muted-foreground" />
                      <div>
                        <p className="text-sm">{result.text}</p>
                        <p className="mt-1 text-xs text-muted-foreground">{result.chapter}</p>
                      </div>
                    </button>
                  ))}
                </div>
              ) : (
                <p className="text-center text-sm text-muted-foreground py-8">
                  Type a search query and press Enter
                </p>
              )}
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
