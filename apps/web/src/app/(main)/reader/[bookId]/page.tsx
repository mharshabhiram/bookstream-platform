'use client';

import { useEffect, useRef, useState, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { useQuery, useMutation } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ChevronLeft,
  ChevronRight,
  Settings,
  List,
  Bookmark,
  Highlighter,
  Type,
  Sun,
  Moon,
  Maximize,
  Minimize,
  Search,
  X,
  Menu,
  Share2,
} from 'lucide-react';
import { booksApi, readingApi } from '@/lib/api';
import { useReaderStore } from '@/stores/reader';
import { ReaderToolbar } from '@/components/reader/ReaderToolbar';
import { ReaderSidebar } from '@/components/reader/ReaderSidebar';
import { ReaderSettings } from '@/components/reader/ReaderSettings';
import { TableOfContents } from '@/components/reader/TableOfContents';
import { ReaderSearch } from '@/components/reader/ReaderSearch';
import { HighlightPopover } from '@/components/reader/HighlightPopover';

export default function ReaderPage() {
  const { bookId } = useParams();
  const bookIdStr = Array.isArray(bookId) ? bookId[0] : bookId;

  const readerRef = useRef<HTMLDivElement>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [selectedText, setSelectedText] = useState('');
  const [selectionRect, setSelectionRect] = useState<DOMRect | null>(null);

  const {
    theme,
    fontFamily,
    fontSize,
    lineHeight,
    marginHorizontal,
    marginVertical,
    brightness,
    isFullscreen,
    isToolbarOpen,
    isSidebarOpen,
    isSettingsOpen,
    isTocOpen,
    isSearchOpen,
    isNotesOpen,
    toggleFullscreen,
    toggleToolbar,
    toggleSidebar,
    toggleSettings,
    toggleToc,
    toggleSearch,
  } = useReaderStore();

  const { data: bookData } = useQuery({
    queryKey: ['book', bookIdStr],
    queryFn: () => booksApi.get(bookIdStr!),
    enabled: !!bookIdStr,
  });

  const { data: progressData } = useQuery({
    queryKey: ['progress', bookIdStr],
    queryFn: () => readingApi.getProgress(bookIdStr!),
    enabled: !!bookIdStr,
  });

  const { data: highlightsData } = useQuery({
    queryKey: ['highlights', bookIdStr],
    queryFn: () => readingApi.getHighlights(bookIdStr!),
    enabled: !!bookIdStr,
  });

  const { data: bookmarksData } = useQuery({
    queryKey: ['bookmarks', bookIdStr],
    queryFn: () => readingApi.getBookmarks(bookIdStr!),
    enabled: !!bookIdStr,
  });

  const updateProgress = useMutation({
    mutationFn: (data: any) => readingApi.updateProgress(bookIdStr!, data),
  });

  const createHighlight = useMutation({
    mutationFn: readingApi.createHighlight,
  });

  const createBookmark = useMutation({
    mutationFn: readingApi.createBookmark,
  });

  const book = bookData?.data;
  const progress = progressData?.data;
  const highlights = highlightsData?.data || [];
  const bookmarks = bookmarksData?.data || [];

  // Apply reader settings
  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty('--reader-font-size', `${fontSize}px`);
    root.style.setProperty('--reader-line-height', `${lineHeight}`);
    root.style.setProperty('--reader-margin-h', `${marginHorizontal}px`);
    root.style.setProperty('--reader-margin-v', `${marginVertical}px`);
  }, [fontSize, lineHeight, marginHorizontal, marginVertical]);

  // Handle text selection
  const handleSelection = useCallback(() => {
    const selection = window.getSelection();
    if (selection && selection.toString().trim()) {
      setSelectedText(selection.toString());
      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();
      setSelectionRect(rect);
    } else {
      setSelectedText('');
      setSelectionRect(null);
    }
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft') goToPrevPage();
      if (e.key === 'ArrowRight') goToNextPage();
      if (e.key === 'Escape') {
        if (isSettingsOpen) toggleSettings();
        if (isSidebarOpen) toggleSidebar();
        if (isTocOpen) toggleToc();
      }
      if (e.key === 'f' && e.ctrlKey) {
        e.preventDefault();
        toggleSearch();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const goToNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage((p) => p + 1);
      updateProgress.mutate({
        current_page: currentPage + 1,
        total_pages: totalPages,
        progress_percent: ((currentPage + 1) / totalPages) * 100,
      });
    }
  };

  const goToPrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage((p) => p - 1);
    }
  };

  const handleAddHighlight = (color: string) => {
    if (selectedText) {
      createHighlight.mutate({
        book_id: bookIdStr!,
        text: selectedText,
        start_cfi: `page-${currentPage}`,
        end_cfi: `page-${currentPage}`,
        color,
      });
      setSelectedText('');
      setSelectionRect(null);
    }
  };

  const handleAddBookmark = () => {
    createBookmark.mutate({
      book_id: bookIdStr!,
      cfi: `page-${currentPage}`,
      page_number: currentPage,
      chapter_title: book?.toc?.[0]?.title,
    });
  };

  const themeClasses = {
    light: 'bg-white text-gray-900',
    dark: 'bg-[#1a1714] text-[#e8e4df]',
    sepia: 'bg-[#f4ecd8] text-[#5b4636]',
    amoled: 'bg-black text-white',
  };

  const fontClasses = {
    sans: 'font-sans',
    serif: 'font-serif',
    mono: 'font-mono',
  };

  if (!book) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-pulse text-muted-foreground">Loading book...</div>
      </div>
    );
  }

  return (
    <div
      className={`relative flex h-screen overflow-hidden ${themeClasses[theme]} ${fontClasses[fontFamily]}`}
      style={{ filter: `brightness(${brightness}%)` }}
    >
      {/* Reader Content */}
      <div
        ref={readerRef}
        className="flex-1 overflow-y-auto"
        onMouseUp={handleSelection}
        onTouchEnd={handleSelection}
      >
        {/* Top Toolbar */}
        <AnimatePresence>
          {isToolbarOpen && (
            <motion.header
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="sticky top-0 z-30 flex items-center justify-between border-b border-border/50 px-4 py-3 backdrop-blur-xl"
            >
              <div className="flex items-center gap-3">
                <button
                  onClick={() => window.history.back()}
                  className="rounded-lg p-2 transition-colors hover:bg-muted"
                >
                  <ChevronLeft className="h-5 w-5" />
                </button>
                <div>
                  <h1 className="text-sm font-semibold line-clamp-1">{book.title}</h1>
                  <p className="text-xs opacity-60">{book.author_name}</p>
                </div>
              </div>

              <div className="flex items-center gap-1">
                <button
                  onClick={toggleToc}
                  className="rounded-lg p-2 transition-colors hover:bg-muted"
                  title="Table of Contents"
                >
                  <List className="h-5 w-5" />
                </button>
                <button
                  onClick={toggleSearch}
                  className="rounded-lg p-2 transition-colors hover:bg-muted"
                  title="Search"
                >
                  <Search className="h-5 w-5" />
                </button>
                <button
                  onClick={handleAddBookmark}
                  className="rounded-lg p-2 transition-colors hover:bg-muted"
                  title="Bookmark"
                >
                  <Bookmark className="h-5 w-5" />
                </button>
                <button
                  onClick={toggleSettings}
                  className="rounded-lg p-2 transition-colors hover:bg-muted"
                  title="Settings"
                >
                  <Settings className="h-5 w-5" />
                </button>
                <button
                  onClick={toggleFullscreen}
                  className="rounded-lg p-2 transition-colors hover:bg-muted"
                  title="Fullscreen"
                >
                  {isFullscreen ? <Minimize className="h-5 w-5" /> : <Maximize className="h-5 w-5" />}
                </button>
              </div>
            </motion.header>
          )}
        </AnimatePresence>

        {/* Content Area */}
        <div
          className="mx-auto max-w-3xl px-8 py-12"
          style={{
            fontSize: `var(--reader-font-size)`,
            lineHeight: `var(--reader-line-height)`,
            paddingLeft: `var(--reader-margin-h)`,
            paddingRight: `var(--reader-margin-h)`,
            paddingTop: `var(--reader-margin-v)`,
            paddingBottom: `var(--reader-margin-v)`,
          }}
        >
          {/* Book content would be rendered here via EPUB.js or PDF.js */}
          <div className="prose max-w-none">
            <h1 className="mb-8 text-3xl font-bold">{book.title}</h1>
            {book.description && (
              <p className="mb-8 text-lg leading-relaxed opacity-80">{book.description}</p>
            )}

            {/* Placeholder content - in production this would be actual book content */}
            <div className="space-y-6 text-lg leading-relaxed">
              <p>
                This is a preview of the reader interface. In production, the actual book content
                would be rendered here using EPUB.js for EPUB files or PDF.js for PDF files.
              </p>
              <p>
                The reader supports customizable fonts, themes, margins, and line height.
                You can highlight text, add notes, create bookmarks, and navigate through chapters.
              </p>
              <p>
                Your reading progress is automatically saved and synced across all your devices.
              </p>
            </div>
          </div>
        </div>

        {/* Bottom Progress Bar */}
        <div className="sticky bottom-0 z-20 border-t border-border/50 bg-inherit/80 backdrop-blur-xl">
          <div className="flex items-center justify-between px-4 py-2">
            <button
              onClick={goToPrevPage}
              disabled={currentPage <= 1}
              className="rounded-lg p-2 transition-colors hover:bg-muted disabled:opacity-30"
            >
              <ChevronLeft className="h-5 w-5" />
            </button>

            <div className="flex flex-1 items-center gap-3 px-4">
              <span className="text-xs opacity-60">{currentPage}</span>
              <div className="flex-1 h-1 rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-primary transition-all"
                  style={{ width: `${(currentPage / totalPages) * 100}%` }}
                />
              </div>
              <span className="text-xs opacity-60">{totalPages}</span>
            </div>

            <button
              onClick={goToNextPage}
              disabled={currentPage >= totalPages}
              className="rounded-lg p-2 transition-colors hover:bg-muted disabled:opacity-30"
            >
              <ChevronRight className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Highlight Popover */}
      <HighlightPopover
        selectedText={selectedText}
        selectionRect={selectionRect}
        onHighlight={handleAddHighlight}
        onNote={() => {}}
        onShare={() => {}}
        onDismiss={() => {
          setSelectedText('');
          setSelectionRect(null);
        }}
      />

      {/* Sidebars */}
      <ReaderSidebar
        open={isSidebarOpen}
        onClose={toggleSidebar}
        highlights={highlights}
        bookmarks={bookmarks}
        notes={[]}
        activeTab={isNotesOpen ? 'notes' : 'highlights'}
      />

      <TableOfContents
        open={isTocOpen}
        onClose={toggleToc}
        toc={book.toc || []}
        currentChapter={''}
        onNavigate={(chapter) => {
          console.log('Navigate to', chapter);
          toggleToc();
        }}
      />

      <ReaderSearch
        open={isSearchOpen}
        onClose={toggleSearch}
        bookId={bookIdStr!}
      />

      <ReaderSettings
        open={isSettingsOpen}
        onClose={toggleSettings}
      />
    </div>
  );
}
