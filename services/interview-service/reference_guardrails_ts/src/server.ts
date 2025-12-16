// src/server.ts
import express from "express";
import { loadCompetencyPack } from "../schemas/loader";
import { makeGuardrails } from "./middleware";

(async()=>{
  const app = express(); app.use(express.json());
  const pack = await loadCompetencyPack(__dirname + "/../packs/interview_competency_pack_v1_1.json");
  const { blockUnsafeQuestions, redactPII } = makeGuardrails(pack);

  app.post("/ask", blockUnsafeQuestions, (req,res)=> res.json({ok:true, asked:req.body.question}));
  app.post("/transcript", redactPII, (req,res)=> res.json({ transcript: (req as any).transcript }));

  app.listen(3000, ()=> console.log("Guardrail middleware active on :3000"));
})().catch(e=>{ console.error(e); process.exit(1); });
