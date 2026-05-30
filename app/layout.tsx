import type { Metadata } from "next";
import "./globals.css";
import Navigation from "@/components/editorial/Navigation";
import Footer from "@/components/editorial/Footer";

export const metadata: Metadata = {
  metadataBase: new URL("https://terre-etendue-islam.fr"),
  title: {
    default: "Terre Étendue Islam — Revue de Cosmologie Indépendante",
    template: "%s | Terre Étendue Islam",
  },
  description:
    "Plateforme de recherche dédiée à l'examen critique du modèle cosmologique standard à la lumière des données empiriques, de l'épistémologie et des sources sacrées de l'Islam.",
  openGraph: {
    type: "website",
    locale: "fr_FR",
    siteName: "Terre Étendue Islam",
  },
  twitter: {
    card: "summary_large_image",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" className="scroll-smooth">
      <body className="min-h-screen flex flex-col" style={{ background: "#FAFAF8" }}>
        <Navigation />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
