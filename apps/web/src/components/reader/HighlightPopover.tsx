'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { Highlighter, StickyNote, Share2, X } from 'lucide-react';

const HIGHLIGHT_COLORS = [
  { id: 'yellow', bg: 'bg-yellow-400', label: 'Yellow' },
  { id: 'green', bg: 'bg-green-400', label: 'Green' },
  { id: 'blue', bg: 'bg-blue-400', label: 'Blue' },
  { id: 'pink', bg: 'bg-pink-400', label: 'Pink' },
  { id: 'purple', bg: 'bg-purple-400', label: 'Purple' },
  { id: 'orange', bg: 'bg-orange-400', label: 'Orange' },
];

interface HighlightPopoverProps {
  selectedText: string;
  selectionRect: DOMRect | null;
  onHighlight: (color: string) => void;
  onNote: () => void;
  onShare: () => void;
  onDismiss: () => void;
}

export function HighlightPopover({
  selectedText,
  selectionRect,
  onHighlight,
  onNote,
  onShare,
  onDismiss,
}: HighlightPopoverProps) {
  if (!selectedText || !selectionRect) return null;

  // Position popover above selection
  const top = selectionRect.top - 60;
  const left = Math.min(
    Math.max(selectionRect.left + selectionRect.width / 2 - 140, 16),
    window.innerWidth - 296
  );

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 10, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 10, scale: 0.95 }}
        transition={{ duration: 0.15 }}
        className="fixed z-50 rounded-xl border border-border bg-card shadow-2xl backdrop-blur-xl"
        style={{ top: `${top}px`, left: `${left}px`, width: '280px' }}
      >
        {/* Color picker */}
        <div className="flex items-center gap-1.5 p-3 pb-2">
          {HIGHLIGHT_COLORS.map((color) => (
            <button
              key={color.id}
              onClick={() => onHighlight(color.id)}
              className={`h-7 w-7 rounded-full ${color.bg} ring-2 ring-transparent transition-all hover:scale-110 hover:ring-white/50`}
              title={color.label}
            />
          ))}
        </div>

        {/* Actions */}
        <div className="flex items-center gap-1 border-t border-border p-2">
          <button
            onClick={onNote}
            className="flex flex-1 items-center justify-center gap-1.5 rounded-lg py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted"
          >
            <StickyNote className="h-3.5 w-3.5" />
            Note
          </button>
          <button
            onClick={onShare}
            className="flex flex-1 items-center justify-center gap-1.5 rounded-lg py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted"
          >
            <Share2 className="h-3.5 w-3.5" />
            Share
          </button>
          <button
            onClick={onDismiss}
            className="flex flex-1 items-center justify-center gap-1.5 rounded-lg py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-muted"
          >
            <X className="h-3.5 w-3.5" />
            Dismiss
          </button>
        </div>

        {/* Selected text preview */}
        <div className="border-t border-border px-3 py-2">
          <p className="line-clamp-2 text-xs text-muted-foreground italic">
            &ldquo;{selectedText.slice(0, 120)}{selectedText.length > 120 ? '...' : ''}&rdquo;
          </p>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
