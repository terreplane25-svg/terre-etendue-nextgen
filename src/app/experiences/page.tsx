import { Suspense } from "react";
import { getAllArticles } from "@/lib/articles";
import ExperiencesClient from "./ExperiencesClient";
import type { Metadata } from "next";

export const metadata: Metadata = {
  alternates: { canonical: '/experiences' },
  title: "Laboratoire de Physique Naturelle — Expériences",
  description: "Démonstrations pédagogiques reproductibles : densité, pression, perspective, forces — la physique se vérifie à la main.",
};

export default function ExperiencesPage() {
  const allArticles = getAllArticles() as any[];

  // Articles de la catégorie « expériences » OU tagués « physique-naturelle »
  // (les analyses observatoire taguées physique-naturelle vivent ici, pas sur /observatory).
  const demonstrations = allArticles
    .filter((a) => a.category === "experiences" || (a.tags && a.tags.includes("physique-naturelle")))
    .map((a: any) => ({
      slug: a.slug, title: a.title, description: a.description || "",
      category: a.category, tags: a.tags || [], pinned: a.pinned || false, readTime: a.readTime || 5,
    }));

  return (
    <Suspense>
      <ExperiencesClient demonstrations={demonstrations} />
    </Suspense>
  );
}
