import { config, finishOptions, json, setCors } from "./_lib/server.js";

export default async function handler(req, res) {
  if (!setCors(req, res)) return json(res, 403, { ok: false, error: "Origin blocked" });
  if (finishOptions(req, res)) return;
  if (req.method !== "GET") return json(res, 405, { ok: false, error: "Method not allowed" });

  const current = config();
  return json(res, 200, {
    ok: true,
    service: "Troll Engine Vercel Server",
    version: "1.0.0",
    repository: current.repository,
    branch: current.branch,
    githubWriteReady: Boolean(current.githubToken && current.apiKey),
    time: new Date().toISOString()
  });
}
