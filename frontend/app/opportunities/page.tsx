import Link from "next/link";
import Topbar from "@/components/Topbar";
import ScoreBadge from "@/components/ScoreBadge";
import StatusBadge from "@/components/StatusBadge";
import { apiGet } from "@/lib/api";
import { Opportunity } from "@/lib/types";

export const dynamic = "force-dynamic";

function formatAmount(amount: number | null, currency: string | null) {
  if (!amount) return "—";
  return new Intl.NumberFormat("fr-FR").format(amount) + (currency ? ` ${currency}` : "");
}

export default async function OpportunitiesPage({
  searchParams,
}: {
  searchParams: Promise<{ country_code?: string; status?: string; min_score?: string }>;
}) {
  const params = await searchParams;
  const opportunities = await apiGet<Opportunity[]>("/opportunities", {
    country_code: params.country_code,
    status: params.status,
    min_score: params.min_score,
  });

  return (
    <>
      <Topbar title="Opportunités" subtitle="Événements détectés, qualifiés et classés par score commercial." />
      <div className="px-6 py-8 md:px-10">
        <div className="card overflow-hidden">
          <table className="table-africand w-full">
            <thead>
              <tr>
                <th>Entreprise</th>
                <th>Pays</th>
                <th>Secteur</th>
                <th>Trigger</th>
                <th>Montant</th>
                <th>Service Africand</th>
                <th>Score</th>
                <th>Statut</th>
              </tr>
            </thead>
            <tbody>
              {opportunities?.length ? (
                opportunities.map((o) => (
                  <tr key={o.id}>
                    <td>
                      <Link href={`/opportunities/${o.id}`} className="font-medium text-slate-100 hover:text-gold-400">
                        {o.company_name ?? "Entreprise non identifiée"}
                      </Link>
                      <p className="mt-0.5 max-w-sm truncate text-xs text-slate-500">{o.description}</p>
                    </td>
                    <td>{o.country_name ?? "—"}</td>
                    <td>{o.sector_name ?? "—"}</td>
                    <td>{o.trigger_name ?? "—"}</td>
                    <td>{formatAmount(o.amount, o.currency)}</td>
                    <td>
                      <div className="flex flex-wrap gap-1">
                        {o.suggested_service.map((s) => (
                          <span key={s} className="rounded bg-navy-700/60 px-1.5 py-0.5 text-[11px] text-slate-300">
                            {s}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td>
                      <ScoreBadge score={o.opportunity_score} />
                    </td>
                    <td>
                      <StatusBadge status={o.status} />
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="py-10 text-center text-slate-500">
                    Aucune opportunité trouvée. Lancez une collecte depuis l&apos;administration.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
