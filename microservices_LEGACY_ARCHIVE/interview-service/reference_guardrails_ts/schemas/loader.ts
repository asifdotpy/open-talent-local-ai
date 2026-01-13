// schemas/loader.ts
import type { CompetencyPack } from "./interview_types_v1_1";
export async function loadCompetencyPack(pathOrUrl: string): Promise<CompetencyPack>{
  if (typeof window === "undefined"){
    const fs = await import("fs/promises").catch(()=>null as any);
    if (fs && !/^https?:/i.test(pathOrUrl)){ const text = await fs.readFile(pathOrUrl,"utf-8"); return JSON.parse(text); }
  }
  const res = await fetch(pathOrUrl); if (!res.ok) throw new Error(`Failed to fetch pack: ${res.status}`); return await res.json();
}
