"use client";

import { useState, useEffect, useMemo } from "react";
import type { LeaderboardData, ModelResult } from "@/types";
import { Navbar, Hero, StatsStrip, Leaderboard, About, Footer } from "@/components";

export default function Home() {
  const [data, setData] = useState<LeaderboardData>({ exam: {}, pos: {}, grammar: {} });

  useEffect(() => {
    fetch("/leaderboard.json")
      .then((r) => r.json())
      .then((d) => setData(d))
      .catch(() => console.log("Failed to load leaderboard data"));
  }, []);

  const modelCount = useMemo(() => {
    const models = new Set<string>();
    Object.values(data).forEach((task) => {
      Object.values(task).forEach((year) => {
        (year as ModelResult[]).forEach((m) => models.add(m.model));
      });
    });
    return models.size || 6;
  }, [data]);

  return (
    <>
      <Navbar />
      <Hero />
      <StatsStrip modelCount={modelCount} />
      <Leaderboard data={data} />
      <About />
      <Footer />
    </>
  );
}
