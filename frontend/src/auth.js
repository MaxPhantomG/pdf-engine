import { login, register, saveToken, clearToken } from "./api.js";

export async function handleLogin(username, password) {
  const result = await login(username, password);

  if (!result.ok) {
    return {
      ok: false,
      message: result.data?.detail || "Ошибка входа",
    };
  }

  const token = result.data?.access_token || result.data?.token;

  if (!token) {
    return {
      ok: false,
      message: "Токен не был получен от сервера",
    };
  }

  saveToken(token);

  return {
    ok: true,
    message: "Вход выполнен",
  };
}

export async function handleRegister(username, password) {
  const result = await register(username, password);

  if (!result.ok) {
    return {
      ok: false,
      message: result.data?.detail || "Ошибка регистрации",
    };
  }

  return {
    ok: true,
    message: "Регистрация выполнена",
  };
}

export function logout() {
  clearToken();
}

