import type { Metadata } from "next";
import { Space_Grotesk, Inter, JetBrains_Mono } from "next/font/google";
import "../globals.css";
import { LanguageProvider } from "@/contexts/LanguageContext";
import { translations, Language } from "@/utils/translations";
import { GoogleAnalytics } from '@next/third-parties/google'

const spaceGrotesk = Space_Grotesk({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export async function generateMetadata({ params }: { params: Promise<{ lang: string }> }): Promise<Metadata> {
  const { lang } = await params;
  const t = translations[lang as Language] || translations.sk;
  return {
    title: t.meta.title,
    description: t.meta.description,
  };
}

export default async function RootLayout({
  children,
  params,
}: Readonly<{
  children: React.ReactNode;
  params: Promise<{ lang: string }>;
}>) {
  const { lang } = await params;
  const validLang = (lang as Language) in translations ? (lang as Language) : "sk";
  return (
    <html lang={validLang}>
      <body className={`${spaceGrotesk.variable} ${inter.variable} ${jetbrainsMono.variable} antialiased bg-[var(--color-cream)] text-[var(--color-ink)] min-h-screen`}>
        <LanguageProvider initialLanguage={validLang}>
          {children}
        </LanguageProvider>
      </body>
      <GoogleAnalytics gaId="G-4RNZMKLBDK" />
    </html>
  );
}

