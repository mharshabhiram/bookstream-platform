'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { X, Highlighter, Bookmark, StickyNote, ChevronRight } from 'lucide-react';

interface ReaderSidebarProps {
  open: boolean;
  onClose: () => void;
  highlights: any[];
  bookmarks: any[];
  notes: any[];
  activeTab: 'highlights' | 'bookmarks' | 'notes';
}

export function ReaderSidebar({ open, onClose, highlights, bookmarks, notes, activeTab }: ReaderSidebarProps) {
  const tabs = [
    { id: 'highlights' as const, label: 'Highlights', icon: Highlighter, count: highlights.length },
    { id: 'bookmarks' as const, label: 'Bookmarks', icon: Bookmark, count: bookmarks.length },
    { id: 'notes' as const, label: 'Notes', icon: StickyNote, count: notes.length },
  ];

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
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed right-0 top-0 bottom-0 z-50 w-80 border-l border-border bg-card/95 backdrop-blur-xl shadow-2xl"
          >
            <div className="flex items-center justify-between border-b border-border px-4 py-3">
              <h2 className="font-semibold">Annotations</h2>
              <button
                onClick={onClose}
                className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-muted"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="flex border-b border-border">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  className={`flex flex-1 items-center justify-center gap-1.5 border-b-2 px-3 py-2.5 text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'border-primary text-primary'
                      : 'border-transparent text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <tab.icon className="h-4 w-4" />
                  {tab.label}
                  {tab.count > 0 && (
                    <span className="rounded-full bg-primary/10 px-1.5 py-0.5 text-xs text-primary">
                      {tab.count}
                    </span>
                  )}
                </button>
              ))}
            </div>

            <div className="overflow-y-auto p-4">
              {activeTab === 'highlights' && (
                <div className="space-y-3">
                  {highlights.length === 0 ? (
                    <p className="text-center text-sm text-muted-foreground py-8">
                      No highlights yet. Select text to highlight.
                    </p>
                  ) : (
                    highlights.map((h: any) => (
                      <div
                        key={h.id}
                        className="group rounded-lg border border-border p-3 transition-colors hover:border-primary/20"
                      >
                        <div className="flex items-start gap-2">
                          <div
                            className="mt-1 h-3 w-3 flex-shrink-0 rounded-full"
                            style={{ backgroundColor: h.color }}
                          />
                          <p className="text-sm leading-relaxed">{h.text}</p>
                        </div>
                        {h.note && (
                          <p className="mt-2 text-xs text-muted-foreground italic">{h.note}</p>
                        )}
                        <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
                          <span>{h.chapter_title || 'Unknown chapter'}</span>
                          <span>{new Date(h.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              )}

              {activeTab === 'bookmarks' && (
                <div className="space-y-2">
                  {bookmarks.length === 0 ? (
                    <p className="text-center text-sm text-muted-foreground py-8">
                      No bookmarks yet.
                    </p>
                  ) : (
                    bookmarks.map((b: any) => (
                      <button
                        key={b.id}
                        className="flex w-full items-center gap-3 rounded-lg border border-border p-3 text-left transition-colors hover:border-primary/20 hover:bg-muted/50"
                      >
                        <Bookmark className="h-4 w-4 text-primary" />
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{b.label || 'Bookmark'}</p>
                          <p className="text-xs text-muted-foreground">{b.chapter_title || 'Page ' + b.page_number}</p>
                        </div>
                        <ChevronRight className="h-4 w-4 text-muted-foreground" />
                      </button>
                    ))
                  )}
                </div>
              )}

              {activeTab === 'notes' && (
                <div className="space-y-3">
                  {notes.length === 0 ? (
                    <p className="text-center text-sm text-muted-foreground py-8">
                      No notes yet. Select text to add a note.
                    </p>
                  ) : (
                    notes.map((n: any) => (
                      <div key={n.id} className="rounded-lg border border-border p-3">
                        <h4 className="text-sm font-medium">{n.title || 'Untitled Note'}</h4>
                        <p className="mt-1 text-sm text-muted-foreground">{n.content}</p>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
