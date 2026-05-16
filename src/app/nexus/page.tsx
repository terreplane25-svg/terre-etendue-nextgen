import NexusClient from "./NexusClient";

export const metadata = {
  title: "Le Nexus — Graphe de Connaissances",
  description: "Visualisation interactive des connexions entre tous les articles et concepts de la plateforme.",
};

export default function NexusPage() {
  return <NexusClient />;
}
