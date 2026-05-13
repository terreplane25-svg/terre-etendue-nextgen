import { getArticle } from '@/lib/articles';
import AboutClient from './AboutClient';

export const metadata = {
  title: 'À propos — Terre Étendue Islam',
  description: 'Manifeste, méthodologie et éthique intellectuelle de la plateforme.',
};

export default async function AboutPage() {
  const manifeste = await getArticle('manifeste');
  const methodo = await getArticle('methodologie');
  const ethique = await getArticle('ethique-intellectuelle');

  return (
    <AboutClient
      manifeste={manifeste?.htmlContent || ''}
      methodologie={methodo?.htmlContent || ''}
      ethique={ethique?.htmlContent || ''}
    />
  );
}
