import { handleLogin, handleRegister } from "./auth.js";
import { uploadSelectedFiles, loadDocuments } from "./documents.js";
import { searchDocuments } from "./api.js";
import { isLoggedIn, clearToken } from "./api.js";

const authForm = document.getElementById("auth-form");
const authMessage = document.getElementById("auth-message");
const logoutBtn = document.getElementById("logout-btn");
const uploadForm = document.getElementById("upload-form");
const uploadMessage = document.getElementById("upload-message");
const pdfFilesInput = document.getElementById("pdf-files");
const refreshDocsBtn = document.getElementById("refresh-docs-btn");
const documentsList = document.getElementById("documents-list");
const searchForm = document.getElementById("search-form");
const searchMessage = document.getElementById("search-message");

const authSection = document.getElementById("auth-section");
const appSection = document.getElementById("app-section");

function $(id) { return document.getElementById(id); }

function setMessage(element, text, isError = false) {
  if (!element) return;
  element.textContent = text || "";
  element.style.color = isError ? "#ff4d4f" : "#52c41a";
}

function showApp(isAuthenticated) {
  if (isAuthenticated) {
    authSection.classList.add("hidden");
    authSection.style.display = "none";
    appSection.classList.remove("hidden");
    appSection.style.display = "block";
  } else {
    authSection.classList.remove("hidden");
    authSection.style.display = "block";
    appSection.classList.add("hidden");
    appSection.style.display = "none";
  }
}

async function refreshDocuments() {
  if (!documentsList) return;
  documentsList.innerHTML = "Загрузка...";

  const result = await loadDocuments();

  if (!result?.ok) {
    documentsList.innerHTML = `<div class="empty-state">${result?.data?.detail || "Ошибка доступа"}</div>`;
    return;
  }

  renderDocuments(result.data || []);
}

function renderDocuments(documents) {
  if (!documentsList) return;
  documentsList.innerHTML = "";

  if (!documents || documents.length === 0) {
    documentsList.innerHTML = '<div class="empty-state">У вас пока нет документов.</div>';
    return;
  }

  const wrapper = document.createElement("div");
  wrapper.className = "documents-grid";

  documents.forEach((doc) => {
    const item = document.createElement("div");
    item.className = "doc-item";
    item.innerHTML = `
      <div class="doc-info">
        <strong>${doc.name || 'Без названия'}</strong>
        <div class="doc-meta">Статус: <span class="badge">${doc.status}</span></div>
      </div>
      <div class="doc-actions">
        <button class="delete-btn" data-id="${doc.id}">Удалить</button>
      </div>
    `;
    
    // Навешиваем событие на кнопку удаления
    item.querySelector(".delete-btn").onclick = async (e) => {
        if(confirm("Удалить этот документ?")) {
            await deleteDocument(doc.id);
            refreshDocuments(); // Обновляем список
        }
    };

    wrapper.appendChild(item);
  });

  documentsList.appendChild(wrapper);
}

// ГЛАВНЫЙ ОБРАБОТЧИК ФОРМЫ
async function handleAuthSubmit(event) {
  event.preventDefault();
  
  const mode = event.submitter && event.submitter.id === "register-btn" ? "register" : "login";
  
  const username = $("username")?.value?.trim();
  const password = $("password")?.value;

  if (!username || !password) {
    setMessage(authMessage, "Заполните все поля", true);
    return;
  }

  setMessage(authMessage, mode === "register" ? "Регистрация..." : "Вход...");

  const result = mode === "register" 
    ? await handleRegister(username, password)
    : await handleLogin(username, password);

  if (result.ok) {
    setMessage(authMessage, "Успешно!");
    if (mode === "login") {
      showApp(true);
      await refreshDocuments();
    }
  } else {
    setMessage(authMessage, result.message || "Ошибка", true);
  }
}

async function handleUploadSubmit(event) {
  event.preventDefault();
  const files = pdfFilesInput?.files;
  if (!files || files.length === 0) return setMessage(uploadMessage, "Файлы не выбраны", true);

  setMessage(uploadMessage, "Загрузка...");
  const result = await uploadSelectedFiles(files);
  
  if (result.ok) {
    setMessage(uploadMessage, "Загружено успешно");
    uploadForm.reset();
    await refreshDocuments();
  } else {
    setMessage(uploadMessage, "Ошибка загрузки", true);
  }
}

function handleLogout() {
  clearToken();
  showApp(false);
  if (authForm) authForm.reset();
  setMessage(authMessage, "Вы вышли");
}

function initialize() {
  if (!authForm) return;

  // 1. Проверка авторизации при загрузке
  const authStatus = isLoggedIn();
  showApp(authStatus);
  if (authStatus) refreshDocuments();

  // 2. Слушатели событий
  authForm.addEventListener("submit", handleAuthSubmit);
  
  if (uploadForm) uploadForm.addEventListener("submit", handleUploadSubmit);
  
  if (refreshDocsBtn) refreshDocsBtn.onclick = refreshDocuments;
  
  if (logoutBtn) logoutBtn.onclick = handleLogout;

  if (searchForm) {
    searchForm.onsubmit = async (e) => {
        e.preventDefault();
        const q = $("search-query").value;
        setMessage(searchMessage, "Поиск по: " + q);
    };
  }
}

initialize();
