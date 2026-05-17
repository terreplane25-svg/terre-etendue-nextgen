import { getArticle } from '@/lib/articles';
import AboutClient from './AboutClient';

export const metadata = {
  title: 'À propos',
  description: 'Manifeste, méthodologie et éthique intellectuelle de la plateforme.',
};

export default async function AboutPage() {
  const manifeste = await getArticle('manifeste');
  const methodo = await getArticle('methodologie');
  const ethique = await getArticle('ethique-intellectuelle');
  const etatDesLieux = await getArticle('etat-des-lieux-ou-en-sommes-nous');

  return (
    <AboutClient
      manifeste={manifeste?.htmlContent || ''}
      methodologie={methodo?.htmlContent || ''}
      ethique={ethique?.htmlContent || ''}
      etatDesLieux={etatDesLieux?.htmlContent || ''}
    />
  );
}
