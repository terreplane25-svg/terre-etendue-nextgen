import { getArticlesByCategory } from "@/lib/articles";
import EditorialArticleList from "@/components/editorial/EditorialArticleList";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Le Quartier Général — Épistémologie",
  description:
    "Quinze études fondatrices sur l'épistémologie du modèle cosmologique standard.",
};

export default function HeadquartersPage() {
  const articles = getArticlesByCategory("headquarters");

  const formatted = articles.map((a, i) => ({
    slug: a.slug,
    title: a.title,
    description: a.description || "",
    type: "Publication",
    charCount: 0,
    citations: 0,
    pinned: a.pinned || false,
    order: i + 1,
  }));

  return (
    <EditorialArticleList
      pillar="headquarters"
      articles={formatted}
      title="Le Quartier Général"
      subtitle="Épistémologie & Méthode"
      description="Quinze études fondatrices qui examinent les présupposés de la cosmologie standard. De la chronologie du modèle héliocentrique aux failles méthodologiques des preuves classiques."
    />
  );
}
