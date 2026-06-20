import { Suspense } from "react";
import { getAllArticles } from "@/lib/articles";
import ExperiencesClient from "./ExperiencesClient";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Laboratoire de Physique Naturelle — Expériences",
  description: "Démonstrations pédagogiques reproductibles et retracement historique des grandes expériences.",
};

const HISTORICAL_SLUGS = [
  "leau-ne-ment-pas",
  "la-rotation-terrestre-deux-experiences-zero-preuve",
  "les-horloges-atomiques-ne-prouvent-rien",
  "la-perspective-pourquoi-les-objets-disparaissent",
  "lhorizon-la-perspective-et-la-refraction",
  "les-marees-contre-lheliocentrisme",
  "densite-pourquoi-les-choses-montent-et-descendent",
  "pression-lumiere-halos-rayons-et-ondes",
  "lespace-une-frontiere-infranchissable",
];

export default function ExperiencesPage() {
  const allArticles = getAllArticles() as any[];

  const historical = allArticles
    .filter((a) => HISTORICAL_SLUGS.includes(a.slug))
    .map((a: any) => ({
      slug: a.slug, title: a.title, description: a.description || "",
      category: a.category, tags: a.tags || [], pinned: a.pinned || false, readTime: a.readTime || 5,
    }));

  const demonstrations = allArticles
    .filter((a) => a.tags && a.tags.includes("physique-naturelle"))
    .map((a: any) => ({
      slug: a.slug, title: a.title, description: a.description || "",
      category: a.category, tags: a.tags || [], pinned: a.pinned || false, readTime: a.readTime || 5,
    }));

  return (
    <Suspense>
      <ExperiencesClient historical={historical} demonstrations={demonstrations} />
    </Suspense>
  );
}
