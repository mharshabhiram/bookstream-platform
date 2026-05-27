'use client';

import { motion } from 'framer-motion';
import { BookOpen, Sparkles, Library, ArrowRight } from 'lucide-react';
import Link from 'next/link';

export default function LandingPage() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-background">
      {/* Animated background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-book-100/30 via-background to-book-200/20 dark:from-book-900/20 dark:via-background dark:to-book-800/10" />

      {/* Floating orbs */}
      <motion.div
        className="absolute top-20 left-[10%] w-72 h-72 rounded-full bg-book-300/20 dark:bg-book-700/10 blur-3xl"
        animate={{
          y: [0, -30, 0],
          scale: [1, 1.1, 1],
        }}
        transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
      />
      <motion.div
        className="absolute bottom-20 right-[15%] w-96 h-96 rounded-full bg-primary/10 dark:bg-primary/5 blur-3xl"
        animate={{
          y: [0, 20, 0],
          scale: [1, 1.05, 1],
        }}
        transition={{ duration: 10, repeat: Infinity, ease: 'easeInOut', delay: 2 }}
      />

      {/* Navigation */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-6 lg:px-12">
        <div className="flex items-center gap-2">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-primary-foreground">
            <BookOpen className="h-5 w-5" />
          </div>
          <span className="text-xl font-bold tracking-tight">BookStream</span>
        </div>
        <div className="flex items-center gap-4">
          <Link
            href="/login"
            className="rounded-lg px-4 py-2 text-sm font-medium text-foreground/80 transition-colors hover:text-foreground"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="rounded-lg bg-primary px-5 py-2.5 text-sm font-medium text-primary-foreground shadow-lg shadow-primary/20 transition-all hover:shadow-primary/30 hover:scale-105"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <main className="relative z-10 flex flex-col items-center justify-center px-6 pt-20 pb-32 text-center lg:px-12">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-6 inline-flex items-center gap-2 rounded-full border border-border bg-card/50 px-4 py-1.5 text-sm text-muted-foreground backdrop-blur-sm"
        >
          <Sparkles className="h-3.5 w-3.5 text-primary" />
          The most beautiful way to read ebooks
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="max-w-4xl text-5xl font-bold tracking-tight text-foreground sm:text-6xl lg:text-7xl"
        >
          Your personal{' '}
          <span className="bg-gradient-to-r from-primary to-book-500 bg-clip-text text-transparent">
            reading sanctuary
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-6 max-w-2xl text-lg text-muted-foreground"
        >
          Read EPUBs and PDFs with a premium, customizable experience. Organize your library,
          track your progress, and discover your next favorite book.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-10 flex flex-col gap-4 sm:flex-row"
        >
          <Link
            href="/register"
            className="group inline-flex items-center gap-2 rounded-xl bg-primary px-8 py-4 text-base font-semibold text-primary-foreground shadow-xl shadow-primary/25 transition-all hover:shadow-primary/40 hover:scale-105"
          >
            Start Reading Free
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </Link>
          <Link
            href="/library"
            className="inline-flex items-center gap-2 rounded-xl border border-border bg-card/50 px-8 py-4 text-base font-semibold text-foreground backdrop-blur-sm transition-all hover:bg-card"
          >
            <Library className="h-4 w-4" />
            Browse Library
          </Link>
        </motion.div>

        {/* Feature cards */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="mt-24 grid max-w-5xl gap-6 sm:grid-cols-3"
        >
          {[
            {
              icon: BookOpen,
              title: 'Premium Reader',
              desc: 'Customizable fonts, themes, and layouts for the perfect reading experience.',
            },
            {
              icon: Library,
              title: 'Smart Library',
              desc: 'Organize with shelves, collections, and intelligent recommendations.',
            },
            {
              icon: Sparkles,
              title: 'Sync Everything',
              desc: 'Your progress, highlights, and notes synced across all devices.',
            },
          ].map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 + i * 0.1 }}
              className="group relative overflow-hidden rounded-2xl border border-border bg-card/50 p-6 backdrop-blur-sm transition-all hover:border-primary/20 hover:bg-card"
            >
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
                <feature.icon className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold">{feature.title}</h3>
              <p className="mt-2 text-sm text-muted-foreground">{feature.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </main>
    </div>
  );
}
