function bucketFor(score: number): { label: string; classes: string } {
  if (score >= 90) return { label: "Priorité immédiate", classes: "bg-red-500/15 text-red-400 border-red-500/30" };
  if (score >= 75) return { label: "High priority", classes: "bg-gold-500/15 text-gold-400 border-gold-500/30" };
  if (score >= 50) return { label: "Nurture", classes: "bg-blue-500/15 text-blue-300 border-blue-500/30" };
  return { label: "Monitor", classes: "bg-slate-500/15 text-slate-400 border-slate-500/30" };
}

export default function ScoreBadge({ score }: { score: number }) {
  const { label, classes } = bucketFor(score);
  return (
    <span className={`inline-flex items-center gap-2 rounded-full border px-2.5 py-1 text-xs font-medium ${classes}`}>
      <span className="font-serif text-sm">{score}</span>
      <span>/100 · {label}</span>
    </span>
  );
}
