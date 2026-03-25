"use client";

import {
  ReactNode,
  useState,
  useEffect,
  createContext,
  useContext,
} from "react";
import { User, UserRole } from "@/lib/types/auth";
import { jwtDecode } from "jwt-decode";

interface AuthContextType {
  isAuthenticated: boolean;
  token: string | null;
  user: User | null;
  login: (token: string) => void;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Load token from localStorage
    const savedToken = localStorage.getItem("token");
    if (savedToken) {
      try {
        const decoded: any = jwtDecode(savedToken);
        // Check expiry
        const currentTime = Date.now() / 1000;
        if (decoded.exp < currentTime) {
          handleLogout();
        } else {
          setToken(savedToken);
          // In a real app, you might fetch user info here or decode it from JWT
          setUser({
            id: decoded.sub || "",
            email: decoded.email || "",
            role: (decoded.role as UserRole) || "DOCTOR",
          });
        }
      } catch (error) {
        console.error("Invalid token", error);
        handleLogout();
      }
    }
    setIsLoading(false);
  }, []);

  const handleLogin = (newToken: string) => {
    setToken(newToken);
    localStorage.setItem("token", newToken);
    try {
      const decoded: any = jwtDecode(newToken);
      setUser({
        id: decoded.sub || "",
        email: decoded.email || "",
        role: (decoded.role as UserRole) || "DOCTOR",
      });
    } catch (error) {
      console.error("Error decoding token during login", error);
    }
  };

  const handleLogout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("token");
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated: !!token,
        token,
        user,
        login: handleLogin,
        logout: handleLogout,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
