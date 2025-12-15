import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const ABBREV_LOCALES = ["sk", "en"];
const DEFAULT_LOCALE = "sk";

export function proxy(request: NextRequest) {
    const { pathname } = request.nextUrl;

    // Check if there is any supported locale in the pathname
    const pathnameHasLocale = ABBREV_LOCALES.some(
        (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
    );

    if (pathnameHasLocale) {
        // If accessing /sk explicitly, redirect to / (canonical for default locale)
        // BUT allow if it's an internal rewrite (detected via search param)
        if (pathname === '/sk' || pathname.startsWith('/sk/')) {
            // If it's a rewrite, let it pass
            if (request.nextUrl.searchParams.has('internal_rewrite')) {
                return;
            }

            const newUrl = new URL(request.url);
            newUrl.pathname = pathname.replace(/^\/sk/, '') || '/';
            return NextResponse.redirect(newUrl);
        }
        return;
    }

    // If no locale in path, we are at root or internal path
    // Logic: 
    // 1. Check cookie 'language'
    // 2. Check Accept-Language header
    // 3. Default to 'sk'

    // NOTE: User requested "root / sk default language" but "go to /en if prefered".
    // So:
    const cookieLang = request.cookies.get("language")?.value;
    const preferredLocale = cookieLang === 'en' ? 'en' : 'sk'; // Simplified logic, can expand to accept-language later if needed

    if (preferredLocale === 'en' && pathname === '/') {
        // If user wants EN but is at /, redirect to /en
        return NextResponse.redirect(new URL(`/en`, request.url));
    }

    // Rewrite / to /sk so it hit src/app/[lang]
    if (pathname === '/') {
        const rewriteUrl = new URL(`/${DEFAULT_LOCALE}`, request.url);
        rewriteUrl.searchParams.set('internal_rewrite', 'true');
        return NextResponse.rewrite(rewriteUrl);
    }

    // For other paths without locale, rewrite to default locale
    const rewriteUrl = new URL(`/${DEFAULT_LOCALE}${pathname}`, request.url);
    rewriteUrl.searchParams.set('internal_rewrite', 'true');
    return NextResponse.rewrite(rewriteUrl);
}

export const config = {
    matcher: [
        // Skip all internal paths (_next) and static files
        "/((?!_next|logos|favicon.ico|robots.txt|.*\\.(?:svg|png|jpg|jpeg|gif|webp|json|css|js)).*)",
    ],
};
