import Link from "next/link";
import { getAllArticles } from "@/lib/articles";
import { editorial } from "@/lib/editorial-tokens";
import HomeClient from "./HomeClient";

export default function HomePage() {
  const articles = getAllArticles();

  const pillarCounts = {
    headquarters: articles.filter((a) => a.pillar === "headquarters").length,
    observatory: articles.filter((a) => a.pillar === "observatory").length,
    library: articles.filter((a) => a.pillar === "library").length,
  };

  return (
    <HomeClient
      articleCount={articles.length}
      pillarCounts={pillarCounts}
    />
  );
}
