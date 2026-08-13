"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  api,
  CatalogEntry,
  ComplianceSummary,
  Load,
  Project,
  Room,
  RuleResult,
} from "@/lib/api";

const ROOM_TYPES = [
  "sala",
  "cozinha",
  "quarto",
  "banheiro",
  "area_servico",
  "externa",
  "outro",
];

export default function ProjectWorkspace() {
  const { id } = useParams<{ id: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [rooms, setRooms] = useState<Room[]>([]);
  const [selectedRoomId, setSelectedRoomId] = useState<string | null>(null);
  const [loads, setLoads] = useState<Load[]>([]);
  const [catalog, setCatalog] = useState<CatalogEntry[]>([]);
  const [ruleResults, setRuleResults] = useState<RuleResult[]>([]);
  const [compliance, setCompliance] = useState<ComplianceSummary | null>(null);
  const [chatLog, setChatLog] = useState<{ role: "user" | "assistant"; text: string }[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [busy, setBusy] = useState(false);

  const [roomName, setRoomName] = useState("");
  const [roomType, setRoomType] = useState("sala");
  const [roomArea, setRoomArea] = useState("");
  const [roomPerimeter, setRoomPerimeter] = useState("");

  useEffect(() => {
    if (!id) return;
    api.getProject(id).then(setProject);
    api.listRooms(id).then(setRooms);
    api.listCatalog().then(setCatalog);
    refreshCompliance(id);
  }, [id]);

  useEffect(() => {
    if (selectedRoomId) api.listRoomLoads(selectedRoomId).then(setLoads);
  }, [selectedRoomId]);

  function refreshCompliance(projectId: string) {
    api.getRuleResults(projectId).then(setRuleResults).catch(() => {});
    api.getComplianceSummary(projectId).then(setCompliance).catch(() => {});
  }

  async function handleAddRoom(e: React.FormEvent) {
    e.preventDefault();
    if (!id) return;
    const room = await api.addRoom(id, {
      name: roomName,
      room_type: roomType,
      area_m2: roomArea ? parseFloat(roomArea) : null,
      perimeter_m: roomPerimeter ? parseFloat(roomPerimeter) : null,
    });
    setRooms((prev) => [...prev, room]);
    setRoomName("");
    setRoomArea("");
    setRoomPerimeter("");
  }

  async function handleAddCatalogLoad(code: string) {
    if (!selectedRoomId) return;
    const created = await api.addLoadFromCatalog(selectedRoomId, code, 1);
    setLoads((prev) => [...prev, ...created]);
  }

  async function handleGenerate() {
    if (!id) return;
    setBusy(true);
    try {
      await api.generateDesign(id);
      refreshCompliance(id);
      const p = await api.getProject(id);
      setProject(p);
    } catch (err) {
      alert(String(err));
    } finally {
      setBusy(false);
    }
  }

  async function handleSendChat(e: React.FormEvent) {
    e.preventDefault();
    if (!id || !chatInput.trim()) return;
    const message = chatInput;
    setChatLog((prev) => [...prev, { role: "user", text: message }]);
    setChatInput("");
    try {
      const res = await api.chat(id, message);
      setChatLog((prev) => [...prev, { role: "assistant", text: res.reply }]);
    } catch (err) {
      setChatLog((prev) => [...prev, { role: "assistant", text: `Erro: ${String(err)}` }]);
    }
  }

  if (!project) {
    return <main className="p-8 text-gray-400">Carregando projeto...</main>;
  }

  return (
    <main className="flex h-screen flex-col">
      <header className="flex items-center justify-between border-b border-gray-800 bg-panel px-4 py-3">
        <div>
          <a href="/" className="text-sm text-gray-500 hover:text-gray-300">
            ← Projetos
          </a>
          <h1 className="text-xl font-semibold text-white">{project.name}</h1>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleGenerate}
            disabled={busy}
            className="rounded bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-500 disabled:opacity-50"
          >
            {busy ? "Gerando..." : "Gerar projeto elétrico"}
          </button>
          <a
            href={api.documentUrl(project.id)}
            target="_blank"
            rel="noreferrer"
            className="rounded border border-gray-700 px-3 py-1.5 text-sm text-gray-200 hover:border-blue-600"
          >
            Exportar PDF
          </a>
        </div>
      </header>

      <div className="grid flex-1 grid-cols-[280px_1fr_320px] overflow-hidden">
        {/* Painel esquerdo: ambientes e cargas */}
        <aside className="overflow-y-auto border-r border-gray-800 bg-panel/50 p-4">
          <h2 className="text-sm font-semibold uppercase text-gray-400">Ambientes</h2>
          <form onSubmit={handleAddRoom} className="mt-2 space-y-2">
            <input
              required
              placeholder="Nome (ex: Cozinha)"
              value={roomName}
              onChange={(e) => setRoomName(e.target.value)}
              className="w-full rounded border border-gray-700 bg-gray-900 p-1.5 text-sm text-white"
            />
            <select
              value={roomType}
              onChange={(e) => setRoomType(e.target.value)}
              className="w-full rounded border border-gray-700 bg-gray-900 p-1.5 text-sm text-white"
            >
              {ROOM_TYPES.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
            <div className="flex gap-2">
              <input
                placeholder="Área m²"
                value={roomArea}
                onChange={(e) => setRoomArea(e.target.value)}
                className="w-1/2 rounded border border-gray-700 bg-gray-900 p-1.5 text-sm text-white"
              />
              <input
                placeholder="Perímetro m"
                value={roomPerimeter}
                onChange={(e) => setRoomPerimeter(e.target.value)}
                className="w-1/2 rounded border border-gray-700 bg-gray-900 p-1.5 text-sm text-white"
              />
            </div>
            <button className="w-full rounded bg-gray-700 py-1.5 text-sm text-white hover:bg-gray-600">
              Adicionar ambiente
            </button>
          </form>

          <ul className="mt-4 space-y-1">
            {rooms.map((r) => (
              <li key={r.id}>
                <button
                  onClick={() => setSelectedRoomId(r.id)}
                  className={`w-full rounded px-2 py-1.5 text-left text-sm ${
                    selectedRoomId === r.id ? "bg-blue-600 text-white" : "text-gray-300 hover:bg-gray-800"
                  }`}
                >
                  {r.name} <span className="text-xs opacity-70">({r.room_type})</span>
                </button>
              </li>
            ))}
          </ul>

          {selectedRoomId && (
            <div className="mt-6">
              <h3 className="text-sm font-semibold uppercase text-gray-400">Cargas do ambiente</h3>
              <ul className="mt-2 space-y-1 text-sm text-gray-300">
                {loads.map((l) => (
                  <li key={l.id} className="flex justify-between">
                    <span>{l.name}</span>
                    <span className="text-gray-500">{l.nominal_power_w} W</span>
                  </li>
                ))}
                {loads.length === 0 && <li className="text-gray-600">Nenhuma carga cadastrada.</li>}
              </ul>
              <details className="mt-2">
                <summary className="cursor-pointer text-sm text-blue-400">+ Adicionar do catálogo</summary>
                <ul className="mt-1 max-h-64 space-y-1 overflow-y-auto text-xs">
                  {catalog.map((c) => (
                    <li key={c.code}>
                      <button
                        onClick={() => handleAddCatalogLoad(c.code)}
                        className="w-full rounded px-1.5 py-1 text-left text-gray-300 hover:bg-gray-800"
                      >
                        {c.name} — {c.typical_power_w} W{" "}
                        {c.confidence < 0.7 && (
                          <span className="text-status-amarelo">(estimativa)</span>
                        )}
                      </button>
                    </li>
                  ))}
                </ul>
              </details>
            </div>
          )}
        </aside>

        {/* Centro: planta (lista de ambientes) + status */}
        <section className="overflow-y-auto p-6">
          <h2 className="text-lg font-semibold text-white">Planta (visão simplificada)</h2>
          <p className="mt-1 text-sm text-gray-500">
            Nesta versão do MVP os ambientes são cadastrados manualmente. A interpretação
            automática de planta (visão computacional) é um próximo passo.
          </p>
          <div className="mt-4 grid grid-cols-2 gap-3">
            {rooms.map((r) => (
              <div key={r.id} className="rounded-lg border border-gray-800 bg-panel p-4">
                <h3 className="font-medium text-white">{r.name}</h3>
                <p className="text-xs text-gray-500">{r.room_type}</p>
                <p className="mt-2 text-sm text-gray-400">
                  Área: {r.area_m2 ?? "—"} m² · Perímetro: {r.perimeter_m ?? "—"} m
                </p>
              </div>
            ))}
          </div>

          <h2 className="mt-8 text-lg font-semibold text-white">Verificações de regras</h2>
          <ul className="mt-2 space-y-1.5">
            {ruleResults.map((r, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm">
                <span className={`status-badge status-${r.status}`}>{r.status}</span>
                <span className="text-gray-300">{r.message}</span>
              </li>
            ))}
            {ruleResults.length === 0 && (
              <li className="text-gray-600">
                Nenhuma verificação ainda — clique em "Gerar projeto elétrico".
              </li>
            )}
          </ul>
        </section>

        {/* Direita: chat de IA */}
        <aside className="flex flex-col border-l border-gray-800 bg-panel/50">
          <div className="border-b border-gray-800 p-3">
            <h2 className="text-sm font-semibold uppercase text-gray-400">Assistente EletroIA</h2>
          </div>
          <div className="flex-1 space-y-2 overflow-y-auto p-3">
            {chatLog.map((m, idx) => (
              <div
                key={idx}
                className={`rounded p-2 text-sm ${
                  m.role === "user" ? "bg-blue-600/20 text-blue-100" : "bg-gray-800 text-gray-200"
                }`}
              >
                {m.text}
              </div>
            ))}
            {chatLog.length === 0 && (
              <p className="text-sm text-gray-600">
                Pergunte algo sobre o projeto, ex: "Por que o chuveiro está em um circuito
                separado?"
              </p>
            )}
          </div>
          <form onSubmit={handleSendChat} className="border-t border-gray-800 p-3">
            <input
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Digite sua pergunta..."
              className="w-full rounded border border-gray-700 bg-gray-900 p-2 text-sm text-white"
            />
          </form>
        </aside>
      </div>

      {compliance && (
        <footer className="flex gap-4 border-t border-gray-800 bg-panel px-4 py-2 text-xs text-gray-400">
          <span className="status-badge status-VERDE">VERDE {compliance.counts.VERDE ?? 0}</span>
          <span className="status-badge status-AMARELO">AMARELO {compliance.counts.AMARELO ?? 0}</span>
          <span className="status-badge status-VERMELHO">VERMELHO {compliance.counts.VERMELHO ?? 0}</span>
          <span className="status-badge status-AZUL">AZUL {compliance.counts.AZUL ?? 0}</span>
          <span className="ml-auto italic">{compliance.note}</span>
        </footer>
      )}
    </main>
  );
}
