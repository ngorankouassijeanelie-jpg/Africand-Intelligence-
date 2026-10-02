import Topbar from "@/components/Topbar";
import CrmDealCard from "@/components/CrmDealCard";
import { apiGet } from "@/lib/api";
import { CrmDeal, Opportunity } from "@/lib/types";

export const dynamic = "force-dynamic";

const STAGES = [
  { key: "detected", label: "Détecté" },
  { key: "qualified", label: "Qualifié" },
  { key: "target", label: "Cible" },
  { key: "contacted", label: "Contacté" },
  { key: "meeting", label: "Rendez-vous" },
  { key: "proposal", label: "Proposition" },
  { key: "negotiation", label: "Négociation" },
  { key: "won", label: "Gagné" },
  { key: "client", label: "Client" },
  { key: "lost", label: "Perdu" },
];

export default async function CrmPage() {
  const [deals, opportunities] = await Promise.all([
    apiGet<CrmDeal[]>("/crm/deals"),
    apiGet<Opportunity[]>("/opportunities"),
  ]);

  const opportunityById = new Map((opportunities ?? []).map((o) => [o.id, o]));

  return (
    <>
      <Topbar title="CRM Africand" subtitle="Pipeline commercial — de la détection au client." />
      <div className="overflow-x-auto px-6 py-8 md:px-10">
        <div className="flex min-w-max gap-4">
          {STAGES.map((stage) => {
            const stageDeals = (deals ?? []).filter((d) => d.stage === stage.key);
            return (
              <div key={stage.key} className="w-64 shrink-0">
                <div className="mb-2 flex items-center justify-between px-1">
                  <h3 className="text-sm font-medium text-slate-300">{stage.label}</h3>
                  <span className="text-xs text-slate-500">{stageDeals.length}</span>
                </div>
                <div className="space-y-2">
                  {stageDeals.map((deal) => (
                    <CrmDealCard
                      key={deal.id}
                      deal={deal}
                      description={opportunityById.get(deal.opportunity_id)?.description ?? "Opportunité"}
                    />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </>
  );
}
