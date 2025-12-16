// src/middleware.ts
import type { Request, Response, NextFunction } from "express";
import type { CompetencyPack } from "../schemas/interview_types_v1_1";
export function makeGuardrails(pack: CompetencyPack){
  const patterns = pack.bias_guardrails?.question_moderation?.blocklist_patterns || [];
  const safeRewrites = pack.bias_guardrails?.question_moderation?.safe_rewrites || [];
  const redact = pack.bias_guardrails?.blinding?.redact_fields || [];

  function blockUnsafeQuestions(req: Request, res: Response, next: NextFunction){
    const q = String(req.body?.question ?? "");
    for (const r of patterns){ if (new RegExp(r.pattern,"i").test(q)){ 
      return res.status(400).json({ error: "Unsafe question blocked", reason: r.reason, suggestion: safeRewrites[0]?.safe });
    }}
    next();
  }

  function redactPII(req: Request, _res: Response, next: NextFunction){
    const t = String(req.body?.transcript ?? ""); let red = t;
    for (const f of redact){ red = red.replace(new RegExp(`\b${f}\b`,"gi"), "[REDACTED]"); }
    (req as any).transcript = red; next();
  }

  return { blockUnsafeQuestions, redactPII };
}
