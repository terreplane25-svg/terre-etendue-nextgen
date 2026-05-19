import Link from 'next/link';
import Image from 'next/image';

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 bg-[#050A12]">
      <div className="mb-10">
        <Image src="/images/globe-crossed.png" alt="Globe barré" width={260} height={260} priority />
      </div>
      <div className="border-2 border-[#D4A843] px-6 py-2 mb-8">
        <span className="text-[14px] font-orbitron tracking-[0.25em] text-[#D4A843]">ERREUR 404</span>
      </div>
      <h1 className="text-4xl md:text-5xl font-bold text-[#C8D8E8] text-center mb-8 leading-tight" style={{fontFamily:'Georgia, serif'}}>
        Ce modèle n&apos;existe<br/>pas non plus
      </h1>
      <p className="text-[16px] text-[#C8D8E8]/50 text-center mb-12 max-w-md leading-relaxed">
        La page que vous cherchez n&apos;a pas été trouvée.<br/>
        Comme la courbure — elle devrait être là, mais elle n&apos;y est pas.
      </p>
      <div className="flex flex-wrap gap-4 justify-center mb-14">
        <Link href="/" className="px-8 py-3 bg-[#D4A843] text-[#050A12] text-[13px] font-orbitron tracking-[0.15em] hover:bg-[#c09535] transition-colors">
          RETOUR À L&apos;ACCUEIL
        </Link>
        <Link href="/nexus" className="px-8 py-3 border-2 border-[#C8D8E8]/40 text-[#C8D8E8] text-[13px] font-orbitron tracking-[0.15em] hover:bg-[#C8D8E8]/10 transition-colors">
          EXPLORER LE NEXUS
        </Link>
      </div>
      <div className="text-center">
        <p className="text-[15px] italic text-[#D4A843]/70 mb-1 font-amiri">« Et la terre, comment elle a été étendue ? »</p>
        <p className="text-[13px] text-[#D4A843]/40">— Al-Ghashiyah, 88:20</p>
      </div>
    </div>
  );
}
