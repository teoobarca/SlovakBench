export type Language = 'en' | 'sk';

export const translations = {
    en: {
        meta: {
            title: "SlovakBench — Slovak LLM Benchmark",
            description: "Evaluating Large Language Models on Slovak language tasks.",
        },
        nav: {
            leaderboard: "Leaderboard",
            about: "About",
            github: "GitHub",
        },
        hero: {
            label: "BENCHMARK",
            title_start: "Slovak",
            title_end: "Bench",
            description: "Evaluating Large Language Models on Slovak language tasks. Rigorous benchmarks for grammar, comprehension, and linguistic understanding.",
        },
        stats: {
            models_evaluated: "Models Evaluated",
            task_categories: "Task Categories",
            total_questions: "Total Questions",
            latest_year: "Latest Year",
        },
        leaderboard: {
            label: "RESULTS",
            title: "Leaderboard",
            last_updated: "Last updated: December 2025",
            tasks: {
                exam: "Maturita Exam",
                pos: "POS Tagging",
                grammar: "Grammar",
            },
            descriptions: {
                exam: {
                    title: "Slovak Maturita Exam",
                    desc: "Official Slovak high school graduation exam (Maturita) in Slovak Language and Literature. Includes MCQ and short-text answers covering grammar, literature, and comprehension."
                },
                pos: {
                    title: "Sentence Analysis",
                    desc: "Evaluates the model's ability to identify parts of speech (POS), base forms (lemmas), and syntactic relationships.",
                },
                grammar: {
                    title: "Grammar Correction",
                    desc: "Detecting and correcting grammatical and spelling errors in Slovak text."
                }
            },
            filters: {
                year: "Year",
                provider: "Provider",
                all_providers: "All"
            },
            table: {
                rank: "Rank",
                model: "Model",
                score: "Score (%)",
                mcq: "MCQ (%)",
                text: "Text (%)",
                pos: "Parts of Speech",
                lemma: "Base Form",
                dep: "Syntax",
                latency: "Latency",
                cost: "Cost",
                no_data: "No data available",
                no_data_desc: "This task/year combination hasn't been evaluated yet.",
                failed_questions: "questions failed",
                view_table: "Table",
                view_scatter: "Scatter"
            },
            scatter: {
                score_vs_cost: "Score vs Cost",
                y_axis: "Score (%)",
                x_axis: "Cost ($)"
            }
        },
        about: {
            label_story: "OUR STORY",
            title_story: "The First Slovak LLM Benchmark",
            text_story_1: "When we started exploring how well AI language models understand Slovak, we found a gap: there was no comprehensive benchmark for evaluating LLMs on Slovak language tasks.",
            text_story_2: "So we built one. SlovakBench is the first open-source benchmark specifically designed to measure how well large language models perform on Slovak — from understanding grammar to passing our national Maturita exam.",
            label_about: "METHODOLOGY",
            title_why: "Why It Matters",
            text_why_1: "Most AI benchmarks focus on English, leaving languages like Slovak underrepresented. This means we have no reliable way to compare how different AI models handle our language.",
            text_why_2: "SlovakBench uses real-world tasks: official Maturita exams, linguistic analysis from the Slovak National Corpus, and grammar correction. No shortcuts, no synthetic data.",
            label_tasks: "TASKS",
            title_tasks: "What We Test",
            coming_soon: "(coming soon)",
            task_exam: {
                title: "Maturita Exam",
                desc: "Official Slovak high school graduation exam — the ultimate test of language and literature comprehension."
            },
            task_pos: {
                title: "Sentence Analysis",
                desc: "Parts of speech, lemmas, and syntactic relationships on Slovak National Corpus data."
            },
            task_grammar: {
                title: "Grammar Correction",
                desc: "Finding and fixing grammatical errors in authentic Slovak text."
            }
        },
        footer: {
            resources: "RESOURCES",
            author: "AUTHOR",
            desc: "Open source benchmark for evaluating LLMs on Slovak language tasks.",
            copyright: "© 2025 SlovakBench. MIT License.",
            source: "Data: NÚCEM (Maturita), Slovak National Corpus (UD SNK)"
        }
    },
    sk: {
        meta: {
            title: "SlovakBench — Benchmark Slovenských LLM",
            description: "Hodnotenie veľkých jazykových modelov na slovenských úlohách.",
        },
        nav: {
            leaderboard: "Rebríček",
            about: "O projekte",
            github: "GitHub",
        },
        hero: {
            label: "BENCHMARK",
            title_start: "Slovak",
            title_end: "Bench",
            description: "Hodnotenie veľkých jazykových modelov na slovenských úlohách. Rigorózne testy gramatiky, porozumenia a lingvistických schopností.",
        },
        stats: {
            models_evaluated: "Hodnotené modely",
            task_categories: "Kategórie úloh",
            total_questions: "Počet otázok",
            latest_year: "Posledný ročník",
        },
        leaderboard: {
            label: "VÝSLEDKY",
            title: "Rebríček",
            last_updated: "Posledná aktualizácia: December 2025",
            tasks: {
                exam: "Maturita",
                pos: "Vetný rozbor",
                grammar: "Gramatika",
            },
            descriptions: {
                exam: {
                    title: "Maturitná skúška",
                    desc: "Oficiálna maturitná skúška zo slovenského jazyka a literatúry. Zahŕňa testové otázky (MCQ) a krátke odpovede zamerané na gramatiku, literatúru a porozumenie."
                },
                pos: {
                    title: "Vetný rozbor",
                    desc: "Schopnosť modelov správne určiť slovné druhy, základné tvary slov a vzťahy medzi slovami vo vete (syntax).",
                },
                grammar: {
                    title: "Korekcia gramatiky",
                    desc: "Oprava gramatických chýb a preklepov v slovenskom texte.",
                }
            },
            filters: {
                year: "Rok",
                provider: "Poskytovateľ",
                all_providers: "Všetci"
            },
            table: {
                rank: "Poradie",
                model: "Model",
                score: "Skóre (%)",
                mcq: "Test (%)",
                text: "Text (%)",
                pos: "Slovné druhy",
                lemma: "Základ slova",
                dep: "Vetné členy",
                latency: "Odozva",
                cost: "Cena",
                no_data: "Dáta nedostupné",
                no_data_desc: "Pre túto kombináciu úlohy a roku zatiaľ neexistujú výsledky.",
                failed_questions: "zlyhaní",
                view_table: "Tabuľka",
                view_scatter: "Graf"
            },
            scatter: {
                score_vs_cost: "Skóre vs Cena",
                y_axis: "Skóre (%)",
                x_axis: "Cena ($)"
            }
        },
        about: {
            label_story: "NÁŠ PRÍBEH",
            title_story: "Prvý slovenský LLM benchmark",
            text_story_1: "Keď sme začali skúmať, ako dobre AI jazykové modely rozumejú slovenčine, zistili sme medzeru: neexistoval žiadny komplexný benchmark na hodnotenie veľkých jazykových modelov v slovenčine.",
            text_story_2: "Tak sme si ho vytvorili. SlovakBench je prvý open-source benchmark špecificky navrhnutý na meranie toho, ako dobre veľké jazykové modely zvládajú slovenčinu — od gramatiky až po maturitnú skúšku.",
            label_about: "METODOLÓGIA",
            title_why: "Prečo na tom záleží",
            text_why_1: "Väčšina AI benchmarkov sa zameriava na angličtinu, čím jazyky ako slovenčina zostávajú podreprezentované. To znamená, že nemáme spoľahlivý spôsob porovnania, ako rôzne AI modely zvládajú náš jazyk.",
            text_why_2: "SlovakBench používa reálne úlohy: oficiálne maturitné skúšky, lingvistickú analýzu zo Slovenského národného korpusu a opravu gramatiky. Žiadne skratky, žiadne syntetické dáta.",
            label_tasks: "ÚLOHY",
            title_tasks: "Čo testujeme",
            coming_soon: "(pripravujeme)",
            task_exam: {
                title: "Maturita",
                desc: "Oficiálna slovenská maturitná skúška — ultimátny test jazykového a literárneho porozumenia."
            },
            task_pos: {
                title: "Vetný rozbor",
                desc: "Slovné druhy, základné tvary a syntaktické vzťahy na dátach Slovenského národného korpusu."
            },
            task_grammar: {
                title: "Gramatika",
                desc: "Vyhľadávanie a oprava gramatických chýb v autentickom slovenskom texte."
            }
        },
        footer: {
            resources: "ZDROJE",
            author: "AUTOR",
            desc: "Open source benchmark pre hodnotenie LLM v slovenčine.",
            copyright: "© 2025 SlovakBench. MIT License.",
            source: "Dáta: NÚCEM (Maturita), Slovenský národný korpus (UD SNK)"
        }
    }
};
