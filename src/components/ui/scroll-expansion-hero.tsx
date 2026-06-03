'use client';

import {
  useEffect,
  useRef,
  useState,
  ReactNode,
} from 'react';
import Image from 'next/image';
import { motion } from 'framer-motion';

interface ScrollExpandMediaProps {
  mediaType?: 'video' | 'image';
  mediaSrc: string;
  posterSrc?: string;
  bgImageSrc: string;
  title?: string;
  date?: string;
  scrollToExpand?: string;
  textBlend?: boolean;
  children?: ReactNode;
}

const ScrollExpandMedia = ({
  mediaType = 'image',
  mediaSrc,
  posterSrc,
  bgImageSrc,
  title,
  date,
  scrollToExpand,
  textBlend,
  children,
}: ScrollExpandMediaProps) => {
  const [scrollProgress, setScrollProgress] = useState<number>(0);
  const [showContent, setShowContent] = useState<boolean>(false);
  const [mediaFullyExpanded, setMediaFullyExpanded] = useState<boolean>(false);
  const [touchStartY, setTouchStartY] = useState<number>(0);
  const [isMobileState, setIsMobileState] = useState<boolean>(false);

  const sectionRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    setScrollProgress(0);
    setShowContent(false);
    setMediaFullyExpanded(false);
  }, [mediaType]);

  useEffect(() => {
    const handleWheel = (e: globalThis.WheelEvent) => {
      if (mediaFullyExpanded && e.deltaY < 0 && window.scrollY <= 5) {
        setMediaFullyExpanded(false);
        e.preventDefault();
      } else if (!mediaFullyExpanded) {
        e.preventDefault();
        const scrollDelta = e.deltaY * 0.0009;
        const newProgress = Math.min(Math.max(scrollProgress + scrollDelta, 0), 1);
        setScrollProgress(newProgress);
        if (newProgress >= 1) { setMediaFullyExpanded(true); setShowContent(true); }
        else if (newProgress < 0.75) { setShowContent(false); }
      }
    };

    const handleTouchStart = (e: globalThis.TouchEvent) => { setTouchStartY(e.touches[0].clientY); };
    const handleTouchMove = (e: globalThis.TouchEvent) => {
      if (!touchStartY) return;
      const touchY = e.touches[0].clientY;
      const deltaY = touchStartY - touchY;
      if (mediaFullyExpanded && deltaY < -20 && window.scrollY <= 5) { setMediaFullyExpanded(false); e.preventDefault(); }
      else if (!mediaFullyExpanded) {
        e.preventDefault();
        const scrollFactor = deltaY < 0 ? 0.008 : 0.005;
        const scrollDelta = deltaY * scrollFactor;
        const newProgress = Math.min(Math.max(scrollProgress + scrollDelta, 0), 1);
        setScrollProgress(newProgress);
        if (newProgress >= 1) { setMediaFullyExpanded(true); setShowContent(true); }
        else if (newProgress < 0.75) { setShowContent(false); }
        setTouchStartY(touchY);
      }
    };
    const handleTouchEnd = () => { setTouchStartY(0); };
    const handleScroll = () => { if (!mediaFullyExpanded) window.scrollTo(0, 0); };

    window.addEventListener('wheel', handleWheel, { passive: false });
    window.addEventListener('scroll', handleScroll);
    window.addEventListener('touchstart', handleTouchStart, { passive: false });
    window.addEventListener('touchmove', handleTouchMove, { passive: false });
    window.addEventListener('touchend', handleTouchEnd);
    return () => {
      window.removeEventListener('wheel', handleWheel);
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('touchstart', handleTouchStart);
      window.removeEventListener('touchmove', handleTouchMove);
      window.removeEventListener('touchend', handleTouchEnd);
    };
  }, [scrollProgress, mediaFullyExpanded, touchStartY]);

  useEffect(() => {
    const check = () => setIsMobileState(window.innerWidth < 768);
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  const mediaWidth = 300 + scrollProgress * (isMobileState ? 650 : 1250);
  const mediaHeight = 400 + scrollProgress * (isMobileState ? 200 : 400);
  const textTranslateX = scrollProgress * (isMobileState ? 180 : 150);
  const firstWord = title ? title.split(' ')[0] : '';
  const restOfTitle = title ? title.split(' ').slice(1).join(' ') : '';

  return (
    <div ref={sectionRef} className="transition-colors duration-700 ease-in-out overflow-x-hidden">
      <section className="relative flex flex-col items-center justify-start min-h-[100dvh]">
        <div className="relative w-full flex flex-col items-center min-h-[100dvh]">
          <motion.div className="absolute inset-0 z-0 h-full" initial={{ opacity: 0 }} animate={{ opacity: 1 - scrollProgress }} transition={{ duration: 0.1 }}>
            <Image src={bgImageSrc} alt="Background" width={1920} height={1080} className="w-screen h-screen" style={{ objectFit: 'cover', objectPosition: 'center' }} priority />
            <div className="absolute inset-0 bg-black/10" />
          </motion.div>

          <div className="container mx-auto flex flex-col items-center justify-start relative z-10">
            <div className="flex flex-col items-center justify-center w-full h-[100dvh] relative">
              <div className="absolute z-0 top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 transition-none rounded-2xl"
                style={{ width: `${mediaWidth}px`, height: `${mediaHeight}px`, maxWidth: '95vw', maxHeight: '85vh', boxShadow: '0px 0px 50px rgba(0,0,0,0.3)' }}>
                {mediaType === 'image' ? (
                  <div className="relative w-full h-full">
                    <Image src={mediaSrc} alt={title || ''} width={1280} height={720} className="w-full h-full object-cover rounded-xl" />
                    <motion.div className="absolute inset-0 bg-black/50 rounded-xl" initial={{ opacity: 0.7 }} animate={{ opacity: 0.7 - scrollProgress * 0.3 }} transition={{ duration: 0.2 }} />
                  </div>
                ) : (
                  <div className="relative w-full h-full pointer-events-none">
                    <video src={mediaSrc} poster={posterSrc} autoPlay muted loop playsInline preload="auto" className="w-full h-full object-cover rounded-xl" controls={false} />
                    <motion.div className="absolute inset-0 bg-black/30 rounded-xl" initial={{ opacity: 0.7 }} animate={{ opacity: 0.5 - scrollProgress * 0.3 }} transition={{ duration: 0.2 }} />
                  </div>
                )}
                <div className="flex flex-col items-center text-center relative z-10 mt-4 transition-none">
                  {date && <p className="text-2xl" style={{ transform: `translateX(-${textTranslateX}vw)`, color: '#BAB5AC' }}>{date}</p>}
                  {scrollToExpand && <p className="font-medium text-center" style={{ transform: `translateX(${textTranslateX}vw)`, color: '#BAB5AC' }}>{scrollToExpand}</p>}
                </div>
              </div>

              <div className={`flex items-center justify-center text-center gap-4 w-full relative z-10 transition-none flex-col ${textBlend ? 'mix-blend-difference' : 'mix-blend-normal'}`}>
                <motion.h2 className="text-4xl md:text-5xl lg:text-7xl font-bold transition-none" style={{ transform: `translateX(-${textTranslateX}vw)`, color: '#F5F3EE', letterSpacing: '-0.03em' }}>{firstWord}</motion.h2>
                <motion.h2 className="text-4xl md:text-5xl lg:text-7xl font-bold text-center transition-none" style={{ transform: `translateX(${textTranslateX}vw)`, color: '#F5F3EE', letterSpacing: '-0.03em' }}>{restOfTitle}</motion.h2>
              </div>
            </div>

            <motion.section className="flex flex-col w-full px-8 py-10 md:px-16 lg:py-20" initial={{ opacity: 0 }} animate={{ opacity: showContent ? 1 : 0 }} transition={{ duration: 0.7 }}>
              {children}
            </motion.section>
          </div>
        </div>
      </section>
    </div>
  );
};

export default ScrollExpandMedia;
