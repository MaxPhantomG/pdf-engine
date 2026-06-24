import { searchDocuments, searchInDocument } from "./api.js";

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

    // Новая схема: result.data содержит query, results, total_documents, total_matches
    const searchData = result.data;
    
    return {
      ok: true,
      status: result.status,
      data: {
        query: searchData.query,
        results: searchData.results || [],
        total_documents: searchData.total_documents || 0,
        total_matches: searchData.total_matches || 0
      }
    };
  } catch (err) {
    return { ok: false, status: 500, data: { detail: err?.message || "Не удалось выполнить поиск" } };
  }
}

// ➕ Новая функция для поиска в конкретном документе
export async function runSearchInDocument(documentId, query) {
  if (!query || typeof query !== "string") {
    return { ok: false, status: 400, data: { detail: "Пустой запрос" } };
  }

  try {
    const result = await searchInDocument(documentId, query);

    if (!result.ok) {
      return {
        ok: false,
        status: result.status,
        data: result.data?.detail || "Ошибка поиска в документе",
      };
    }

    return {
      ok: true,
      status: result.status,
      data: result.data
    };
  } catch (err) {
    return { ok: false, status: 500, data: { detail: err?.message || "Не удалось выполнить поиск" } };
  }
}
