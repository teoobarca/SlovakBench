'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { translations, Language } from '@/utils/translations';

interface LanguageContextType {
    language: Language;
    setLanguage: (lang: Language) => void;
    t: typeof translations.en;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children, initialLanguage }: { children: ReactNode; initialLanguage: Language }) {
    const [language, setLanguageState] = useState<Language>(initialLanguage);

    // Sync state if initialLanguage changes (e.g. navigation)
    useEffect(() => {
        setLanguageState(initialLanguage);
    }, [initialLanguage]);

    // Change language via URL
    const handleSetLanguage = (lang: Language) => {
        setLanguageState(lang);
        document.cookie = `language=${lang}; path=/; max-age=31536000`; // 1 year

        // Calculate new path
        const currentPath = window.location.pathname;
        let newPath = currentPath;

        if (lang === 'en') {
            // Switch to EN: /foo -> /en/foo (unless already /en)
            if (!currentPath.startsWith('/en')) {
                newPath = `/en${currentPath === '/' ? '' : currentPath}`;
            }
        } else {
            // Switch to SK: /en/foo -> /foo
            if (currentPath.startsWith('/en')) {
                newPath = currentPath.replace(/^\/en/, '') || '/';
            }
        }

        window.location.href = newPath;
    };

    return (
        <LanguageContext.Provider value={{ language, setLanguage: handleSetLanguage, t: translations[language] || translations.sk }}>
            {children}
        </LanguageContext.Provider>
    );
}

export function useLanguage() {
    const context = useContext(LanguageContext);
    if (context === undefined) {
        throw new Error('useLanguage must be used within a LanguageProvider');
    }
    return context;
}
