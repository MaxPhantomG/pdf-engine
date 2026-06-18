import { searchDocuments } from "./api.js";

export async function runSearch(query) {
  const trimmed = query.trim();

  if (!trimmed) {
    return {
      ok: false,
      message: "Введите поисковый запрос",
      data: [],
    };
  }

  const result = await searchDocuments(trimmed);

  if (!result.ok) {
    return {
      ok: false,
      message: result.data?.detail || "Ошибка поиска",
      data: [],
    };
  }

  return {
    ok: true,
    data: Array.isArray(result.data) ? result.data : result.data.results || [],
  };
}

