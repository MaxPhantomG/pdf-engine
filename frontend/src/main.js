import { handleLogin, handleRegister } from "./auth.js";
import { uploadSelectedFiles, loadDocuments } from "./documents.js";
import { searchDocuments } from "./api.js";
import { isLoggedIn, clearToken } from "./api.js";

// ========== ЭЛЕМЕНТЫ DOM ==========
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
const searchQuery = document.getElementById("search-query");

const authSection = document.getElementById("auth-section");
const appSection = document.getElementById("app-section");


const modal = document.getElementById('document-modal');
const modalOverlay = modal?.querySelector('.modal-overlay');
const modalClose = document.getElementById('modal-close');
const modalDocumentName = document.getElementById('modal-document-name');
const modalDocumentContent = document.getElementById('modal-document-content');
const modalSearchForm = document.getElementById('modal-search-form');
const modalSearchQuery = document.getElementById('modal-search-query');
const modalSearchMessage = document.getElementById('modal-search-message');
const modalSearchResults = document.getElementById('modal-search-results');

let currentDocumentId = null;

// ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
function $(id) { return document.getElementById(id); }

function setMessage(element, text, isError = false) {
  if (!element) return;
  element.textContent = text || "";
  element.style.color = isError ? "#ff4d4f" : "#52c41a";
}

function showApp(isAuthenticated) {
  if (!authSection || !appSection) return;
  
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


function openDocumentModal(documentId, documentName) {
  if (!modal) {
    console.error('Модальное окно не найдено в HTML');
    return;
  }
  
  currentDocumentId = documentId;
  if (modalDocumentName) modalDocumentName.textContent = documentName;
  modal.classList.remove('hidden');
  
  // Загружаем содержимое документа
  loadDocumentContent(documentId);
}

// Функция закрытия модального окна
function closeDocumentModal() {
  // ✅ Безопасная проверка
  if (!modal) return;
  
  modal.classList.add('hidden');
  currentDocumentId = null;
  if (modalDocumentContent) modalDocumentContent.innerHTML = '';
  if (modalSearchResults) modalSearchResults.innerHTML = '';
  if (modalSearchMessage) modalSearchMessage.textContent = '';
}

// Загрузка содержимого документа
async function loadDocumentContent(documentId) {
  if (!modalDocumentContent) return;
  
  modalDocumentContent.innerHTML = '<p>Загрузка...</p>';
  
  // ❗❗❗ ВАЖНО: fetchDocumentContent нужно добавить в api.js
  // Временно делаем через fetch напрямую
  const token = localStorage.getItem('token');
  const response = await fetch(`/api/documents/${documentId}/content`, {
    headers: {
      'X-User-Token': token || ''
    }
  });
  
  const result = response.ok ? { ok: true, data: await response.json() } : { ok: false, data: await response.json() };
  
  if (!result.ok) {
    modalDocumentContent.innerHTML = `<p class="error">Ошибка загрузки: ${result.data?.detail || 'Неизвестная ошибка'}</p>`;
    return;
  }
  
  const content = result.data.content || 'Документ пуст';
  modalDocumentContent.innerHTML = content;
}


async function searchInDocumentHandler(e) {
  e.preventDefault();
  
  const query = modalSearchQuery?.value?.trim();
  if (!query) return;
  
  if (modalSearchMessage) modalSearchMessage.textContent = 'Поиск...';
  if (modalSearchResults) modalSearchResults.innerHTML = '';

  const token = localStorage.getItem('token');
  const response = await fetch(`/api/documents/${currentDocumentId}/search?q=${encodeURIComponent(query)}`, {
    headers: {
      'X-User-Token': token || ''
    }
  });
  
  const result = response.ok ? { ok: true, data: await response.json() } : { ok: false, data: await response.json() };
  
  if (!result.ok) {
    if (modalSearchMessage) {
      modalSearchMessage.textContent = `Ошибка: ${result.data?.detail || 'Неизвестная ошибка'}`;
      modalSearchMessage.className = 'message error';
    }
    return;
  }
  
  if (modalSearchMessage) {
    modalSearchMessage.textContent = `Найдено совпадений: ${result.data.total_matches}`;
    modalSearchMessage.className = 'message success';
  }

  const matches = result.data.matches || [];
  if (modalSearchResults) {
    modalSearchResults.innerHTML = matches.map((match, index) => `
      <div class="snippet" data-position="${match.position}">
        <strong>Совпадение #${index + 1}:</strong>
        <br>
        <span>${escapeHtml(match.snippet)}</span>
      </div>
    `).join('');
  }
  
  highlightMatches(query);
}

function highlightMatches(query) {
  if (!modalDocumentContent) return;
  
  const content = modalDocumentContent.textContent;
  const queryLower = query.toLowerCase();
  
  const highlighted = content.replace(
    new RegExp(`(${escapeRegExp(query)})`, 'gi'),
    '<span class="highlight">$1</span>'
  );
  
  modalDocumentContent.innerHTML = highlighted;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
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
    
    const viewButtonHtml = modal 
      ? `<button class="view-btn" data-id="${doc.id}" data-name="${doc.name}">Просмотр</button>`
      : '';
    
    item.innerHTML = `
      <div class="doc-info">
        <strong>${doc.name || 'Без названия'}</strong>
        <div class="doc-meta">Статус: <span class="badge">${doc.status}</span></div>
      </div>
      <div class="doc-actions">
        ${viewButtonHtml}
        <button class="delete-btn" data-id="${doc.id}">Удалить</button>
      </div>
    `;
    
    const viewBtn = item.querySelector(".view-btn");
    if (viewBtn) {
      viewBtn.onclick = () => openDocumentModal(doc.id, doc.name);
    }
    
    // Обработчик кнопки удаления
    item.querySelector(".delete-btn").onclick = async (e) => {
      if(confirm("Удалить этот документ?")) {
        await deleteDocument(doc.id);
        refreshDocuments();
      }
    };

    wrapper.appendChild(item);
  });

  documentsList.appendChild(wrapper);
}

// ========== ОБРАБОТЧИКИ ФОРМ ==========
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

// ========== ИНИЦИАЛИЗАЦИЯ ==========
function initialize() {
  if (!authForm) {
    console.error('Форма авторизации не найдена');
    return;
  }

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
      const q = searchQuery?.value;
      if (q) {
        setMessage(searchMessage, "Поиск по: " + q);
      }
    };
  }

  if (modal) {
    // Закрытие по кнопке
    if (modalClose) {
      modalClose.onclick = closeDocumentModal;
    }
    
    // Закрытие по клику на overlay
    if (modalOverlay) {
      modalOverlay.onclick = closeDocumentModal;
    }
    
    // Закрытие по Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
        closeDocumentModal();
      }
    });
    
    // Форма поиска в модальном окне
    if (modalSearchForm) {
      modalSearchForm.onsubmit = searchInDocumentHandler;
    }
  } else {
    console.warn('Модальное окно не найдено. Функционал просмотра документов недоступен.');
  }
}

initialize();
