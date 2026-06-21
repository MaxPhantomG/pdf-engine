import { login, register, saveToken, clearToken } from "./api.js";

export async function handleLogin(username, password) {
  const result = await login(username, password);
  console.log('[AUTH] handleLogin result', result);

  const token =
    result?.access_token ||
    result?.token ||
    result?.data?.access_token ||
    result?.data?.token;

  if (!token) {
    const detail =
      result?.data?.detail ??
      result?.data?.message ??
      "Ошибка входа";
    return { ok: false, message: detail };
  }

  saveToken(token);
  return { ok: true, message: "Вход выполнен" };
}

export async function handleRegister(username, password) {
  const result = await register(username, password);
  console.log('[AUTH] handleRegister result', result);

  if (result?.ok === false) {
    const detail = result?.data?.detail ?? result?.data?.message ?? "Ошибка регистрации";
    return { ok: false, message: detail };
  }

  return { ok: true, message: "Регистрация выполнена" };
}

export function logout() {
  clearToken();
}
