// schemas/zod_schema.ts
import { z } from "zod";
export const CompetencyPackSchema = z.object({
  pack_name: z.string(),
  version: z.string(),
  updated: z.string(),
  competencies: z.array(z.any()).min(1),
  bias_guardrails: z.any().optional()
});
