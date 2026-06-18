import { fetchDocumentStatus } from "./api.js";

export async function getDocumentStatus(documentId) {
  const result = await fetchDocumentStatus(documentId);

  if (!result.ok) {
    return {
      ok: false,
      message: result.data?.detail || "Ошибка получения статуса",
      data: null,
    };
  }

  return {
    ok: true,
    data: result.data,
  };
}

export function formatStatus(status) {
  switch (status) {
    case "queued":
      return "В очереди";
    case "processing":
      return "Обрабатывается";
    case "ready":
      return "Готов";
    case "error":
      return "Ошибка";
    default:
      return status || "Неизвестно";
  }
}

