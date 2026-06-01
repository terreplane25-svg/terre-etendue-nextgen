import { getAllArticles } from "@/lib/articles";
import ExperiencesClient from "./ExperiencesClient";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Laboratoire de Physique Naturelle — Expériences",
  description:
    "Retracement historique des grandes expériences et démonstrations pédagogiques reproductibles : densité, pression, perspective, optique, magnétisme et forces.",
};

// Articles historiques existants (slugs connus)
const HISTORICAL_SLUGS = [
  "200-ans-de-resultats-nuls-darago-a-einstein",
  "leau-ne-ment-pas",
  "le-pendule-de-foucault-une-preuve-contestee",
  "les-horloges-atomiques-ne-prouvent-rien",
  "ce-quon-voit-quand-on-ne-devrait-plus-voir",
  "lhorizon-la-perspective-et-la-refraction",
  "le-mythe-deratosthene",
  "le-mouvement-zetetique-150-ans-de-resistance",
  "lespace-une-frontiere-infranchissable",
  "pression-lumiere-halos-rayons-et-ondes",
  "pourquoi-les-choses-montent-et-descendent",
  "les-marees-contre-lheliocentrisme",
];

export default function ExperiencesPage() {
  const allArticles = getAllArticles() as any[];

  // Section 1: Retracement historique (articles existants par slug)
  const historical = allArticles.filter((a) =>
    HISTORICAL_SLUGS.includes(a.slug)
  );

  // Section 2: Démonstrations (nouveaux articles avec tag physique-naturelle)
  const demonstrations = allArticles.filter(
    (a) => a.tags && a.tags.includes("physique-naturelle")
  );

  return (
    <ExperiencesClient
      historical={historical.map((a: any) => ({
        slug: a.slug,
        title: a.title,
        description: a.description || "",
        category: a.category,
        tags: a.tags || [],
        pinned: a.pinned || false,
        readTime: a.readTime || 5,
      }))}
      demonstrations={demonstrations.map((a: any) => ({
        slug: a.slug,
        title: a.title,
        description: a.description || "",
        category: a.category,
        tags: a.tags || [],
        pinned: a.pinned || false,
        readTime: a.readTime || 5,
      }))}
    />
  );
}
