"use client";

import HudArticleList from "@/components/HudArticleList";
import type { ArticleMeta } from "@/lib/articles";

export default function LibraryClient({ articles }: { articles: ArticleMeta[] }) {
  return <HudArticleList articles={articles} category="library" />;
}
