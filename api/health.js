import { config, finishOptions, json, setCors } from "./_lib/server.js";

export default async function handler(req, res) {
  if (!setCors(req, res)) return json(res, 403, { ok: false, error: "Origin blocked" });
  if (finishOptions(req, res)) return;
  if (req.method !== "GET") return json(res, 405, { ok: false, error: "Method not allowed" });

  const current = config();
  const blobReady = Boolean(process.env.BLOB_READ_WRITE_TOKEN);
  const uploadKeyReady = Boolean(current.apiKey);
  const githubWriteReady = Boolean(current.githubToken && current.apiKey);

  res.setHeader("Cache-Control", "no-store");
  return json(res, 200, {
    ok: true,
    service: "Troll Engine Vercel Server",
    version: "1.1.0",
    appVersion: "4.29-beta.2",
    repository: current.repository,
    branch: current.branch,
    blobReady,
    uploadKeyReady,
    githubWriteReady,
    videoShareReady: blobReady && uploadKeyReady,
    time: new Date().toISOString()
  });
}
