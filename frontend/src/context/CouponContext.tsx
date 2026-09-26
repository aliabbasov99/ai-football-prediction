"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  useSyncExternalStore,
  type ReactNode,
} from "react";
import { MAX_COUPON_ITEMS } from "@/constants";
import type { CouponSelection } from "@/components/couponUtils";

interface CouponContextValue {
  items: CouponSelection[];
  stake: number;
  isOpen: boolean;
  /** eyni açar varsa mövcudu silir, yoxdursa əlavə edir */
  toggle: (item: CouponSelection) => void;
  remove: (key: string) => void;
  clear: () => void;
  has: (key: string) => boolean;
  setStake: (value: number) => void;
  open: () => void;
  close: () => void;
}

const CouponContext = createContext<CouponContextValue | null>(null);

const STORAGE_KEY = "afp_coupon";
const STAKE_KEY = "afp_stake";

/**
 * Minimal `localStorage` store — `useSyncExternalStore` ilə oxunur.
 *
 * Niyə bu? Kupon və məqədədər yalnız brauzerdə mövcuddür, ona görə
 * `useState` + `useEffect` ilə oxumaq hydration uyğunsuzluğu yaradır və
 * React 19-un `set-state-in-effect` qaydasını pozmaq deməkdir.
 * `useSyncExternalStore` server snapshot verə bilər, `storage` hadisəsinə
 * abunə olur və tətbiqi tərəfdən də yazmağa imkan verir.
 */
function createLocalStore<T>(key: string, serverValue: T) {
  let value: T = serverValue;
  let raw: string | null = null;
  const listeners = new Set<() => void>();

  const emit = () => listeners.forEach((fn) => fn());

  const readStorage = (): T => {
    if (typeof window === "undefined") return serverValue;
    try {
      const next = window.localStorage.getItem(key);
      // Eyni dəyəri təkrar parse etmə (render loop-unun qarşısını alır)
      if (next === raw) return value;
      raw = next;
      value = next ? (JSON.parse(next) as T) : serverValue;
    } catch {
      value = serverValue;
    }
    return value;
  };

  return {
    subscribe(fn: () => void) {
      listeners.add(fn);
      // Digər tab-lar dəyişəndə habar ver
      if (typeof window !== "undefined") {
        window.addEventListener("storage", fn);
      }
      return () => {
        listeners.delete(fn);
        if (typeof window !== "undefined") {
          window.removeEventListener("storage", fn);
        }
      };
    },
    getSnapshot: readStorage,
    getServerSnapshot(): T {
      return serverValue;
    },
    set(next: T) {
      value = next;
      raw = JSON.stringify(next);
      if (typeof window !== "undefined") {
        try {
          window.localStorage.setItem(key, raw);
        } catch {
          /* kvota dolubsa səfirlə */
        }
      }
      emit();
    },
  };
}

const EMPTY_ITEMS: CouponSelection[] = [];
const itemsStore = createLocalStore<CouponSelection[]>(STORAGE_KEY, EMPTY_ITEMS);
const stakeStore = createLocalStore<number>(STAKE_KEY, 10);

export function CouponProvider({ children }: { children: ReactNode }) {
  const items = useSyncExternalStore(
    itemsStore.subscribe,
    itemsStore.getSnapshot,
    itemsStore.getServerSnapshot,
  );
  const stake = useSyncExternalStore(
    stakeStore.subscribe,
    stakeStore.getSnapshot,
    stakeStore.getServerSnapshot,
  );
  const [isOpen, setIsOpen] = useState(false);

  const setStake = useCallback((value: number) => {
    stakeStore.set(Number.isFinite(value) ? value : 10);
  }, []);

  const toggle = useCallback((item: CouponSelection) => {
    const prev = itemsStore.getSnapshot();
    const exists = prev.some((i) => i.key === item.key);
    if (exists) {
      itemsStore.set(prev.filter((i) => i.key !== item.key));
    } else if (prev.length < MAX_COUPON_ITEMS) {
      itemsStore.set([...prev, item]);
    }
    setIsOpen(true);
  }, []);

  const remove = useCallback((key: string) => {
    itemsStore.set(itemsStore.getSnapshot().filter((i) => i.key !== key));
  }, []);

  const clear = useCallback(() => itemsStore.set(EMPTY_ITEMS), []);

  const has = useCallback(
    (key: string) => items.some((i) => i.key === key),
    [items],
  );

  const value = useMemo<CouponContextValue>(
    () => ({
      items,
      stake,
      isOpen,
      toggle,
      remove,
      clear,
      has,
      setStake,
      open: () => setIsOpen(true),
      close: () => setIsOpen(false),
    }),
    [items, stake, isOpen, toggle, remove, clear, has, setStake],
  );

  return <CouponContext.Provider value={value}>{children}</CouponContext.Provider>;
}

export function useCoupon(): CouponContextValue {
  const ctx = useContext(CouponContext);
  if (!ctx) throw new Error("useCoupon must be used within <CouponProvider>");
  return ctx;
}
