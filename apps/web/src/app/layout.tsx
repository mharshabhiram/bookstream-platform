import type { Metadata, Viewport } from 'next';
import { Inter, Merriweather, JetBrains_Mono } from 'next/font/google';
import { Providers } from '@/components/providers';
import { Toaster } from 'sonner';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap',
});

const merriweather = Merriweather({
  weight: ['300', '400', '700', '900'],
  subsets: ['latin'],
  variable: '--font-serif',
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
});

export const metadata: Metadata = {
  title: {
    default: 'BookStream — Premium Ebook Reader',
    template: '%s | BookStream',
  },
  description:
    'Read, organize, and discover ebooks with the most beautiful reading experience.',
  keywords: ['ebook', 'reader', 'epub', 'pdf', 'books', 'reading'],
  authors: [{ name: 'BookStream' }],
  creator: 'BookStream',
  metadataBase: new URL('https://bookstream.io'),
  openGraph: {
    type: 'website',
    locale: 'en_US',
    siteName: 'BookStream',
  },
  twitter: {
    card: 'summary_large_image',
    creator: '@bookstream',
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#f8f6f3' },
    { media: '(prefers-color-scheme: dark)', color: '#1a1714' },
  ],
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${inter.variable} ${merriweather.variable} ${jetbrainsMono.variable}`}
    >
      <body className="min-h-screen bg-background font-sans">
        <Providers>
          {children}
          <Toaster
            position="bottom-right"
            toastOptions={{
              className: 'glass border-border',
            }}
          />
        </Providers>
      </body>
    </html>
  );
}
