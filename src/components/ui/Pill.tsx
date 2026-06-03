interface Props {
  children: React.ReactNode;
  color?: string;
}

export default function Pill({ children, color = '#7C6FC4' }: Props) {
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center',
      fontSize: 10, fontWeight: 600, letterSpacing: '0.14em',
      textTransform: 'uppercase' as const,
      fontFamily: "'JetBrains Mono', monospace",
      padding: '4px 12px', borderRadius: 99,
      background: color + '0F', color,
    }}>{children}</span>
  );
}
