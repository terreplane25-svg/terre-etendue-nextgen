"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { editorial } from "@/lib/editorial-tokens";

// ─── Search (Cmd+K) ───
// Import your existing SearchCommand component here
// import SearchCommand from "./SearchCommand";

const navLinks = [
  { href: "/", label: "Accueil" },
  { href: "/headquarters", label: "Q.G." },
  { href: "/observatory", label: "Observatoire" },
  { href: "/library", label: "Bibliothèque" },
  { href: "/lab", label: "Lab" },
  { href: "/nexus", label: "Nexus" },
];

export default function Navigation() {
  const pathname = usePathname();
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 24);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  // Lock body scroll when mobile menu open
  useEffect(() => {
    document.body.style.overflow = mobileOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [mobileOpen]);

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  return (
    <>
      <nav
        className="sticky top-0 z-50 transition-all duration-300"
        style={{
          background: scrolled ? "rgba(250,250,248,0.92)" : editorial.bg,
          backdropFilter: scrolled ? "blur(12px)" : "none",
          WebkitBackdropFilter: scrolled ? "blur(12px)" : "none",
          borderBottom: `1px solid ${scrolled ? editorial.ruleFaint : "transparent"}`,
        }}
      >
        <div className="max-w-7xl mx-auto px-6 md:px-10 h-[72px] flex items-center justify-between">
          {/* ─── Logo ─── */}
          <Link href="/" className="flex items-baseline gap-2.5 no-underline group">
            {/* Hexagonal mark */}
            <svg width="26" height="26" viewBox="0 0 32 32" className="mr-1 transition-transform duration-300 group-hover:rotate-[30deg]">
              <polygon
                points="16,2 29,9 29,23 16,30 3,23 3,9"
                fill="none"
                stroke={editorial.bronze}
                strokeWidth="1.4"
              />
              <polygon
                points="16,8 23,12 23,20 16,24 9,20 9,12"
                fill="none"
                stroke={editorial.bronze}
                strokeWidth="0.7"
              />
              <circle cx="16" cy="16" r="2.5" fill={editorial.bronze} opacity="0.25" />
            </svg>
            <span
              className="text-[13px] font-semibold tracking-[0.18em]"
              style={{ fontFamily: editorial.fontLabel, color: editorial.ink }}
            >
              TERRE ÉTENDUE
            </span>
            <span
              className="text-[9px] font-medium tracking-[0.25em] -ml-1"
              style={{ fontFamily: editorial.fontLabel, color: editorial.bronze }}
            >
              ISLAM
            </span>
          </Link>

          {/* ─── Desktop Nav Links ─── */}
          <div className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="no-underline transition-colors duration-200"
                style={{
                  fontFamily: editorial.fontSans,
                  fontSize: 13,
                  fontWeight: 500,
                  color: isActive(link.href) ? editorial.ink : editorial.inkGhost,
                  borderBottom: isActive(link.href)
                    ? `2px solid ${editorial.bronze}`
                    : "2px solid transparent",
                  paddingBottom: 4,
                  letterSpacing: "0.02em",
                }}
              >
                {link.label}
              </Link>
            ))}

            {/* Search trigger */}
            <button
              className="flex items-center gap-2 transition-colors duration-200"
              style={{
                background: "none",
                border: `1px solid ${editorial.ruleFaint}`,
                borderRadius: 2,
                padding: "6px 12px",
                fontFamily: editorial.fontMono,
                fontSize: 11,
                color: editorial.inkGhost,
              }}
              // onClick={() => setSearchOpen(true)}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="11" cy="11" r="8" />
                <path d="M21 21l-4.35-4.35" />
              </svg>
              <span className="hidden lg:inline">Rechercher</span>
              <kbd
                className="hidden lg:inline ml-2 px-1.5 py-0.5 rounded-sm text-[10px]"
                style={{ background: editorial.bgWarm, color: editorial.inkGhost }}
              >
                ⌘K
              </kbd>
            </button>
          </div>

          {/* ─── Mobile Hamburger ─── */}
          <button
            className="md:hidden flex flex-col justify-center items-center w-10 h-10 gap-[5px]"
            style={{ background: "none", border: "none" }}
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label={mobileOpen ? "Fermer le menu" : "Ouvrir le menu"}
          >
            <span
              className="block w-5 h-[1.5px] transition-all duration-300"
              style={{
                background: editorial.ink,
                transform: mobileOpen ? "rotate(45deg) translate(2px, 2px)" : "none",
              }}
            />
            <span
              className="block w-5 h-[1.5px] transition-all duration-300"
              style={{
                background: editorial.ink,
                opacity: mobileOpen ? 0 : 1,
              }}
            />
            <span
              className="block w-5 h-[1.5px] transition-all duration-300"
              style={{
                background: editorial.ink,
                transform: mobileOpen ? "rotate(-45deg) translate(2px, -2px)" : "none",
              }}
            />
          </button>
        </div>
      </nav>

      {/* ─── Mobile Drawer ─── */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
            className="fixed inset-0 top-[72px] z-40 md:hidden"
            style={{ background: editorial.bg }}
          >
            <div className="flex flex-col px-6 pt-8 gap-1">
              {navLinks.map((link, i) => (
                <motion.div
                  key={link.href}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05, duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
                >
                  <Link
                    href={link.href}
                    className="block no-underline py-4"
                    style={{
                      fontFamily: editorial.fontDisplay,
                      fontSize: 28,
                      fontWeight: 500,
                      color: isActive(link.href) ? editorial.ink : editorial.inkMuted,
                      borderBottom: `1px solid ${editorial.ruleFaint}`,
                    }}
                  >
                    {link.label}
                  </Link>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
