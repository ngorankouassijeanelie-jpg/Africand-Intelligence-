const STATUS_LABELS: Record<string, string> = {
  detected: "Détecté",
  qualified: "Qualifié",
  target: "Cible",
  contacted: "Contacté",
  meeting: "Rendez-vous",
  proposal: "Proposition",
  negotiation: "Négociation",
  won: "Gagné",
  client: "Client",
  lost: "Perdu",
  open: "Ouvert",
  closed: "Clôturé",
};

export default function StatusBadge({ status }: { status: string }) {
  const lost = status === "lost";
  const won = status === "won" || status === "client";
  return (
    <span
      className={`inline-block rounded-full border px-2.5 py-1 text-xs font-medium ${
        lost
          ? "border-red-500/30 bg-red-500/10 text-red-400"
          : won
          ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
          : "border-navy-600 bg-navy-700/50 text-slate-300"
      }`}
    >
      {STATUS_LABELS[status] ?? status}
    </span>
  );
}
