import { fetchDocumentStatus } from "./api.js";

export function formatStatus(status) {
  switch ((status || "").toString().toLowerCase()) {
    case "queued":
      return "Ожидание";
    case "processing":
      return "Обрабатывается";
    case "ready":
      return "Готов";
    case "failed":
      return "Ошибка";
    default:
      return String(status || "неизвестно");
  }
}


export async function getDocumentStatus(documentId) {
  try {
    const result = await fetchDocumentStatus(documentId);
    return {
      ok: result.ok,
      status: result.status,
      data: result.data,
    };
  } catch (e) {
    return { ok: false, status: 500, data: { detail: e?.message ?? "Ошибка запроса статуса" } };
  }
}
