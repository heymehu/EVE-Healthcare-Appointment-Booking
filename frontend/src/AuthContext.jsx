import { createContext, useContext, useMemo, useState } from "react";
import { AuthAPI } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("eve_token"));
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("eve_user");
    return raw ? JSON.parse(raw) : null;
  });

  const persist = (nextToken, nextUser) => {
    setToken(nextToken);
    setUser(nextUser);
    if (nextToken) localStorage.setItem("eve_token", nextToken);
    else localStorage.removeItem("eve_token");
    if (nextUser) localStorage.setItem("eve_user", JSON.stringify(nextUser));
    else localStorage.removeItem("eve_user");
  };

  const value = useMemo(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token),
      async signup(payload) {
        await AuthAPI.signup(payload);
        const data = await AuthAPI.login({ email: payload.email, password: payload.password });
        persist(data.access_token, data.user);
        return data;
      },
      async login(payload) {
        const data = await AuthAPI.login(payload);
        persist(data.access_token, data.user);
        return data;
      },
      logout() {
        persist(null, null);
      },
    }),
    [token, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}
