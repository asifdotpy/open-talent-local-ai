// tests/guardrails.test.ts
import pack from "../packs/interview_competency_pack_v1_1.json";

test("blocks age question", ()=>{
  const rules = pack.bias_guardrails?.question_moderation?.blocklist_patterns || [];
  const q = "How old are you?";
  const hit = rules.find((r:any)=> new RegExp(r.pattern,"i").test(q));
  expect(hit?.reason).toMatch(/Age|age/);
});
