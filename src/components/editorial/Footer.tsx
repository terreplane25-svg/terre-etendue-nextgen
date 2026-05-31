import { getAllArticles } from "@/lib/articles";
import { editorial } from "@/lib/editorial-tokens";

export default function Footer() {
  const articles = getAllArticles();
  const totalChars = articles.reduce((sum, a) => sum + (a.content?.length || 0), 0);
  const formattedChars = new Intl.NumberFormat("fr-FR").format(totalChars);

  return (
    <footer
      className="border-t mt-auto"
      style={{
        borderColor: editorial.rule,
        background: editorial.bgWarm,
      }}
    >
      <div className="max-w-7xl mx-auto px-6 md:px-10 py-12 md:py-14">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-8">
          {/* Left */}
          <div>
            <div
              className="text-[10px] font-semibold tracking-[0.2em] mb-2"
              style={{ fontFamily: editorial.fontLabel, color: editorial.ink }}
            >
              TERRE ÉTENDUE ISLAM
            </div>
            <div
              className="text-[13px] leading-relaxed"
              style={{ fontFamily: editorial.fontBody, color: editorial.inkMuted }}
            >
              Revue indépendante de cosmologie · Fondée 2024
              <br />
              Examen critique · Données empiriques · Sources sacrées
            </div>
          </div>

          {/* Right — Dynamic stats */}
          <div className="text-right">
            <div
              className="text-[11px] leading-[1.8]"
              style={{ fontFamily: editorial.fontMono, color: editorial.inkGhost }}
            >
              {articles.length} publications · {formattedChars} caractères
              <br />
              450+ sources primaires · 3 modèles 3D
            </div>
          </div>
        </div>

        {/* Bottom rule + copyright */}
        <div
          className="mt-10 pt-6 text-[11px]"
          style={{
            borderTop: `1px solid ${editorial.ruleFaint}`,
            fontFamily: editorial.fontSans,
            color: editorial.inkGhost,
          }}
        >
          © {new Date().getFullYear()} Terre Étendue Islam. Tous droits réservés.
        </div>
      </div>
    </footer>
  );
}
