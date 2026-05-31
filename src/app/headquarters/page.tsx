import { getAllArticles } from "@/lib/articles";
import EditorialArticleList from "@/components/editorial/EditorialArticleList";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Le Quartier Général — Épistémologie",
  description:
    "Quinze études fondatrices sur l'épistémologie du modèle cosmologique standard.",
};

export default function HeadquartersPage() {
  const allArticles = getAllArticles();
  const articles = allArticles.filter((a: any) => a.pillar === "headquarters");

  const formatted = articles.map((a: any, i: number) => ({
    slug: a.slug,
    title: a.title,
    description: a.description || "",
    type: a.type || "Publication",
    charCount: a.content?.length || 0,
    citations: a.citations || 0,
    pinned: a.pinned || false,
    order: a.order || i + 1,
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
