"use client";

import { useCallback, useEffect, useState } from "react";
import { api, getToken, setToken } from "@/lib/api";

/**
 * Session vəziyyəti.
 *
 * `anon`  — token yoxdur (və ya etibarsızdır)
 * `user`  — giriş edib, amma admin deyil
 * `admin` — admin rolu var
 */
export type AuthStatus = "loading" | "anon" | "user" | "admin";

export interface AuthState {
  status: AuthStatus;
  isAdmin: boolean;
  /** Rolu `admin` olan istifadəçinin nickname-i (varsa). */
  nickname: string | null;
  /** Token mövcud deyil, amma status hələ yoxlanmayıb. */
  isLoading: boolean;
  /** Rolu dəyişdikdən sonra yenidən yoxlamağa məcbur edir. */
  refresh: () => void;
  logout: () => void;
}

/**
 * JWT tokenini yoxlayır və rolu müəyyən edir.
 *
 * Token `localStorage`-dadır, yəni yalnız mount-dan sonra oxuna bilər.
 * Buna görə ilk render "loading" qaytarır və həll **zaman aşımı
 * callback-i** daxilində aparılır — bu, effect gövdəsində birbaşa
 * `setState` çağırmadan (React 19 `set-state-in-effect` qaydası) qaçınır.
 */
export function useAuth(): AuthState {
  const [status, setStatus] = useState<AuthStatus>("loading");
  const [nickname, setNickname] = useState<string | null>(null);
  const [nonce, setNonce] = useState(0);

  const refresh = useCallback(() => setNonce((n) => n + 1), []);

  const logout = useCallback(() => {
    setToken(null);
    setStatus("anon");
    setNickname(null);
  }, []);

  useEffect(() => {
    if (!getToken()) {
      const t = setTimeout(() => setStatus("anon"), 0);
      return () => clearTimeout(t);
    }

    let cancelled = false;
    api
      .me()
      .then((res) => {
        if (cancelled) return;
        const role = res.user?.role;
        setNickname(res.user?.nickname ?? null);
        setStatus(role === "admin" ? "admin" : "user");
      })
      .catch(() => {
        if (cancelled) return;
        // Token etibarsızdır — təmizlə və anon qaytar
        setToken(null);
        setStatus("anon");
      });

    return () => {
      cancelled = true;
    };
  }, [nonce]);

  return {
    status,
    isAdmin: status === "admin",
    nickname,
    isLoading: status === "loading",
    refresh,
    logout,
  };
}
