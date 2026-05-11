import { getArticlesByCategory } from "@/lib/articles";
import ObservatoryClient from "./ObservatoryClient";

export const metadata = {
  title: "L\u2019Observatoire — Empirique | Terre Étendue Islam",
  description: "Observations empiriques, données scientifiques et analyses factuelles.",
};

export default function ObservatoryPage() {
  const articles = getArticlesByCategory("observatory");
  return <ObservatoryClient articles={articles} />;
}
