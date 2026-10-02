"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { clientApi } from "@/lib/clientApi";
import { CrmDeal } from "@/lib/types";

const STAGES = [
  "detected",
  "qualified",
  "target",
  "contacted",
  "meeting",
  "proposal",
  "negotiation",
  "won",
  "client",
  "lost",
];

const LOST_REASONS = [
  { value: "budget", label: "Budget" },
  { value: "timing", label: "Timing" },
  { value: "concurrent", label: "Concurrent" },
  { value: "aucun_besoin", label: "Aucun besoin" },
  { value: "pas_de_reponse", label: "Pas de réponse" },
  { value: "autre", label: "Autre raison" },
];

export default function CrmDealCard({ deal, description }: { deal: CrmDeal; description: string }) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  async function updateStage(stage: string) {
    setLoading(true);
    await clientApi.patch(`/crm/deals/${deal.id}`, { stage });
    setLoading(false);
    router.refresh();
  }

  async function setLostReason(lost_reason: string) {
    setLoading(true);
    await clientApi.patch(`/crm/deals/${deal.id}`, { lost_reason });
    setLoading(false);
    router.refresh();
  }

  return (
    <div className="rounded-lg border border-navy-600/50 bg-navy-900/50 p-3 text-sm">
      <p className="truncate text-slate-100">{description}</p>
      <p className="mt-1 text-xs text-slate-500">
        {deal.estimated_value ? `${new Intl.NumberFormat("fr-FR").format(deal.estimated_value)} FCFA` : "Valeur non estimée"}
        {" · "}
        {deal.probability}% proba.
      </p>
      <div className="mt-2 flex items-center gap-2">
        <select
          value={deal.stage}
          disabled={loading}
          onChange={(e) => updateStage(e.target.value)}
          className="rounded border border-navy-600 bg-navy-900 px-1.5 py-1 text-xs text-slate-200"
        >
          {STAGES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>
      {deal.stage === "lost" && (
        <select
          value={deal.lost_reason ?? ""}
          disabled={loading}
          onChange={(e) => setLostReason(e.target.value)}
          className="mt-2 w-full rounded border border-red-500/30 bg-navy-900 px-1.5 py-1 text-xs text-red-300"
        >
          <option value="">Raison de la perte...</option>
          {LOST_REASONS.map((r) => (
            <option key={r.value} value={r.value}>
              {r.label}
            </option>
          ))}
        </select>
      )}
    </div>
  );
}
