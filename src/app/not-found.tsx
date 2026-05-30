import Link from 'next/link';
import Image from 'next/image';

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 bg-[var(--void)]">
      <div className="mb-10">
        <Image src="/images/globe-crossed.png" alt="Globe barré" width={260} height={260} priority />
      </div>
      <div className="border-2 border-[var(--gold)] px-6 py-2 mb-8">
        <span className="text-[14px] font-orbitron tracking-[0.25em] text-[var(--gold)]">ERREUR 404</span>
      </div>
      <h1 className="text-4xl md:text-5xl font-bold text-[var(--text)] text-center mb-8 leading-tight" style={{fontFamily:'Georgia, serif'}}>
        Ce modèle n&apos;existe<br/>pas non plus
      </h1>
      <p className="text-[16px] text-[var(--text)]/50 text-center mb-12 max-w-md leading-relaxed">
        La page que vous cherchez n&apos;a pas été trouvée.<br/>
        Comme la courbure — elle devrait être là, mais elle n&apos;y est pas.
      </p>
      <div className="flex flex-wrap gap-4 justify-center mb-14">
        <Link href="/" className="px-8 py-3 bg-[var(--gold)] text-[var(--void)] text-[13px] font-orbitron tracking-[0.15em] hover:opacity-90 transition-colors">
          RETOUR À L&apos;ACCUEIL
        </Link>
        <Link href="/nexus" className="px-8 py-3 border-2 border-[var(--text-30)] text-[var(--text)] text-[13px] font-orbitron tracking-[0.15em] hover:bg-[var(--text-15)] transition-colors">
          EXPLORER LE NEXUS
        </Link>
      </div>
      <div className="text-center">
        <p className="text-[15px] italic text-[var(--gold)]/70 mb-1 font-amiri">« Et la terre, comment elle a été étendue ? »</p>
        <p className="text-[13px] text-[var(--gold)]/40">— Al-Ghashiyah, 88:20</p>
      </div>
    </div>
  );
}
