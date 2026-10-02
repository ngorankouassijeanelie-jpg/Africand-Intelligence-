import Link from "next/link";
import Topbar from "@/components/Topbar";
import { apiGet } from "@/lib/api";
import { Alert } from "@/lib/types";

export const dynamic = "force-dynamic";

const TYPE_LABELS: Record<string, string> = {
  priority: "🔴 Opportunité prioritaire",
  high: "🟠 High priority",
  tender: "📄 Appel d'offres",
};

export default async function AlertsPage() {
  const alerts = await apiGet<Alert[]>("/alerts");

  return (
    <>
      <Topbar title="Africand Alerts" subtitle="Notifications automatiques sur les opportunités critiques." />
      <div className="px-6 py-8 md:px-10">
        <div className="space-y-3">
          {alerts?.length ? (
            alerts.map((a) => (
              <Link
                key={a.id}
                href={`/opportunities/${a.opportunity_id}`}
                className="card flex flex-col gap-1 p-4 hover:bg-navy-700/40"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gold-400">{TYPE_LABELS[a.type] ?? a.type}</span>
                  <span className="text-xs text-slate-500">{new Date(a.sent_at).toLocaleString("fr-FR")}</span>
                </div>
                <p className="text-sm text-slate-200">{a.message}</p>
                <p className="text-xs text-slate-500">Canal : {a.channel} · Destinataire : {a.recipient}</p>
              </Link>
            ))
          ) : (
            <p className="text-sm text-slate-500">Aucune alerte pour le moment.</p>
          )}
        </div>
      </div>
    </>
  );
}
