import { uploadDocuments, fetchDocuments } from "./api.js";

export async function uploadSelectedFiles(files) {
  if (!files || files.length === 0) {
    return {
      ok: false,
      message: "Файлы не выбраны",
    };
  }

  const result = await uploadDocuments(files);

  if (!result.ok) {
    return {
      ok: false,
      message: result.data?.detail || "Ошибка загрузки файлов",
    };
  }

  return {
    ok: true,
    message: "Файлы загружены",
    data: result.data,
  };
}

export async function loadDocuments() {
  const result = await fetchDocuments();

  if (!result.ok) {
    return {
      ok: false,
      message: result.data?.detail || "Ошибка получения списка документов",
      data: [],
    };
  }

  return {
    ok: true,
    data: Array.isArray(result.data) ? result.data : [],
  };
}

