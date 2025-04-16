import './globals.css';
import ClientLayout from './ClientLayout';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'ShareTunes - LLMを活用した音楽推薦サービス',
  description: 'あなただけのパーソナライズされた音楽推薦を楽しみましょう',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body className="bg-gray-100 min-h-screen">
        <ClientLayout>
          {children}
        </ClientLayout>
      </body>
    </html>
  );
}