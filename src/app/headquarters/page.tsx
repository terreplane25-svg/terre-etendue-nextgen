import { getArticlesByCategory } from "@/lib/articles";
import HeadquartersClient from "./HeadquartersClient";

export const metadata = {
  title: "Le Q.G. — Épistémologie",
  description: "Fondements méthodologiques, cadre de pensée et philosophie de la recherche.",
};

export default function HeadquartersPage() {
  const articles = getArticlesByCategory("headquarters");
  return <HeadquartersClient articles={articles} />;
}
