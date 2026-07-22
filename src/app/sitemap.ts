import { MetadataRoute } from 'next';
import fs from 'fs';
import path from 'path';

const SITE_URL = 'https://terre-etendue-islam.fr';

export default function sitemap(): MetadataRoute.Sitemap {
  const articlesDir = path.join(process.cwd(), 'content/articles');
  const files = fs.readdirSync(articlesDir).filter(f => f.endsWith('.json'));

  // Pages statiques
  const staticPages: MetadataRoute.Sitemap = [
    { url: SITE_URL, lastModified: new Date(), changeFrequency: 'weekly', priority: 1 },
    { url: `${SITE_URL}/headquarters`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
    { url: `${SITE_URL}/observatory`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
    { url: `${SITE_URL}/library`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
    { url: `${SITE_URL}/experiences`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.9 },
    { url: `${SITE_URL}/laboratoire`, lastModified: new Date(), changeFrequency: 'weekly', priority: 0.8 },
    { url: `${SITE_URL}/enseignants`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
    { url: `${SITE_URL}/lab`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
    { url: `${SITE_URL}/nexus`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.7 },
    { url: `${SITE_URL}/about`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.5 },
  ];

  // Pages articles dynamiques
  const articlePages: MetadataRoute.Sitemap = files.map(file => {
    const slug = file.replace('.json', '');
    const filePath = path.join(articlesDir, file);
    const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
    const date = data.date ? new Date(data.date) : new Date();
    const pinned = data.pinned === true;

    return {
      url: `${SITE_URL}/article/${slug}`,
      lastModified: date,
      changeFrequency: 'monthly' as const,
      priority: pinned ? 0.9 : 0.7,
    };
  });

  return [...staticPages, ...articlePages];
}
