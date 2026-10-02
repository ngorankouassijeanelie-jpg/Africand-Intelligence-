import Link from "next/link";
import Topbar from "@/components/Topbar";
import KpiCard from "@/components/KpiCard";
import ScoreBadge from "@/components/ScoreBadge";
import { apiGet } from "@/lib/api";
import { Alert, KpiData } from "@/lib/types";

export const dynamic = "force-dynamic";

interface TopOpportunity {
  id: number;
  description: string;
  score: number;
  urgency: string;
  status: string;
  country_code: string | null;
  detected_at: string;
}

function formatXof(value: number) {
  return new Intl.NumberFormat("fr-FR").format(value) + " FCFA";
}

export default async function DashboardPage() {
  const [kpi, topOpportunities, alerts] = await Promise.all([
    apiGet<KpiData>("/dashboard/kpi"),
    apiGet<TopOpportunity[]>("/dashboard/top-opportunities", { limit: 8 }),
    apiGet<Alert[]>("/alerts"),
  ]);

  return (
    <>
      <Topbar
        title="Tableau de bord"
        subtitle="Qu'est-ce qui vient de se passer en Afrique de l'Ouest et qui pourrait créer une mission pour Africand ?"
      />
      <div className="space-y-8 px-6 py-8 md:px-10">
        {!kpi ? (
          <p className="text-sm text-amber-400">
            API indisponible. Démarrez le backend (voir README) pour afficher les données en direct.
          </p>
        ) : (
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            <KpiCard label="Nouvelles opportunités" value={kpi.nouvelles_opportunites} />
            <KpiCard label="Opportunités prioritaires" value={kpi.opportunites_prioritaires} />
            <KpiCard label="Appels d'offres actifs" value={kpi.appels_offres_actifs} />
            <KpiCard label="Entreprises surveillées" value={kpi.entreprises_surveillees} />
            <KpiCard label="Investisseurs actifs" value={kpi.investisseurs_actifs} />
            <KpiCard label="Partenariats potentiels" value={kpi.partenariats_potentiels} />
            <KpiCard label="Opportunités cette semaine" value={kpi.opportunites_cette_semaine} />
            <KpiCard label="Valeur commerciale potentielle" value={formatXof(kpi.valeur_commerciale_potentielle)} />
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="card p-5 lg:col-span-2">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-serif text-lg text-white">Top opportunités</h2>
              <Link href="/opportunities" className="text-xs text-gold-400 hover:underline">
                Voir toutes les opportunités →
              </Link>
            </div>
            <div className="space-y-3">
              {topOpportunities?.length ? (
                topOpportunities.map((o) => (
                  <Link
                    key={o.id}
                    href={`/opportunities/${o.id}`}
                    className="flex items-center justify-between gap-4 rounded-lg border border-navy-600/50 bg-navy-900/40 px-4 py-3 hover:bg-navy-700/40"
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm text-slate-100">{o.description}</p>
                      <p className="text-xs text-slate-500">
                        {o.country_code ?? "—"} · détecté le {new Date(o.detected_at).toLocaleDateString("fr-FR")}
                      </p>
                    </div>
                    <ScoreBadge score={o.score} />
                  </Link>
                ))
              ) : (
                <p className="text-sm text-slate-500">Aucune opportunité pour le moment.</p>
              )}
            </div>
          </div>

          <div className="card p-5">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-serif text-lg text-white">Alertes récentes</h2>
              <Link href="/alerts" className="text-xs text-gold-400 hover:underline">
                Tout voir →
              </Link>
            </div>
            <div className="space-y-3">
              {alerts?.length ? (
                alerts.slice(0, 6).map((a) => (
                  <div key={a.id} className="rounded-lg border border-navy-600/50 bg-navy-900/40 px-3 py-2.5">
                    <p className="text-xs uppercase tracking-wide text-gold-400">{a.type}</p>
                    <p className="mt-1 text-sm text-slate-200">{a.message}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-500">Aucune alerte pour le moment.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
