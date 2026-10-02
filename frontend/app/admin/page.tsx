"use client";

import { useEffect, useState } from "react";
import Topbar from "@/components/Topbar";
import { clientApi } from "@/lib/clientApi";
import { ScoringWeight, Sector, Source, TriggerDef } from "@/lib/types";

export default function AdminPage() {
  const [token, setToken] = useState<string | null>(null);
  const [email, setEmail] = useState("admin@africand.com");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState<string | null>(null);

  const [sources, setSources] = useState<Source[]>([]);
  const [sectors, setSectors] = useState<Sector[]>([]);
  const [triggers, setTriggers] = useState<TriggerDef[]>([]);
  const [weights, setWeights] = useState<ScoringWeight[]>([]);
  const [ingestResult, setIngestResult] = useState<string | null>(null);

  const [newSourceName, setNewSourceName] = useState("");
  const [newSourceUrl, setNewSourceUrl] = useState("");
  const [newSectorName, setNewSectorName] = useState("");

  useEffect(() => {
    const saved = typeof window !== "undefined" ? window.localStorage.getItem("africand_admin_token") : null;
    if (saved) setToken(saved);
    refreshAll();
  }, []);

  async function refreshAll() {
    const [s, sec, trig, w] = await Promise.all([
      clientApi.get<Source[]>("/admin/sources"),
      clientApi.get<Sector[]>("/admin/sectors"),
      clientApi.get<TriggerDef[]>("/admin/triggers"),
      clientApi.get<ScoringWeight[]>("/admin/scoring-weights"),
    ]);
    setSources(s ?? []);
    setSectors(sec ?? []);
    setTriggers(trig ?? []);
    setWeights(w ?? []);
  }

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setLoginError(null);
    const result = await clientApi.post<{ access_token: string }>("/admin/login", { email, password });
    if (!result) {
      setLoginError("Identifiants invalides ou API indisponible.");
      return;
    }
    setToken(result.access_token);
    window.localStorage.setItem("africand_admin_token", result.access_token);
  }

  async function handleAddSource(e: React.FormEvent) {
    e.preventDefault();
    if (!token) return;
    await clientApi.post("/admin/sources", { name: newSourceName, url: newSourceUrl }, token);
    setNewSourceName("");
    setNewSourceUrl("");
    refreshAll();
  }

  async function handleAddSector(e: React.FormEvent) {
    e.preventDefault();
    if (!token) return;
    await clientApi.post("/admin/sectors", { name: newSectorName, priority: 2 }, token);
    setNewSectorName("");
    refreshAll();
  }

  async function handleDeleteSource(id: number) {
    if (!token) return;
    await clientApi.delete(`/admin/sources/${id}`, token);
    refreshAll();
  }

  async function handleWeightChange(criterion: string, value: number) {
    if (!token) return;
    await clientApi.put(`/admin/scoring-weights/${criterion}`, { weight_percent: value }, token);
    refreshAll();
  }

  async function handleRunIngestion() {
    if (!token) return;
    setIngestResult("Collecte en cours...");
    const result = await clientApi.post<{
      raw_items_collected: number;
      opportunities_created: number;
      opportunities_merged: number;
      alerts_sent: number;
    }>("/admin/ingest/run", {}, token);
    if (!result) {
      setIngestResult("Échec de la collecte.");
      return;
    }
    setIngestResult(
      `${result.raw_items_collected} éléments collectés · ${result.opportunities_created} opportunités créées · ` +
        `${result.opportunities_merged} fusionnées (déduplication) · ${result.alerts_sent} alertes envoyées.`
    );
  }

  return (
    <>
      <Topbar title="Administration" subtitle="Sources, secteurs, triggers, pondérations du score et collecte." />
      <div className="space-y-6 px-6 py-8 md:px-10">
        {!token ? (
          <form onSubmit={handleLogin} className="card max-w-sm space-y-3 p-5">
            <h2 className="font-serif text-lg text-white">Connexion administrateur</h2>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email"
              className="w-full rounded-md border border-navy-600 bg-navy-900 px-3 py-2 text-sm text-slate-100"
            />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Mot de passe"
              className="w-full rounded-md border border-navy-600 bg-navy-900 px-3 py-2 text-sm text-slate-100"
            />
            {loginError && <p className="text-xs text-red-400">{loginError}</p>}
            <button className="w-full rounded-md bg-gold-500 px-3 py-2 text-sm font-medium text-navy-950 hover:bg-gold-400">
              Se connecter
            </button>
          </form>
        ) : (
          <>
            <div className="card flex items-center justify-between p-5">
              <div>
                <h2 className="font-serif text-lg text-white">Collecte & traitement</h2>
                <p className="text-sm text-slate-400">
                  Lance le pipeline complet : collecte des sources actives → extraction IA → détection des triggers →
                  déduplication → scoring → alertes.
                </p>
                {ingestResult && <p className="mt-2 text-sm text-gold-400">{ingestResult}</p>}
              </div>
              <button
                onClick={handleRunIngestion}
                className="shrink-0 rounded-md bg-gold-500 px-4 py-2 text-sm font-medium text-navy-950 hover:bg-gold-400"
              >
                Lancer la collecte
              </button>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <div className="card p-5">
                <h2 className="mb-3 font-serif text-lg text-white">Sources ({sources.length})</h2>
                <form onSubmit={handleAddSource} className="mb-3 flex gap-2">
                  <input
                    value={newSourceName}
                    onChange={(e) => setNewSourceName(e.target.value)}
                    placeholder="Nom de la source"
                    className="w-1/3 rounded-md border border-navy-600 bg-navy-900 px-2 py-1.5 text-xs text-slate-100"
                  />
                  <input
                    value={newSourceUrl}
                    onChange={(e) => setNewSourceUrl(e.target.value)}
                    placeholder="URL du flux RSS"
                    className="flex-1 rounded-md border border-navy-600 bg-navy-900 px-2 py-1.5 text-xs text-slate-100"
                  />
                  <button className="rounded-md bg-navy-700 px-3 py-1.5 text-xs text-slate-100 hover:bg-navy-600">
                    Ajouter
                  </button>
                </form>
                <div className="max-h-72 space-y-1.5 overflow-y-auto">
                  {sources.map((s) => (
                    <div
                      key={s.id}
                      className="flex items-center justify-between rounded-md border border-navy-600/50 bg-navy-900/40 px-3 py-2 text-xs"
                    >
                      <div className="min-w-0">
                        <p className="truncate text-slate-200">{s.name}</p>
                        <p className="truncate text-slate-500">{s.url}</p>
                      </div>
                      <div className="flex shrink-0 items-center gap-2">
                        <span className={s.active ? "text-emerald-400" : "text-slate-500"}>
                          {s.active ? "Actif" : "Inactif"}
                        </span>
                        <button onClick={() => handleDeleteSource(s.id)} className="text-red-400 hover:underline">
                          Supprimer
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="card p-5">
                <h2 className="mb-3 font-serif text-lg text-white">Secteurs ({sectors.length})</h2>
                <form onSubmit={handleAddSector} className="mb-3 flex gap-2">
                  <input
                    value={newSectorName}
                    onChange={(e) => setNewSectorName(e.target.value)}
                    placeholder="Nouveau secteur"
                    className="flex-1 rounded-md border border-navy-600 bg-navy-900 px-2 py-1.5 text-xs text-slate-100"
                  />
                  <button className="rounded-md bg-navy-700 px-3 py-1.5 text-xs text-slate-100 hover:bg-navy-600">
                    Ajouter
                  </button>
                </form>
                <div className="max-h-72 space-y-1.5 overflow-y-auto">
                  {sectors.map((s) => (
                    <div
                      key={s.id}
                      className="flex items-center justify-between rounded-md border border-navy-600/50 bg-navy-900/40 px-3 py-2 text-xs"
                    >
                      <span className="text-slate-200">{s.name}</span>
                      <span className="text-slate-500">Priorité {s.priority}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <div className="card p-5">
                <h2 className="mb-3 font-serif text-lg text-white">Triggers ({triggers.length})</h2>
                <div className="max-h-72 space-y-1.5 overflow-y-auto">
                  {triggers.map((t) => (
                    <div key={t.id} className="rounded-md border border-navy-600/50 bg-navy-900/40 px-3 py-2 text-xs">
                      <p className="text-slate-200">{t.name}</p>
                      <p className="text-slate-500">{t.keywords.join(", ")}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="card p-5">
                <h2 className="mb-3 font-serif text-lg text-white">Pondérations du score (total 100%)</h2>
                <div className="space-y-3">
                  {weights.map((w) => (
                    <div key={w.criterion} className="flex items-center justify-between gap-3 text-sm">
                      <span className="text-slate-300">{w.label}</span>
                      <input
                        type="number"
                        defaultValue={w.weight_percent}
                        onBlur={(e) => handleWeightChange(w.criterion, Number(e.target.value))}
                        className="w-20 rounded-md border border-navy-600 bg-navy-900 px-2 py-1 text-right text-slate-100"
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </>
  );
}
