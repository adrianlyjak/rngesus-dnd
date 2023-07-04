import { useState, useEffect } from "react";

export interface HashParams {
  get isLoaded(): boolean;
  get(key: string): string | null;
  set(key: string, value: string | null): void;
}

export default function hashparams(): HashParams {
  const [params, setParams] = useState(new URLSearchParams());
  const [isLoaded, setIsLoaded] = useState(false);
  useEffect(() => {
    const cb = setParams;
    setIsLoaded(true);
    setParams(parseHashParams());
    Listener.addEventListener(cb);
    return () => Listener.removeEventListener(cb);
  }, []);

  return {
    get isLoaded(): boolean {
      return isLoaded;
    },
    get: (key: string) => params.get(key),
    set: (key: string, value: string | null) => {
      const params = parseHashParams();
      if (value === null) {
        params.delete(key);
      } else {
        params.set(key, value);
      }
      setHashParams(params);
    },
  };
}

function parseHashParams(): URLSearchParams {
  const hash = window.location.hash.replace(/^#/, "");
  return new URLSearchParams(hash);
}

function setHashParams(params: URLSearchParams): void {
  window.location.hash = params.toString();
}

interface SearchParamsEmitter {
  addEventListener(callback: (params: URLSearchParams) => void): void;
  removeEventListener(callback: (params: URLSearchParams) => void): void;
}
const Listener: SearchParamsEmitter = (() => {
  const callbackConversions = new Map<any, any>();
  return {
    addEventListener(callback: (params: URLSearchParams) => void): void {
      const rawCallback = () => callback(parseHashParams());
      callbackConversions.set(callback, rawCallback);
      window.addEventListener("hashchange", rawCallback);
    },
    removeEventListener(callback: (params: URLSearchParams) => void): void {
      const rawCallabck = callbackConversions.get(callback);
      if (rawCallabck) {
        window.removeEventListener("hashchange", rawCallabck);
      }
    },
  };
})();
