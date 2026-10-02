import Link from "next/link";
import { notFound } from "next/navigation";
import Topbar from "@/components/Topbar";
import ScoreBadge from "@/components/ScoreBadge";
import OpportunityActions from "@/components/OpportunityActions";
import { apiGet } from "@/lib/api";
import { CrmDeal, Opportunity } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function OpportunityDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const opportunity = await apiGet<Opportunity>(`/opportunities/${id}`);
  if (!opportunity) notFound();

  const deals = await apiGet<CrmDeal[]>("/crm/deals");
  const hasCrmDeal = Boolean(deals?.some((d) => d.opportunity_id === opportunity.id));

  const subScores = (opportunity.score_breakdown?.sub_scores ?? {}) as Record<string, number>;

  return (
    <>
      <Topbar title="Fiche opportunité" subtitle={opportunity.description} />
      <div className="space-y-6 px-6 py-8 md:px-10">
        <div className="card flex flex-wrap items-center justify-between gap-4 p-5">
          <div className="flex items-center gap-4">
            <ScoreBadge score={opportunity.opportunity_score} />
            <span className="text-xs text-slate-400">
              Confiance de l&apos;extraction : {Math.round(opportunity.confidence * 100)}%
            </span>
          </div>
          <OpportunityActions opportunityId={opportunity.id} currentStatus={opportunity.status} hasCrmDeal={hasCrmDeal} />
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="card p-5 lg:col-span-2">
            <h2 className="mb-4 font-serif text-lg text-white">Détails</h2>
            <dl className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <dt className="text-slate-500">Entreprise</dt>
                <dd className="text-slate-100">
                  {opportunity.company_id ? (
                    <Link href={`/companies/${opportunity.company_id}`} className="text-gold-400 hover:underline">
                      {opportunity.company_name}
                    </Link>
                  ) : (
                    "Non identifiée"
                  )}
                </dd>
              </div>
              <div>
                <dt className="text-slate-500">Pays</dt>
                <dd className="text-slate-100">{opportunity.country_name ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Secteur</dt>
                <dd className="text-slate-100">{opportunity.sector_name ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Trigger</dt>
                <dd className="text-slate-100">{opportunity.trigger_name ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Montant annoncé</dt>
                <dd className="text-slate-100">
                  {opportunity.amount
                    ? `${new Intl.NumberFormat("fr-FR").format(opportunity.amount)} ${opportunity.currency ?? ""}`
                    : "Non communiqué"}
                </dd>
              </div>
              <div>
                <dt className="text-slate-500">Urgence</dt>
                <dd className="text-slate-100 capitalize">{opportunity.urgency}</dd>
              </div>
              <div className="col-span-2">
                <dt className="text-slate-500">Service(s) Africand suggéré(s)</dt>
                <dd className="mt-1 flex flex-wrap gap-1">
                  {opportunity.suggested_service.map((s) => (
                    <span key={s} className="rounded bg-navy-700/60 px-2 py-0.5 text-xs text-slate-300">
                      {s}
                    </span>
                  ))}
                </dd>
              </div>
              <div className="col-span-2">
                <dt className="text-slate-500">Source</dt>
                <dd className="truncate text-slate-100">
                  <a href={opportunity.source_url} target="_blank" rel="noreferrer" className="text-gold-400 hover:underline">
                    {opportunity.source_url || "Non communiquée"}
                  </a>
                </dd>
                {opportunity.related_sources.length > 0 && (
                  <p className="mt-1 text-xs text-slate-500">
                    + {opportunity.related_sources.length} source(s) additionnelle(s) (même événement)
                  </p>
                )}
              </div>
            </dl>
          </div>

          <div className="card p-5">
            <h2 className="mb-4 font-serif text-lg text-white">Détail du score</h2>
            <div className="space-y-2">
              {Object.entries(subScores).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between text-sm">
                  <span className="capitalize text-slate-400">{key.replace(/_/g, " ")}</span>
                  <span className="text-slate-100">{value}/100</span>
                </div>
              ))}
            </div>
            <p className="mt-4 text-xs text-slate-500">
              Pondérations configurables depuis Administration → Pondérations.
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
