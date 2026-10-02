import Link from "next/link";
import { notFound } from "next/navigation";
import Topbar from "@/components/Topbar";
import ScoreBadge from "@/components/ScoreBadge";
import { apiGet } from "@/lib/api";
import { Country } from "@/lib/types";

export const dynamic = "force-dynamic";

interface CountryDetail {
  country: Country;
  opportunities_count: number;
  top_opportunities: { id: number; description: string; score: number; status: string }[];
  companies: { id: number; name: string; sector_id: number | null }[];
  tenders: { id: number; title: string; fit_score: number; deadline: string | null }[];
  active_investors: { id: number; name: string; type: string }[];
}

export default async function CountryDetailPage({ params }: { params: Promise<{ code: string }> }) {
  const { code } = await params;
  const detail = await apiGet<CountryDetail>(`/countries/${code}`);
  if (!detail) notFound();

  return (
    <>
      <Topbar title={detail.country.name} subtitle="Opportunités, investissements, appels d'offres et entreprises actives." />
      <div className="space-y-6 px-6 py-8 md:px-10">
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="card p-5">
            <h2 className="mb-4 font-serif text-lg text-white">Top opportunités ({detail.opportunities_count})</h2>
            <div className="space-y-2">
              {detail.top_opportunities.length ? (
                detail.top_opportunities.map((o) => (
                  <Link
                    key={o.id}
                    href={`/opportunities/${o.id}`}
                    className="flex items-center justify-between gap-3 rounded-lg border border-navy-600/50 bg-navy-900/40 px-3 py-2.5 hover:bg-navy-700/40"
                  >
                    <span className="truncate text-sm text-slate-200">{o.description}</span>
                    <ScoreBadge score={o.score} />
                  </Link>
                ))
              ) : (
                <p className="text-sm text-slate-500">Aucune opportunité détectée pour ce pays.</p>
              )}
            </div>
          </div>

          <div className="card p-5">
            <h2 className="mb-4 font-serif text-lg text-white">Appels d&apos;offres</h2>
            <div className="space-y-2">
              {detail.tenders.length ? (
                detail.tenders.map((t) => (
                  <div key={t.id} className="rounded-lg border border-navy-600/50 bg-navy-900/40 px-3 py-2.5 text-sm">
                    <p className="text-slate-100">{t.title}</p>
                    <p className="text-xs text-slate-500">
                      Fit score {t.fit_score}/100 · Deadline {t.deadline ?? "non précisée"}
                    </p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-500">Aucun appel d&apos;offres suivi pour ce pays.</p>
              )}
            </div>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <div className="card p-5">
            <h2 className="mb-4 font-serif text-lg text-white">Entreprises en croissance</h2>
            <div className="flex flex-wrap gap-2">
              {detail.companies.length ? (
                detail.companies.map((c) => (
                  <Link
                    key={c.id}
                    href={`/companies/${c.id}`}
                    className="rounded-full border border-navy-600 px-3 py-1 text-xs text-slate-300 hover:border-gold-500 hover:text-gold-400"
                  >
                    {c.name}
                  </Link>
                ))
              ) : (
                <p className="text-sm text-slate-500">Aucune entreprise suivie pour ce pays.</p>
              )}
            </div>
          </div>

          <div className="card p-5">
            <h2 className="mb-4 font-serif text-lg text-white">Investisseurs actifs</h2>
            <div className="space-y-2">
              {detail.active_investors.length ? (
                detail.active_investors.map((i) => (
                  <div key={i.id} className="rounded-lg border border-navy-600/50 bg-navy-900/40 px-3 py-2.5 text-sm">
                    <span className="text-slate-100">{i.name}</span> <span className="text-slate-500">· {i.type}</span>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-500">Aucun investisseur actif identifié pour ce pays.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
