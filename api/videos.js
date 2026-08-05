import { handleUpload } from "@vercel/blob/client";
import { list } from "@vercel/blob";

const VIDEO_PREFIX = "troll-engine/videos/";
const MAX_VIDEO_BYTES = 5 * 1024 * 1024 * 1024;

function setCors(req, res) {
  const allowed = process.env.TROLL_ENGINE_CORS_ORIGIN || "*";
  const origin = String(req.headers.origin || "");
  res.setHeader("Access-Control-Allow-Origin", allowed === "*" ? "*" : allowed);
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Vary", "Origin");
  return allowed === "*" || !origin || origin === allowed;
}

function send(res, status, body) {
  res.status(status).json(body);
}

function parseBody(req) {
  if (req.body && typeof req.body === "object") return req.body;
  if (typeof req.body === "string" && req.body.trim()) return JSON.parse(req.body);
  return {};
}

function decodeBase64Url(value) {
  try {
    const normalized = String(value || "").replace(/-/g, "+").replace(/_/g, "/");
    const padded = normalized + "=".repeat((4 - (normalized.length % 4)) % 4);
    return Buffer.from(padded, "base64").toString("utf8");
  } catch {
    return "";
  }
}

function parseMetadata(pathname) {
  const basename = String(pathname || "").split("/").pop() || "video";
  const parts = basename.split("~");
  if (parts.length < 4) {
    return { title: basename, uploader: "Troll Engine user", name: basename };
  }
  return {
    title: decodeBase64Url(parts[1]) || parts[3],
    uploader: decodeBase64Url(parts[2]) || "Troll Engine user",
    name: parts.slice(3).join("~")
  };
}

export default async function handler(req, res) {
  if (!setCors(req, res)) return send(res, 403, { ok: false, error: "Origin blocked" });
  if (req.method === "OPTIONS") return res.status(204).end();

  if (!process.env.BLOB_READ_WRITE_TOKEN) {
    return send(res, 503, {
      ok: false,
      error: "Vercel Blobストアがまだ接続されていません"
    });
  }

  try {
    if (req.method === "GET") {
      const result = await list({ prefix: VIDEO_PREFIX, limit: 1000 });
      const videos = result.blobs
        .filter(blob => String(blob.contentType || "").startsWith("video/"))
        .sort((a, b) => new Date(b.uploadedAt) - new Date(a.uploadedAt))
        .map(blob => ({
          ...parseMetadata(blob.pathname),
          url: blob.url,
          downloadUrl: blob.downloadUrl,
          pathname: blob.pathname,
          contentType: blob.contentType,
          size: blob.size,
          uploadedAt: blob.uploadedAt
        }));
      res.setHeader("Cache-Control", "no-store");
      return send(res, 200, { ok: true, videos, hasMore: result.hasMore });
    }

    if (req.method !== "POST") {
      return send(res, 405, { ok: false, error: "Method not allowed" });
    }

    if (!process.env.TROLL_ENGINE_API_KEY) {
      return send(res, 503, {
        ok: false,
        error: "アップロードキーがVercelに設定されていません"
      });
    }

    const response = await handleUpload({
      body: parseBody(req),
      request: req,
      onBeforeGenerateToken: async (pathname, clientPayload) => {
        if (!String(pathname || "").startsWith(VIDEO_PREFIX)) {
          throw new Error("Invalid video path");
        }

        let payload = {};
        try {
          payload = clientPayload ? JSON.parse(clientPayload) : {};
        } catch {
          throw new Error("Invalid upload information");
        }

        if (payload.apiKey !== process.env.TROLL_ENGINE_API_KEY) {
          throw new Error("Upload key is incorrect");
        }

        return {
          allowedContentTypes: [
            "video/mp4",
            "video/webm",
            "video/quicktime",
            "video/x-m4v"
          ],
          maximumSizeInBytes: MAX_VIDEO_BYTES,
          addRandomSuffix: true,
          tokenPayload: JSON.stringify({
            title: String(payload.title || "").slice(0, 120),
            uploader: String(payload.uploader || "").slice(0, 80)
          })
        };
      },
      onUploadCompleted: async ({ blob, tokenPayload }) => {
        console.log("Troll Engine video uploaded", {
          pathname: blob.pathname,
          url: blob.url,
          metadata: tokenPayload
        });
      }
    });

    return send(res, 200, response);
  } catch (error) {
    console.error("videos api error", error);
    return send(res, 400, {
      ok: false,
      error: error?.message || "Video request failed"
    });
  }
}
