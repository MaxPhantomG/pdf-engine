import { searchDocuments } from "./api.js";

export async function runSearch(query) {
  if (!query || typeof query !== "string") {
    return { ok: false, status: 400, data: { detail: "Пустой запрос" } };
  }

  try {
    const result = await searchDocuments(query);

    if (!result.ok) {
      return {
        ok: false,
        status: result.status,
        data: result.data?.detail || "Ошибка поисковой операции",
      };
    }

    const data =
      Array.isArray(result.data)
        ? result.data
        : Array.isArray(result.data?.results)
        ? result.data.results
        : [];

    return { ok: true, status: result.status, data };
  } catch (err) {
    return { ok: false, status: 500, data: { detail: err?.message || "Не удалось выполнить поиск" } };
  }
}
