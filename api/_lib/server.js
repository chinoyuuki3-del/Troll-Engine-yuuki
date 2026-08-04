const DEFAULT_REPOSITORY = "chinoyuuki3-del/Troll-Engine-yuuki";
const DEFAULT_BRANCH = "main";
const MAX_JSON_BYTES = 900_000;
const MAX_MEDIA_BYTES = 2_500_000;

const ROOT_JSON_FILES = new Set([
  "events.json",
  "features.json",
  "news.json",
  "projects.json",
  "releases.json",
  "status.json",
  "themes.json",
  "update.json",
  "users.json"
]);

const MEDIA_PREFIXES = ["media/", "uploads/", "videos/", "voice/"];
const SENSITIVE_PARTS = [
  "password",
  "passwd",
  "secret",
  "token",
  "credential",
  "private-key",
  "location-history",
  "precise-location"
];

export function config() {
  return {
    repository: process.env.GITHUB_REPO || DEFAULT_REPOSITORY,
    branch: process.env.GITHUB_BRANCH || DEFAULT_BRANCH,
    githubToken: process.env.GITHUB_TOKEN || "",
    apiKey: process.env.TROLL_ENGINE_API_KEY || "",
    corsOrigin: process.env.TROLL_ENGINE_CORS_ORIGIN || "*"
  };
}

export function setCors(req, res) {
  const { corsOrigin } = config();
  const requestedOrigin = req.headers.origin;
  const allowedOrigin = corsOrigin === "*" ? "*" : corsOrigin;

  res.setHeader("Access-Control-Allow-Origin", allowedOrigin);
  res.setHeader("Access-Control-Allow-Methods", "GET,PUT,POST,OPTIONS");
  res.setHeader(
    "Access-Control-Allow-Headers",
    "Content-Type,Authorization,X-Troll-Engine-Key"
  );
  res.setHeader("Vary", "Origin");

  if (requestedOrigin && corsOrigin !== "*" && requestedOrigin !== corsOrigin) {
    return false;
  }
  return true;
}

export function finishOptions(req, res) {
  if (req.method === "OPTIONS") {
    res.status(204).end();
    return true;
  }
  return false;
}

export function json(res, status, body) {
  res.status(status).json(body);
}

export function requireWriteAuth(req, res) {
  const { apiKey, githubToken } = config();
  if (!githubToken) {
    json(res, 503, {
      ok: false,
      error: "GITHUB_TOKEN is not configured on Vercel."
    });
    return false;
  }
  if (!apiKey) {
    json(res, 503, {
      ok: false,
      error: "TROLL_ENGINE_API_KEY is not configured on Vercel."
    });
    return false;
  }

  const bearer = String(req.headers.authorization || "").replace(/^Bearer\s+/i, "");
  const headerKey = String(req.headers["x-troll-engine-key"] || "");
  if (bearer !== apiKey && headerKey !== apiKey) {
    json(res, 401, { ok: false, error: "Unauthorized" });
    return false;
  }
  return true;
}

function cleanPath(input) {
  return String(input || "")
    .trim()
    .replace(/^\/+/, "")
    .replace(/\\/g, "/");
}

function hasUnsafeSegments(path) {
  return (
    !path ||
    path.includes("..") ||
    path.includes("//") ||
    path.startsWith(".") ||
    /[\u0000-\u001f\u007f]/.test(path)
  );
}

function hasSensitiveName(path) {
  const lower = path.toLowerCase();
  return SENSITIVE_PARTS.some(part => lower.includes(part));
}

export function validateDataPath(input) {
  const path = cleanPath(input);
  if (hasUnsafeSegments(path) || hasSensitiveName(path)) return null;
  if (ROOT_JSON_FILES.has(path)) return path;
  if (/^data\/[A-Za-z0-9._/-]+\.json$/.test(path)) return path;
  return null;
}

export function validateMediaPath(input) {
  const path = cleanPath(input);
  if (hasUnsafeSegments(path) || hasSensitiveName(path)) return null;
  if (!MEDIA_PREFIXES.some(prefix => path.startsWith(prefix))) return null;
  if (!/^[A-Za-z0-9._/-]+$/.test(path)) return null;
  return path;
}

export function measureJson(value) {
  const text = JSON.stringify(value);
  return { text, bytes: Buffer.byteLength(text, "utf8") };
}

export function decodeBase64(value) {
  const normalized = String(value || "").replace(/^data:[^;]+;base64,/, "");
  if (!/^[A-Za-z0-9+/]*={0,2}$/.test(normalized) || normalized.length % 4 !== 0) {
    throw new Error("Invalid base64 content");
  }
  return Buffer.from(normalized, "base64");
}

export { MAX_JSON_BYTES, MAX_MEDIA_BYTES };

export async function githubRequest(path, options = {}) {
  const { githubToken } = config();
  const headers = {
    Accept: "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "Troll-Engine-Vercel-Server",
    ...(options.headers || {})
  };
  if (githubToken) headers.Authorization = `Bearer ${githubToken}`;

  const response = await fetch(`https://api.github.com${path}`, {
    ...options,
    headers
  });

  const text = await response.text();
  let body = null;
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = { message: text };
    }
  }

  if (!response.ok) {
    const error = new Error(body?.message || `GitHub API error ${response.status}`);
    error.status = response.status;
    error.details = body;
    throw error;
  }
  return body;
}

export async function readGithubFile(path) {
  const { repository, branch } = config();
  const encodedPath = path.split("/").map(encodeURIComponent).join("/");
  const body = await githubRequest(
    `/repos/${repository}/contents/${encodedPath}?ref=${encodeURIComponent(branch)}`
  );
  if (Array.isArray(body) || body.type !== "file") {
    const error = new Error("The requested path is not a file");
    error.status = 400;
    throw error;
  }
  return body;
}

export async function writeGithubFile({ path, contentBase64, message, sha }) {
  const { repository, branch } = config();
  const encodedPath = path.split("/").map(encodeURIComponent).join("/");
  return githubRequest(`/repos/${repository}/contents/${encodedPath}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      content: contentBase64,
      branch,
      ...(sha ? { sha } : {})
    })
  });
}

export function toPublicRawUrl(path) {
  const { repository, branch } = config();
  return `https://raw.githubusercontent.com/${repository}/${branch}/${path}`;
}
