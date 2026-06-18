const API_BASE = "http://localhost:8000";

function getToken() {
  return localStorage.getItem("token");
}

async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = getToken();

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`APIBASE{API_BASE}APIB​ASE{path}`, {
    ...options,
    headers,
  });

  const contentType = response.headers.get("content-type") || "";

  if (contentType.includes("application/json")) {
    const data = await response.json();
    return { ok: response.ok, status: response.status, data };
  }

  const text = await response.text();
  return { ok: response.ok, status: response.status, data: text };
}

export async function login(username, password) {
  return request("/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });
}

export async function register(username, password) {
  return request("/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  });
}

export async function uploadDocuments(files) {
  const formData = new FormData();

  for (const file of files) {
    formData.append("files", file);
  }

  return request("/documents/upload", {
    method: "POST",
    body: formData,
  });
}

export async function fetchDocuments() {
  return request("/documents");
}

export async function fetchDocumentStatus(documentId) {
  return request(`/documents/${documentId}/status`);
}

export async function searchDocuments(query) {
  return request("/search", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query }),
  });
}

export function saveToken(token) {
  localStorage.setItem("token", token);
}

export function clearToken() {
  localStorage.removeItem("token");
}

export function isLoggedIn() {
  return Boolean(getToken());
}

