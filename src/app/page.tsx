import { getAllArticles } from "@/lib/articles";
import HomeClient from "./HomeClient";

export default function HomePage() {
  const articles = getAllArticles();

  const pillarCounts = {
    headquarters: articles.filter((a) => a.category === "headquarters").length,
    observatory: articles.filter((a) => a.category === "observatory").length,
    library: articles.filter((a) => a.category === "library").length,
  };

  return (
    <HomeClient
      articleCount={articles.length}
      pillarCounts={pillarCounts}
    />
  );
}
