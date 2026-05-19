import Link from 'next/link';
import Image from 'next/image';

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 bg-[#F5F0E8]">
      {/* Globe barré */}
      <div className="mb-8">
        <Image
          src="/images/globe-crossed.png"
          alt="Globe terrestre barré"
          width={280}
          height={280}
          priority
        />
      </div>

      {/* Badge ERREUR 404 */}
      <div className="border-2 border-[#D4A843] px-6 py-2 mb-6">
        <span className="text-[13px] font-orbitron tracking-[0.25em] text-[#D4A843]">
          ERREUR 404
        </span>
      </div>

      {/* Titre */}
      <h1 className="text-4xl md:text-5xl font-bold text-[#1a1a1a] text-center mb-8 leading-tight"
          style={{ fontFamily: 'Georgia, serif' }}>
        Ce modèle n&apos;existe<br />pas non plus
      </h1>

      {/* Sous-titre */}
      <p className="text-[15px] text-[#666] text-center mb-10 max-w-md leading-relaxed">
        La page que vous cherchez n&apos;a pas été trouvée.<br />
        Comme la courbure — elle devrait être là, mais elle n&apos;y est pas.
      </p>

      {/* Boutons */}
      <div className="flex flex-wrap gap-4 justify-center mb-12">
        <Link href="/"
          className="px-8 py-3 bg-[#D4A843] text-white text-[12px] font-orbitron tracking-[0.15em] hover:bg-[#c09535] transition-colors">
          RETOUR À L&apos;ACCUEIL
        </Link>
        <Link href="/nexus"
          className="px-8 py-3 border-2 border-[#1a1a1a] text-[#1a1a1a] text-[12px] font-orbitron tracking-[0.15em] hover:bg-[#1a1a1a] hover:text-white transition-colors">
          EXPLORER LE NEXUS
        </Link>
      </div>

      {/* Citation coranique */}
      <div className="text-center">
        <p className="text-[14px] italic text-[#D4A843]/80 mb-1">
          « Et la terre, comment elle a été étendue ? »
        </p>
        <p className="text-[13px] text-[#D4A843]/60">
          — Al-Ghashiyah, 88:20
        </p>
      </div>
    </div>
  );
}
