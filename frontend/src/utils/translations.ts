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
            label_about: "ABOUT",
            title_why: "Why SlovakBench?",
            text_why_1: "Most LLM benchmarks focus on English, leaving low-resource languages underrepresented. SlovakBench provides rigorous evaluation for Slovak language capabilities.",
            text_why_2: "We use real-world tasks: official Maturita exams from NÚCEM, part-of-speech tagging from linguistic corpora, and grammar correction from native texts.",
            label_tasks: "TASKS",
            title_tasks: "Benchmark Tasks",
            coming_soon: "(coming soon)",
            task_exam: {
                title: "Maturita Exam",
                desc: "Slovak high school graduation exam with MCQ and open-ended questions."
            },
            task_pos: {
                title: "POS Tagging",
                desc: "Part-of-speech tagging on Slovak National Corpus data."
            },
            task_grammar: {
                title: "Grammar Correction",
                desc: "Detecting and correcting grammatical errors in Slovak text."
            }
        },
        footer: {
            resources: "RESOURCES",
            author: "AUTHOR",
            desc: "Open source benchmark for evaluating LLMs on Slovak language tasks.",
            copyright: "© 2025 SlovakBench. MIT License.",
            source: "Data sourced from official Slovak Maturita exams"
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
            label_about: "O PROJEKTE",
            title_why: "Prečo SlovakBench?",
            text_why_1: "Väčšina benchmarkov sa zameriava na angličtinu, čím zanedbáva nízko-zdrojové jazyky. SlovakBench prináša rigorózne hodnotenie schopností v slovenčine.",
            text_why_2: "Používame reálne úlohy: oficiálne maturity z NÚCEM, morfologickú analýzu z korpusov a gramatické korekcie natívnych textov.",
            label_tasks: "ÚLOHY",
            title_tasks: "Benchmarkové úlohy",
            coming_soon: "(pripravujeme)",
            task_exam: {
                title: "Maturita",
                desc: "Maturitná skúška s testovými otázkami a tvorením textu."
            },
            task_pos: {
                title: "Vetný rozbor",
                desc: "Morfologické značkovanie na dátach Slovenského národného korpusu."
            },
            task_grammar: {
                title: "Gramatika",
                desc: "Detekcia a oprava gramatických chýb."
            }
        },
        footer: {
            resources: "ZDROJE",
            author: "AUTOR",
            desc: "Open source benchmark pre hodnotenie LLM v slovenčine.",
            copyright: "© 2025 SlovakBench. MIT License.",
            source: "Dáta pochádzajú z oficiálnych maturít (NÚCEM)"
        }
    }
};
