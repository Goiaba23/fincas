import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import api from "@/lib/api";
import { useAuthStore } from "@/lib/store";

interface User {
  id: string;
  email: string;
  display_name: string;
  workspace_id?: string;
}

interface AuthContext {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContext | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [loading, setLoading] = useState(true);
  const { token, user, setAuth, logout: storeLogout } = useAuthStore();

  useEffect(() => {
    if (token && !user) {
      api
        .get("/api/v1/auth/me")
        .then((res) => setAuth(token, res.data))
        .catch(() => storeLogout())
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const res = await api.post("/api/v1/auth/login", { email, password });
    const { access_token } = res.data;
    const me = await api.get("/api/v1/auth/me");
    setAuth(access_token, me.data);
    localStorage.setItem("token", access_token);
  };

  const register = async (email: string, password: string, name: string) => {
    await api.post("/api/v1/auth/register", {
      email,
      password,
      display_name: name,
    });
  };

  const logout = () => {
    localStorage.removeItem("token");
    storeLogout();
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth outside AuthProvider");
  return ctx;
}
