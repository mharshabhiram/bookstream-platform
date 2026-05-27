'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Search, BookOpen, Heart, Clock, Archive, LayoutGrid, List } from 'lucide-react';
import Link from 'next/link';
import { booksApi, userApi } from '@/lib/api';
import { BookCard } from '@/components/library/BookCard';
import { UploadModal } from '@/components/library/UploadModal';
import { Sidebar } from '@/components/layout/Sidebar';
import { TopBar } from '@/components/layout/TopBar';

type ViewMode = 'grid' | 'list';
type FilterTab = 'all' | 'reading' | 'completed' | 'favorites' | 'archived';

export default function LibraryPage() {
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  const [activeTab, setActiveTab] = useState<FilterTab>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showUpload, setShowUpload] = useState(false);

  const { data: libraryData, isLoading } = useQuery({
    queryKey: ['library', activeTab],
    queryFn: () =>
      userApi.getLibrary({
        status: activeTab === 'all' || activeTab === 'favorites' || activeTab === 'archived' 
          ? undefined 
          : activeTab,
        is_favorite: activeTab === 'favorites' ? true : undefined,
        is_archived: activeTab === 'archived' ? true : false,
      }),
  });

  const { data: continueReading } = useQuery({
    queryKey: ['continue-reading'],
    queryFn: () => userApi.getContinueReading(),
  });

  const books = libraryData?.data || [];
  const continueBooks = continueReading?.data || [];

  const filteredBooks = searchQuery
    ? books.filter((b: any) =>
        b.book.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        b.book.author_name?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : books;

  const tabs = [
    { id: 'all' as FilterTab, label: 'All Books', icon: BookOpen },
    { id: 'reading' as FilterTab, label: 'Reading', icon: Clock },
    { id: 'completed' as FilterTab, label: 'Completed', icon: BookOpen },
    { id: 'favorites' as FilterTab, label: 'Favorites', icon: Heart },
    { id: 'archived' as FilterTab, label: 'Archived', icon: Archive },
  ];

  return (
    <div className="flex h-screen bg-background">
      <Sidebar />

      <div className="flex flex-1 flex-col overflow-hidden">
        <TopBar />

        <main className="flex-1 overflow-y-auto">
          {/* Continue Reading */}
          {continueBooks.length > 0 && activeTab === 'all' && !searchQuery && (
            <section className="px-6 py-6 lg:px-10">
              <h2 className="mb-4 text-lg font-semibold">Continue Reading</h2>
              <div className="flex gap-4 overflow-x-auto pb-2">
                {continueBooks.map((item: any) => (
                  <Link
                    key={item.id}
                    href={`/reader/${item.book_id}`}
                    className="group relative flex-shrink-0 w-48"
                  >
                    <div className="relative aspect-[2/3] overflow-hidden rounded-xl bg-muted">
                      {item.book.cover_url ? (
                        <img
                          src={item.book.cover_url}
                          alt={item.book.title}
                          className="h-full w-full object-cover transition-transform group-hover:scale-105"
                        />
                      ) : (
                        <div className="flex h-full items-center justify-center">
                          <BookOpen className="h-8 w-8 text-muted-foreground" />
                        </div>
                      )}
                      <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/20">
                        <div
                          className="h-full bg-primary transition-all"
                          style={{ width: `${item.last_progress_percent}%` }}
                        />
                      </div>
                    </div>
                    <h3 className="mt-2 text-sm font-medium line-clamp-1">{item.book.title}</h3>
                    <p className="text-xs text-muted-foreground">
                      {Math.round(item.last_progress_percent)}% complete
                    </p>
                  </Link>
                ))}
              </div>
            </section>
          )}

          {/* Library Header */}
          <section className="sticky top-0 z-10 bg-background/80 px-6 py-4 backdrop-blur-xl lg:px-10">
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-2 overflow-x-auto">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                      activeTab === tab.id
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                    }`}
                  >
                    <tab.icon className="h-4 w-4" />
                    {tab.label}
                  </button>
                ))}
              </div>

              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search your library..."
                    className="w-48 rounded-lg border border-input bg-background py-2 pl-9 pr-4 text-sm outline-none transition-all focus:border-primary focus:ring-2 focus:ring-primary/20 lg:w-64"
                  />
                </div>
                <button
                  onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
                  className="rounded-lg border border-input p-2 text-muted-foreground transition-colors hover:bg-muted"
                >
                  {viewMode === 'grid' ? <List className="h-4 w-4" /> : <LayoutGrid className="h-4 w-4" />}
                </button>
                <button
                  onClick={() => setShowUpload(true)}
                  className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-all hover:opacity-90"
                >
                  <Plus className="h-4 w-4" />
                  Upload
                </button>
              </div>
            </div>
          </section>

          {/* Book Grid/List */}
          <section className="px-6 py-4 lg:px-10">
            {isLoading ? (
              <div className={`grid gap-4 ${viewMode === 'grid' ? 'sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5' : ''}`}>
                {Array.from({ length: 8 }).map((_, i) => (
                  <div key={i} className="animate-pulse">
                    <div className={`rounded-xl bg-muted ${viewMode === 'grid' ? 'aspect-[2/3]' : 'h-24'}`} />
                    <div className="mt-2 h-4 w-3/4 rounded bg-muted" />
                    <div className="mt-1 h-3 w-1/2 rounded bg-muted" />
                  </div>
                ))}
              </div>
            ) : filteredBooks.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20 text-center">
                <BookOpen className="h-12 w-12 text-muted-foreground/50" />
                <h3 className="mt-4 text-lg font-medium">No books yet</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  Upload your first ebook to get started
                </p>
                <button
                  onClick={() => setShowUpload(true)}
                  className="mt-4 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground"
                >
                  Upload Book
                </button>
              </div>
            ) : (
              <motion.div
                layout
                className={`grid gap-4 ${
                  viewMode === 'grid'
                    ? 'grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6'
                    : 'grid-cols-1'
                }`}
              >
                <AnimatePresence>
                  {filteredBooks.map((item: any) => (
                    <BookCard
                      key={item.id}
                      book={item.book}
                      userBook={item}
                      viewMode={viewMode}
                    />
                  ))}
                </AnimatePresence>
              </motion.div>
            )}
          </section>
        </main>
      </div>

      <UploadModal open={showUpload} onClose={() => setShowUpload(false)} />
    </div>
  );
}
