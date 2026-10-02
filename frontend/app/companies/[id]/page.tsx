import { notFound } from "next/navigation";
import Link from "next/link";
import Topbar from "@/components/Topbar";
import ScoreBadge from "@/components/ScoreBadge";
import { apiGet } from "@/lib/api";
import { CompanyDetail, Opportunity } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function CompanyDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const company = await apiGet<CompanyDetail>(`/companies/${id}`);
  if (!company) notFound();

  const opportunities = await apiGet<Opportunity[]>("/opportunities");
  const companyOpportunities = opportunities?.filter((o) => o.company_id === company.id) ?? [];

  return (
    <>
      <Topbar title={company.name} subtitle={`${company.country_code ?? "Pays non précisé"} · Fiche entreprise`} />
      <div className="space-y-6 px-6 py-8 md:px-10">
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="card p-5 lg:col-span-2">
            <h2 className="mb-3 font-serif text-lg text-white">Informations</h2>
            <dl className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <dt className="text-slate-500">Secteur</dt>
                <dd className="text-slate-100">{company.sector_id ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Site web</dt>
                <dd className="text-slate-100">{company.website ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Chiffre d&apos;affaires</dt>
                <dd className="text-slate-100">{company.revenue ?? "Non disponible"}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Employés</dt>
                <dd className="text-slate-100">{company.employees ?? "Non disponible"}</dd>
              </div>
              <div className="col-span-2">
                <dt className="text-slate-500">Activité</dt>
                <dd className="text-slate-100">{company.description || "Aucune description disponible."}</dd>
              </div>
            </dl>

            <h3 className="mb-2 mt-6 font-serif text-base text-white">Décideurs identifiés</h3>
            {company.contacts.length ? (
              <ul className="space-y-2">
                {company.contacts.map((c) => (
                  <li key={c.id} className="rounded-lg border border-navy-600/50 bg-navy-900/40 px-3 py-2 text-sm">
                    <span className="text-slate-100">{c.name}</span> — <span className="text-slate-400">{c.position}</span>
                    <p className="text-xs text-slate-500">
                      Source : {c.source || "non communiquée"}
                      {c.verification_date ? ` · vérifié le ${c.verification_date}` : ""}
                    </p>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500">
                Aucun décideur identifié publiquement. Conformément à la politique anti-hallucination, aucune
                coordonnée n&apos;est inventée.
              </p>
            )}
          </div>

          <div className="card p-5">
            <h2 className="mb-3 font-serif text-lg text-white">Score commercial</h2>
            <ScoreBadge score={company.commercial_score} />
            <p className="mt-4 text-sm text-slate-400">
              {company.opportunity_count} opportunité(s) détectée(s) pour cette entreprise.
            </p>
          </div>
        </div>

        <div className="card p-5">
          <h2 className="mb-4 font-serif text-lg text-white">Événements récents / Opportunités Africand</h2>
          <div className="space-y-2">
            {companyOpportunities.length ? (
              companyOpportunities.map((o) => (
                <Link
                  key={o.id}
                  href={`/opportunities/${o.id}`}
                  className="flex items-center justify-between gap-4 rounded-lg border border-navy-600/50 bg-navy-900/40 px-4 py-3 hover:bg-navy-700/40"
                >
                  <span className="truncate text-sm text-slate-200">{o.description}</span>
                  <ScoreBadge score={o.opportunity_score} />
                </Link>
              ))
            ) : (
              <p className="text-sm text-slate-500">Aucune opportunité associée pour le moment.</p>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
