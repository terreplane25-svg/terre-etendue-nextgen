import { getArticlesByCategory } from "@/lib/articles";
import HeadquartersClient from "./HeadquartersClient";

export const metadata = {
  title: "Le Q.G. — Épistémologie | Terre Étendue Islam",
  description: "Fondements méthodologiques, cadre de pensée et philosophie de la recherche.",
};

export default function HeadquartersPage() {
  const articles = getArticlesByCategory("headquarters");
  return <HeadquartersClient articles={articles} />;
}
