"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Tableau de bord" },
  { href: "/opportunities", label: "Opportunités" },
  { href: "/companies", label: "Entreprises" },
  { href: "/countries", label: "Pays" },
  { href: "/tenders", label: "Tender Radar" },
  { href: "/crm", label: "CRM" },
  { href: "/alerts", label: "Alertes" },
  { href: "/admin", label: "Administration" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden md:flex md:w-64 md:flex-col border-r border-navy-600/60 bg-navy-900/80 px-4 py-6">
      <div className="mb-8 px-2">
        <p className="font-serif text-lg tracking-wide text-gold-400">AFRICAND</p>
        <p className="text-xs uppercase tracking-[0.2em] text-slate-400">Intelligence</p>
      </div>
      <nav className="flex flex-1 flex-col gap-1">
        {NAV_ITEMS.map((item) => {
          const active = pathname?.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`rounded-lg px-3 py-2 text-sm transition-colors ${
                active
                  ? "bg-gold-500/10 text-gold-400 font-medium"
                  : "text-slate-300 hover:bg-navy-700/60 hover:text-white"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="mt-6 px-2 text-xs text-slate-500">
        Africa Opportunity &amp; Investment Intelligence
      </div>
    </aside>
  );
}
