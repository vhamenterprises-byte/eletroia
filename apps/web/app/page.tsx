"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, Project } from "@/lib/api";

const DEMO_USER_KEY = "eletroia_user_id";

async function getOrCreateDemoUser(): Promise<string> {
  const cached = typeof window !== "undefined" ? localStorage.getItem(DEMO_USER_KEY) : null;
  if (cached) return cached;
  const user = await api.createUser("demo@eletroia.local", "Usuário Demo");
  localStorage.setItem(DEMO_USER_KEY, user.id);
  return user.id;
}

export default function HomePage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");
  const [supplyVoltage, setSupplyVoltage] = useState("127/220V");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listProjects().then(setProjects).catch(() => setError("Não foi possível conectar à API. Verifique se o backend está rodando."));
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const ownerId = await getOrCreateDemoUser();
      const project = await api.createProject({
        owner_id: ownerId,
        name,
        address,
        supply_voltage: supplyVoltage,
      });
      router.push(`/projects/${project.id}`);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-3xl p-8">
      <h1 className="text-3xl font-bold text-white">EletroIA</h1>
      <p className="mt-1 text-gray-400">
        Assistente de engenharia elétrica residencial — a IA conduz, o motor determinístico decide.
      </p>

      {error && (
        <div className="mt-4 rounded border border-status-vermelho/40 bg-status-vermelho/10 p-3 text-sm text-status-vermelho">
          {error}
        </div>
      )}

      <form onSubmit={handleCreate} className="mt-8 space-y-4 rounded-lg border border-gray-800 bg-panel p-6">
        <h2 className="text-lg font-semibold text-white">Novo projeto</h2>
        <div>
          <label className="block text-sm text-gray-400">Nome do projeto</label>
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="mt-1 w-full rounded border border-gray-700 bg-gray-900 p-2 text-white"
            placeholder="Casa da Praia"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-400">Endereço</label>
          <input
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            className="mt-1 w-full rounded border border-gray-700 bg-gray-900 p-2 text-white"
            placeholder="Rua Exemplo, 123"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-400">Tensão de fornecimento</label>
          <select
            value={supplyVoltage}
            onChange={(e) => setSupplyVoltage(e.target.value)}
            className="mt-1 w-full rounded border border-gray-700 bg-gray-900 p-2 text-white"
          >
            <option>127/220V</option>
            <option>220/380V</option>
            <option>Não sei</option>
          </select>
        </div>
        <button
          disabled={loading}
          className="rounded bg-blue-600 px-4 py-2 font-medium text-white hover:bg-blue-500 disabled:opacity-50"
        >
          {loading ? "Criando..." : "Criar projeto"}
        </button>
      </form>

      <section className="mt-10">
        <h2 className="text-lg font-semibold text-white">Projetos existentes</h2>
        <ul className="mt-3 space-y-2">
          {projects.map((p) => (
            <li key={p.id}>
              <a
                href={`/projects/${p.id}`}
                className="block rounded border border-gray-800 bg-panel p-3 hover:border-blue-600"
              >
                <span className="font-medium text-white">{p.name}</span>{" "}
                <span className="text-sm text-gray-500">({p.status})</span>
              </a>
            </li>
          ))}
          {projects.length === 0 && <p className="text-gray-500">Nenhum projeto ainda.</p>}
        </ul>
      </section>
    </main>
  );
}
