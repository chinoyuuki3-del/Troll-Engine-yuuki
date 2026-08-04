import {
  MAX_JSON_BYTES,
  decodeBase64,
  finishOptions,
  json,
  measureJson,
  readGithubFile,
  requireWriteAuth,
  setCors,
  toPublicRawUrl,
  validateDataPath,
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

  const requestedPath = req.method === "GET" ? req.query.path : parseBody(req).path;
  const path = validateDataPath(requestedPath);
  if (!path) return json(res, 400, { ok: false, error: "Invalid or blocked JSON path" });

  try {
    if (req.method === "GET") {
      const file = await readGithubFile(path);
      const decoded = decodeBase64(String(file.content || "").replace(/\n/g, ""));
      const text = decoded.toString("utf8");
      let value;
      try {
        value = JSON.parse(text);
      } catch {
        return json(res, 502, { ok: false, error: "GitHub file is not valid JSON", path });
      }
      return json(res, 200, {
        ok: true,
        path,
        sha: file.sha,
        value,
        rawUrl: toPublicRawUrl(path)
      });
    }

    if (req.method === "PUT" || req.method === "POST") {
      if (!requireWriteAuth(req, res)) return;
      const body = parseBody(req);
      if (!("value" in body)) {
        return json(res, 400, { ok: false, error: "Body must include value" });
      }

      const measured = measureJson(body.value);
      if (measured.bytes > MAX_JSON_BYTES) {
        return json(res, 413, {
          ok: false,
          error: `JSON is too large. Maximum is ${MAX_JSON_BYTES} bytes.`
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

      const formatted = `${JSON.stringify(body.value, null, 2)}\n`;
      const result = await writeGithubFile({
        path,
        contentBase64: Buffer.from(formatted, "utf8").toString("base64"),
        message: String(body.message || `Troll Engine: update ${path}`).slice(0, 180),
        sha: existingSha || undefined
      });

      return json(res, 200, {
        ok: true,
        path,
        commitSha: result.commit?.sha || null,
        contentSha: result.content?.sha || null,
        rawUrl: toPublicRawUrl(path)
      });
    }

    return json(res, 405, { ok: false, error: "Method not allowed" });
  } catch (error) {
    console.error("data api error", error);
    return json(res, error.status || 500, {
      ok: false,
      error: error.message || "Unexpected error",
      details: error.details || undefined
    });
  }
}
