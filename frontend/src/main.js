import { handleLogin, handleRegister } from "./auth.js";
import { uploadSelectedFiles, loadDocuments } from "./documents.js";
import { runSearch } from "./search.js";
import { getDocumentStatus, formatStatus } from "./status.js";
import { isLoggedIn, clearToken } from "./api.js";

const authForm = document.getElementById("auth-form");
const authMessage = document.getElementById("auth-message");
const loginBtn = document.getElementById("login-btn");
const registerBtn = document.getElementById("register-btn");
const logoutBtn = document.getElementById("logout-btn");

const uploadForm = document.getElementById("upload-form");
const uploadMessage = document.getElementById("upload-message");
const pdfFilesInput = document.getElementById("pdf-files");

const refreshDocsBtn = document.getElementById("refresh-docs-btn");
const documentsList = document.getElementById("documents-list");

const searchForm = document.getElementById("search-form");
const searchResults = document.getElementById("search-results");
const searchMessage = document.getElementById("search-message");

const authSection = document.getElementById("auth-section");
const appSection = document.getElementById("app-section");
const documentsSection = document.getElementById("documents-section");
const uploadSection = document.getElementById("upload-section");
const searchSection = document.getElementById("search-section");

let statusRefreshTimer = null;

function $(id) {
  return document.getElementById(id);
}

function setMessage(element, text, isError = false) {
  if (!element) return;

  element.textContent = text || "";
  element.classList.remove("message--error", "message--success");

  if (text) {
    element.classList.add(isError ? "message--error" : "message--success");
  }
}

function setAuthMode(mode) {
  if (!authForm) return;
  authForm.dataset.mode = mode;

  if (loginBtn) {
    loginBtn.classList.toggle("active", mode === "login");
  }

  if (registerBtn) {
    registerBtn.classList.toggle("active", mode === "register");
  }

  if (authForm) {
    authForm.dataset.mode = mode;
  }
}

function getAuthMode() {
  return authForm?.dataset?.mode || "login";
}

function showApp(isAuthenticated) {
  document.body.classList.toggle("authenticated", isAuthenticated);

  if (authSection) authSection.style.display = isAuthenticated ? "none" : "";
  if (appSection) appSection.style.display = isAuthenticated ? "" : "none";

  if (documentsSection) documentsSection.style.display = isAuthenticated ? "" : "none";
  if (uploadSection) uploadSection.style.display = isAuthenticated ? "" : "none";
  if (searchSection) searchSection.style.display = isAuthenticated ? "" : "none";
  if (logoutBtn) logoutBtn.style.display = isAuthenticated ? "" : "none";
}

function clearResults(container, text) {
  if (!container) return;
  container.innerHTML = "";
  if (text) {
    container.textContent = text;
  }
}

function normalizeArray(payload) {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.items)) return payload.items;
  if (Array.isArray(payload?.data)) return payload.data;
  return [];
}

function renderDocuments(documents) {
  if (!documentsList) return;

  documentsList.innerHTML = "";

  if (!documents?.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "Документы не найдены";
    documentsList.appendChild(empty);
    return;
  }

  const wrapper = document.createElement("div");
  wrapper.className = "documents-grid";

  documents.forEach((doc) => {
    const item = document.createElement("div");
    item.className = "doc-item";

    const title = doc.name || doc.filename || doc.title || `Документ #${doc.id ?? ""}`;
    const statusText = formatStatus(doc.status);
    const size = doc.size ? `${doc.size} байт` : "";
    const uploadedAt = doc.uploaded_at ? `Загружен: ${doc.uploaded_at}` : "";

    const titleEl = document.createElement("strong");
    titleEl.textContent = title;

    const statusRow = document.createElement("div");
    statusRow.className = "doc-meta";

    const statusLabel = document.createElement("span");
    statusLabel.textContent = "Статус: ";

    const statusValue = document.createElement("span");
    statusValue.dataset.statusId = String(doc.id);
    statusValue.textContent = statusText;
    statusValue.className = `status-badge status-${String(doc.status || "unknown").toLowerCase()}`;

    statusRow.appendChild(statusLabel);
    statusRow.appendChild(statusValue);

    item.appendChild(titleEl);
    item.appendChild(document.createElement("br"));
    item.appendChild(statusRow);

    if (size) {
      const sizeEl = document.createElement("div");
      sizeEl.className = "doc-meta";
      sizeEl.textContent = size;
      item.appendChild(sizeEl);
    }

    if (uploadedAt) {
      const uploadedEl = document.createElement("div");
      uploadedEl.className = "doc-meta";
      uploadedEl.textContent = uploadedAt;
      item.appendChild(uploadedEl);
    }

    wrapper.appendChild(item);
  });

  documentsList.appendChild(wrapper);
}

function renderSearchResults(results) {
  if (!searchResults) return;

  searchResults.innerHTML = "";

  if (!results?.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "Ничего не найдено";
    searchResults.appendChild(empty);
    return;
  }

  const wrapper = document.createElement("div");
  wrapper.className = "search-grid";

  results.forEach((result) => {
    const item = document.createElement("div");
    item.className = "search-item";

    const title =
      result.document_name ||
      result.filename ||
      result.name ||
      `Документ #${result.document_id ?? result.id ?? ""}`;

    const snippet = result.snippet || result.text || result.content || "";
    const page = result.page != null ? `Страница: ${result.page}` : "";
    const score =
      result.score != null ? `Релевантность: ${Number(result.score).toFixed(3)}` : "";

    const titleEl = document.createElement("strong");
    titleEl.textContent = title;

    item.appendChild(titleEl);

    if (page || score) {
      const meta = document.createElement("div");
      meta.className = "doc-meta";
      meta.textContent = [page, score].filter(Boolean).join(" • ");
      item.appendChild(meta);
    }

    if (snippet) {
      const snippetEl = document.createElement("div");
      snippetEl.className = "search-snippet";
      snippetEl.textContent = snippet;
      item.appendChild(snippetEl);
    }

    wrapper.appendChild(item);
  });

  searchResults.appendChild(wrapper);
}

async function refreshDocuments() {
  if (!documentsList) return;

  const result = await loadDocuments();

  if (!result?.ok) {
    clearResults(documentsList, result?.message || "Не удалось загрузить документы");
    return;
  }

  renderDocuments(result.data || []);
  await refreshStatuses();
}

async function refreshStatuses() {
  if (!documentsList) return;

  const items = documentsList.querySelectorAll("[data-status-id]");

  for (const el of items) {
    const documentId = el.getAttribute("data-status-id");
    if (!documentId) continue;

    const statusResult = await getDocumentStatus(documentId);

    if (statusResult?.ok && statusResult.data?.status) {
      el.textContent = formatStatus(statusResult.data.status);
      el.className = `status-badge status-${String(statusResult.data.status).toLowerCase()}`;
    }
  }
}

async function handleAuthSubmit(event) {
  event.preventDefault();

  const username = $("username")?.value?.trim() || "";
  const password = $("password")?.value || "";
  const mode = getAuthMode();

  if (!username || !password) {
    setMessage(authMessage, "Введите логин и пароль", true);
    return;
  }

  setMessage(authMessage, "Выполняется вход...");

  const result =
    mode === "register"
      ? await handleRegister(username, password)
      : await handleLogin(username, password);

  if (!result?.ok) {
    setMessage(authMessage, result?.message || "Ошибка авторизации", true);
    return;
  }

  setMessage(
    authMessage,
    mode === "register" ? "Регистрация успешна" : "Вход выполнен успешно",
    false
  );

  showApp(true);
  await refreshDocuments();
}

async function handleUploadSubmit(event) {
  event.preventDefault();

  const files = pdfFilesInput?.files;

  if (!files || files.length === 0) {
    setMessage(uploadMessage, "Выберите PDF-файлы", true);
    return;
  }

  setMessage(uploadMessage, "Загрузка файлов...");

  const result = await uploadSelectedFiles(files);

  if (!result?.ok) {
    setMessage(uploadMessage, result?.message || "Не удалось загрузить файлы", true);
    return;
  }

  setMessage(uploadMessage, "Файлы успешно загружены");
  if (uploadForm) uploadForm.reset();

  await refreshDocuments();
}

async function handleSearchSubmit(event) {
  event.preventDefault();

  const query = $("search-query")?.value?.trim() || "";

  if (!query) {
    setMessage(searchMessage, "Введите поисковый запрос", true);
    return;
  }

  setMessage(searchMessage, "Поиск...");

  const result = await runSearch(query);

  if (!result?.ok) {
    setMessage(searchMessage, result?.message || "Ошибка поиска", true);
    clearResults(searchResults);
    return;
  }

  setMessage(searchMessage, "");
  const items = normalizeArray(result.data || result.results || result.payload);
  renderSearchResults(items);
}

function handleLogout() {
  clearToken();
  stopStatusTimer();
  showApp(false);

  setMessage(authMessage, "Вы вышли из системы");
  clearResults(documentsList, "Документы недоступны");
  clearResults(searchResults, "Результаты поиска недоступны");
  setMessage(uploadMessage, "");
  setMessage(searchMessage, "");
}

function startStatusTimer() {
  stopStatusTimer();
  statusRefreshTimer = window.setInterval(() => {
    if (isLoggedIn()) {
      refreshStatuses();
    }
  }, 15000);
}

function stopStatusTimer() {
  if (statusRefreshTimer) {
    window.clearInterval(statusRefreshTimer);
    statusRefreshTimer = null;
  }
}

async function initialize() {
  if (!authForm) return;

  setAuthMode("login");
  showApp(isLoggedIn());

  if (loginBtn) {
    loginBtn.addEventListener("click", () => setAuthMode("login"));
  }

  if (registerBtn) {
    registerBtn.addEventListener("click", () => setAuthMode("register"));
  }

  authForm.addEventListener("submit", handleAuthSubmit);

  if (uploadForm) {
    uploadForm.addEventListener("submit", handleUploadSubmit);
  }

  if (searchForm) {
    searchForm.addEventListener("submit", handleSearchSubmit);
  }

  if (refreshDocsBtn) {
    refreshDocsBtn.addEventListener("click", async () => {
      await refreshDocuments();
    });
  }

  if (logoutBtn) {
    logoutBtn.addEventListener("click", handleLogout);
  }

  if (isLoggedIn()) {
    await refreshDocuments();
    startStatusTimer();
  } else {
    clearResults(documentsList, "Авторизуйтесь, чтобы увидеть документы");
    clearResults(searchResults, "Авторизуйтесь, чтобы выполнять поиск");
  }
}

document.addEventListener("DOMContentLoaded", initialize);

