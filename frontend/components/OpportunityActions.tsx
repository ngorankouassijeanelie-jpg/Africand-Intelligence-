"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { clientApi } from "@/lib/clientApi";

const STATUSES = [
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

export default function OpportunityActions({
  opportunityId,
  currentStatus,
  hasCrmDeal,
}: {
  opportunityId: number;
  currentStatus: string;
  hasCrmDeal: boolean;
}) {
  const router = useRouter();
  const [status, setStatus] = useState(currentStatus);
  const [loading, setLoading] = useState(false);

  async function handleStatusChange(newStatus: string) {
    setStatus(newStatus);
    setLoading(true);
    await clientApi.patch(`/opportunities/${opportunityId}/status`, { status: newStatus });
    setLoading(false);
    router.refresh();
  }

  async function handleCreateDeal() {
    setLoading(true);
    await clientApi.post("/crm/deals", { opportunity_id: opportunityId, stage: status });
    setLoading(false);
    router.push("/crm");
  }

  return (
    <div className="flex flex-wrap items-center gap-3">
      <label className="text-xs text-slate-400">
        Statut pipeline
        <select
          value={status}
          disabled={loading}
          onChange={(e) => handleStatusChange(e.target.value)}
          className="ml-2 rounded-md border border-navy-600 bg-navy-900 px-2 py-1 text-sm text-slate-100"
        >
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </label>
      {!hasCrmDeal && (
        <button
          onClick={handleCreateDeal}
          disabled={loading}
          className="rounded-md bg-gold-500 px-3 py-1.5 text-sm font-medium text-navy-950 hover:bg-gold-400 disabled:opacity-50"
        >
          Transformer en prospect CRM
        </button>
      )}
    </div>
  );
}
