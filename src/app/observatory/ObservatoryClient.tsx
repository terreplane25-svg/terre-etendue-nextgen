"use client";

import HudArticleList from "@/components/HudArticleList";
import type { ArticleMeta } from "@/lib/articles";

export default function ObservatoryClient({ articles }: { articles: ArticleMeta[] }) {
  return <HudArticleList articles={articles} category="observatory" />;
}
