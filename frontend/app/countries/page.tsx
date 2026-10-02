import Link from "next/link";
import Topbar from "@/components/Topbar";
import { apiGet } from "@/lib/api";
import { Country } from "@/lib/types";

export const dynamic = "force-dynamic";

const PHASE_LABELS: Record<number, string> = {
  1: "Phase 1 — MVP",
  2: "Phase 2",
  3: "Phase 3",
};

export default async function CountriesPage() {
  const countries = await apiGet<Country[]>("/countries");

  return (
    <>
      <Topbar title="Intelligence pays" subtitle="Afrique de l'Ouest / UEMOA — point de départ Côte d'Ivoire." />
      <div className="px-6 py-8 md:px-10">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {countries?.map((c) => (
            <Link key={c.code} href={`/countries/${c.code}`} className="card p-4 hover:bg-navy-700/40">
              <div className="flex items-center justify-between">
                <p className="font-serif text-lg text-white">{c.name}</p>
                {!c.active && (
                  <span className="rounded-full border border-slate-600 px-2 py-0.5 text-[10px] text-slate-400">
                    Inactif
                  </span>
                )}
              </div>
              <p className="mt-1 text-xs text-gold-400">{PHASE_LABELS[c.phase] ?? `Phase ${c.phase}`}</p>
            </Link>
          ))}
        </div>
      </div>
    </>
  );
}
