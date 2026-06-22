const API_BASE = (typeof window !== "undefined" && window.location.origin)
  ? `${window.location.origin}/api`
  : "http://localhost:8000/api";

function getToken() {
  return localStorage.getItem("token");
}

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  const token = getToken();

  if (token) {
    headers.set("X-User-Token", token);
    headers.set("Authorization", `Bearer ${token}`);
  }

  const resp = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  const contentType = resp.headers.get("content-type") || "";
  let data;
  if (contentType.includes("application/json")) {
    data = await resp.json();
  } else {
    data = await resp.text();
  }

  return { ok: resp.ok, status: resp.status, data };
}

export async function login(username, password) {
  return request("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
}

export async function register(username, password) {
  return request("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
}

export async function uploadDocuments(files) {
  const formData = new FormData();
  for (const file of files) {
    formData.append("files", file);
  }
  return request("/documents/", {
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
  return request(`/search/?query=${encodeURIComponent(query)}`, {
    method: "GET",
  });
}

export async function deleteDocument(id) {
  return request(`/documents/${id}`, { method: "DELETE" });
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
