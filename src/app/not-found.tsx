import Link from 'next/link';
import Image from 'next/image';

export default function NotFound() {
  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center px-6"
      style={{ background: '#FAFAF6', fontFamily: "'Plus Jakarta Sans', sans-serif" }}
    >
      <div className="mb-10">
        <Image src="/images/globe-crossed.png" alt="Globe barré" width={260} height={260} priority />
      </div>
      <div className="px-6 py-2 mb-8 border-2" style={{ borderColor: '#C48A2E' }}>
        <span className="text-[14px] tracking-[0.25em] font-semibold" style={{ color: '#C48A2E' }}>ERREUR 404</span>
      </div>
      <h1
        className="text-4xl md:text-5xl font-bold text-center mb-8 leading-tight"
        style={{ color: '#141210', fontFamily: 'Georgia, serif' }}
      >
        Ce modèle n&apos;existe<br/>pas non plus
      </h1>
      <p className="text-[16px] text-center mb-12 max-w-md leading-relaxed" style={{ color: '#8A857D' }}>
        La page que vous cherchez n&apos;a pas été trouvée.<br/>
        Comme la courbure — elle devrait être là, mais elle n&apos;y est pas.
      </p>
      <div className="flex flex-wrap gap-4 justify-center mb-14">
        <Link
          href="/"
          className="px-8 py-3 text-[13px] tracking-[0.15em] font-semibold hover:opacity-90 transition-colors"
          style={{ background: '#C48A2E', color: '#FFFFFF' }}
        >
          RETOUR À L&apos;ACCUEIL
        </Link>
        <Link
          href="/nexus"
          className="px-8 py-3 border-2 text-[13px] tracking-[0.15em] font-semibold transition-colors"
          style={{ borderColor: 'rgba(20,18,16,0.2)', color: '#141210' }}
        >
          EXPLORER LE NEXUS
        </Link>
      </div>
      <div className="text-center">
        <p className="text-[15px] italic mb-1" style={{ color: 'rgba(196,138,46,0.7)' }}>« Et la terre, comment elle a été étendue ? »</p>
        <p className="text-[13px]" style={{ color: 'rgba(196,138,46,0.4)' }}>— Al-Ghashiyah, 88:20</p>
      </div>
    </div>
  );
}
