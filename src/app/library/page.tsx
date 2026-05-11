import { getArticlesByCategory } from "@/lib/articles";
import LibraryClient from "./LibraryClient";

export const metadata = {
  title: "La Bibliothèque — Sources Sacrées | Terre Étendue Islam",
  description: "Sources coraniques, hadiths, travaux classiques et références théologiques.",
};

export default function LibraryPage() {
  const articles = getArticlesByCategory("library");
  return <LibraryClient articles={articles} />;
}
