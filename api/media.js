import {
  MAX_MEDIA_BYTES,
  decodeBase64,
  finishOptions,
  json,
  readGithubFile,
  requireWriteAuth,
  setCors,
  toPublicRawUrl,
  validateMediaPath,
  writeGithubFile
} from "./_lib/server.js";

function parseBody(req) {
  if (req.body && typeof req.body === "object") return req.body;
  if (typeof req.body === "string" && req.body.trim()) return JSON.parse(req.body);
  return {};
}

export default async function handler(req, res) {
  if (!setCors(req, res)) return json(res, 403, { ok: false, error: "Origin blocked" });
  if (finishOptions(req, res)) return;
  if (req.method !== "POST" && req.method !== "PUT") {
    return json(res, 405, { ok: false, error: "Method not allowed" });
  }
  if (!requireWriteAuth(req, res)) return;

  try {
    const body = parseBody(req);
    const path = validateMediaPath(body.path);
    if (!path) return json(res, 400, { ok: false, error: "Invalid or blocked media path" });

    const bytes = decodeBase64(body.contentBase64);
    if (!bytes.length) return json(res, 400, { ok: false, error: "Empty media file" });
    if (bytes.length > MAX_MEDIA_BYTES) {
      return json(res, 413, {
        ok: false,
        error: `Media is too large for the Vercel API route. Maximum is ${MAX_MEDIA_BYTES} bytes.`,
        largeVideoHint: "Upload large videos as GitHub Release assets, then save their URL in data/aft-videos.json."
      });
    }

    let existingSha = body.sha || "";
    if (!existingSha) {
      try {
        existingSha = (await readGithubFile(path)).sha;
      } catch (error) {
        if (error.status !== 404) throw error;
      }
    }

    const result = await writeGithubFile({
      path,
      contentBase64: bytes.toString("base64"),
      message: String(body.message || `Troll Engine: upload ${path}`).slice(0, 180),
      sha: existingSha || undefined
    });

    return json(res, 200, {
      ok: true,
      path,
      bytes: bytes.length,
      commitSha: result.commit?.sha || null,
      contentSha: result.content?.sha || null,
      rawUrl: toPublicRawUrl(path)
    });
  } catch (error) {
    console.error("media api error", error);
    return json(res, error.status || 500, {
      ok: false,
      error: error.message || "Unexpected error",
      details: error.details || undefined
    });
  }
}
