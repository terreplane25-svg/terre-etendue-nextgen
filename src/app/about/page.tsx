import AboutClient from './AboutClient';

export const metadata = {
  alternates: { canonical: '/about' },
  title: 'À propos',
  description: 'Manifeste, méthodologie et éthique intellectuelle de la plateforme Terre Étendue Islam.',
};

export default function AboutPage() {
  return <AboutClient />;
}
