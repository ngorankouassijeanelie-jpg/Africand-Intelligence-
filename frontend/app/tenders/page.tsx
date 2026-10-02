import Topbar from "@/components/Topbar";
import { apiGet } from "@/lib/api";
import { Tender } from "@/lib/types";

export const dynamic = "force-dynamic";

function fitColor(score: number) {
  if (score >= 85) return "text-gold-400";
  if (score >= 60) return "text-blue-300";
  return "text-slate-400";
}

export default async function TendersPage() {
  const tenders = await apiGet<Tender[]>("/tenders");

  return (
    <>
      <Topbar title="Africand Tender Radar" subtitle="Appels d'offres, consultations et manifestations d'intérêt suivis." />
      <div className="px-6 py-8 md:px-10">
        <div className="card overflow-hidden">
          <table className="table-africand w-full">
            <thead>
              <tr>
                <th>Institution</th>
                <th>Intitulé</th>
                <th>Pays</th>
                <th>Budget</th>
                <th>Deadline</th>
                <th>Fit Africand</th>
                <th>Statut</th>
              </tr>
            </thead>
            <tbody>
              {tenders?.length ? (
                tenders.map((t) => (
                  <tr key={t.id}>
                    <td className="font-medium text-slate-100">{t.institution}</td>
                    <td className="max-w-xs truncate">{t.title}</td>
                    <td>{t.country_code ?? "—"}</td>
                    <td>{t.budget ?? "Non communiqué"}</td>
                    <td>{t.deadline ?? "—"}</td>
                    <td>
                      <span className={`font-serif text-base ${fitColor(t.fit_score)}`}>{t.fit_score}/100</span>
                    </td>
                    <td className="capitalize">{t.status}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="py-10 text-center text-slate-500">
                    Aucun appel d&apos;offres suivi pour le moment.
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
