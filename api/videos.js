import { handleUpload } from "@vercel/blob/client";
import { list } from "@vercel/blob";

const VIDEO_PREFIX = "troll-engine/videos/";
const MAX_VIDEO_BYTES = 5 * 1024 * 1024 * 1024;

function setCors(req, res) {
  const allowed = process.env.TROLL_ENGINE_CORS_ORIGIN || "*";
  const origin = String(req.headers.origin || "");
  res.setHeader("Access-Control-Allow-Origin", allowed === "*" ? "*" : allowed);
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type,X-Troll-Engine-Key");
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

function safeName(pathname) {
  return String(pathname || "video")
    .split("/")
    .pop()
    .replace(/[^A-Za-z0-9._-]/g, "_")
    .slice(0, 120);
}

export default async function handler(req, res) {
  if (!setCors(req, res)) return send(res, 403, { ok: false, error: "Origin blocked" });
  if (req.method === "OPTIONS") return res.status(204).end();

  try {
    if (req.method === "GET") {
      const result = await list({ prefix: VIDEO_PREFIX, limit: 1000 });
      const videos = result.blobs
        .filter(blob => String(blob.contentType || "").startsWith("video/"))
        .sort((a, b) => new Date(b.uploadedAt) - new Date(a.uploadedAt))
        .map(blob => ({
          url: blob.url,
          downloadUrl: blob.downloadUrl,
          pathname: blob.pathname,
          name: safeName(blob.pathname),
          contentType: blob.contentType,
          size: blob.size,
          uploadedAt: blob.uploadedAt
        }));
      return send(res, 200, { ok: true, videos, hasMore: result.hasMore });
    }

    if (req.method !== "POST") {
      return send(res, 405, { ok: false, error: "Method not allowed" });
    }

    const body = parseBody(req);
    const response = await handleUpload({
      body,
      request: req,
      onBeforeGenerateToken: async (pathname, clientPayload) => {
        const expectedKey = process.env.TROLL_ENGINE_API_KEY || "";
        let payload = {};
        try {
          payload = clientPayload ? JSON.parse(clientPayload) : {};
        } catch {
          throw new Error("Invalid upload information");
        }
        if (!expectedKey || payload.apiKey !== expectedKey) {
          throw new Error("Upload key is incorrect");
        }

        const filename = safeName(pathname);
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
            title: String(payload.title || filename).slice(0, 120),
            uploader: String(payload.uploader || "Troll Engine user").slice(0, 80)
          })
        };
      },
      onUploadCompleted: async ({ blob, tokenPayload }) => {
        console.log("Troll Engine Blob video uploaded", {
          url: blob.url,
          pathname: blob.pathname,
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
