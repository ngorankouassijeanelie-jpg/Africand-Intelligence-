export default function Topbar({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <header className="flex flex-col gap-1 border-b border-navy-600/60 bg-navy-900/60 px-6 py-5 md:px-10">
      <h1 className="font-serif text-2xl text-white">{title}</h1>
      {subtitle ? <p className="text-sm text-slate-400">{subtitle}</p> : null}
    </header>
  );
}
