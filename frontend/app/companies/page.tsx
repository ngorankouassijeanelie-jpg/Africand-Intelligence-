import Link from "next/link";
import Topbar from "@/components/Topbar";
import { apiGet } from "@/lib/api";
import { Company } from "@/lib/types";

export const dynamic = "force-dynamic";

export default async function CompaniesPage({
  searchParams,
}: {
  searchParams: Promise<{ search?: string; country_code?: string }>;
}) {
  const params = await searchParams;
  const companies = await apiGet<Company[]>("/companies", {
    search: params.search,
    country_code: params.country_code,
  });

  return (
    <>
      <Topbar title="Entreprises" subtitle="Base propriétaire de connaissance sur les entreprises suivies." />
      <div className="px-6 py-8 md:px-10">
        <form className="mb-5 flex gap-3">
          <input
            type="text"
            name="search"
            defaultValue={params.search}
            placeholder="Rechercher une entreprise..."
            className="w-full max-w-sm rounded-md border border-navy-600 bg-navy-900 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500"
          />
          <button className="rounded-md bg-navy-700 px-4 py-2 text-sm text-slate-100 hover:bg-navy-600">
            Rechercher
          </button>
        </form>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {companies?.length ? (
            companies.map((c) => (
              <Link key={c.id} href={`/companies/${c.id}`} className="card p-4 hover:bg-navy-700/40">
                <p className="font-serif text-lg text-white">{c.name}</p>
                <p className="mt-1 text-xs text-slate-500">{c.country_code ?? "Pays non précisé"}</p>
                <p className="mt-2 line-clamp-2 text-sm text-slate-400">{c.description || "Aucune description."}</p>
              </Link>
            ))
          ) : (
            <p className="text-sm text-slate-500">Aucune entreprise trouvée.</p>
          )}
        </div>
      </div>
    </>
  );
}
