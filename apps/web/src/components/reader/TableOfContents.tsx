'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { X, ChevronRight } from 'lucide-react';

interface TOCItem {
  id: string;
  title: string;
  href?: string;
  level?: number;
  children?: TOCItem[];
}

interface TableOfContentsProps {
  open: boolean;
  onClose: () => void;
  toc: TOCItem[];
  currentChapter: string;
  onNavigate: (chapter: TOCItem) => void;
}

function TOCItemComponent({
  item,
  level = 0,
  currentChapter,
  onNavigate,
}: {
  item: TOCItem;
  level?: number;
  currentChapter: string;
  onNavigate: (chapter: TOCItem) => void;
}) {
  const isActive = item.id === currentChapter;
  const hasChildren = item.children && item.children.length > 0;

  return (
    <div>
      <button
        onClick={() => onNavigate(item)}
        className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm transition-colors ${
          isActive
            ? 'bg-primary/10 font-medium text-primary'
            : 'text-muted-foreground hover:bg-muted hover:text-foreground'
        }`}
        style={{ paddingLeft: `${12 + level * 16}px` }}
      >
        <ChevronRight className={`h-3.5 w-3.5 flex-shrink-0 transition-transform ${isActive ? 'rotate-90' : ''}`} />
        <span className="line-clamp-2">{item.title}</span>
      </button>
      {hasChildren && (
        <div className="mt-0.5">
          {item.children!.map((child) => (
            <TOCItemComponent
              key={child.id}
              item={child}
              level={level + 1}
              currentChapter={currentChapter}
              onNavigate={onNavigate}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export function TableOfContents({ open, onClose, toc, currentChapter, onNavigate }: TableOfContentsProps) {
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
            className="fixed left-0 top-0 bottom-0 z-50 w-80 border-r border-border bg-card/95 backdrop-blur-xl shadow-2xl"
          >
            <div className="flex items-center justify-between border-b border-border px-4 py-3">
              <h2 className="font-semibold">Contents</h2>
              <button
                onClick={onClose}
                className="rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-muted"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="overflow-y-auto p-2">
              {toc.length === 0 ? (
                <p className="text-center text-sm text-muted-foreground py-8">
                  No table of contents available.
                </p>
              ) : (
                <div className="space-y-0.5">
                  {toc.map((item) => (
                    <TOCItemComponent
                      key={item.id}
                      item={item}
                      currentChapter={currentChapter}
                      onNavigate={onNavigate}
                    />
                  ))}
                </div>
              )}
            </div>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
