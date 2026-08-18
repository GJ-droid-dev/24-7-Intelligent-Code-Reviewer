"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import {
  signInWithPopup,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut as fbSignOut,
  onAuthStateChanged,
  User as FirebaseUser,
} from "firebase/auth";
import { auth, googleProvider } from "./firebase";
import { UserProfile } from "./types";

interface AuthContextType {
  user: UserProfile | null;
  loading: boolean;
  signInWithGoogle: () => Promise<void>;
  signInWithEmail: (email: string, pass: string) => Promise<void>;
  signUpWithEmail: (email: string, pass: string) => Promise<void>;
  signInDemo: () => void;
  signOut: () => Promise<void>;
  getIdToken: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  signInWithGoogle: async () => {},
  signInWithEmail: async () => {},
  signUpWithEmail: async () => {},
  signInDemo: () => {},
  signOut: async () => {},
  getIdToken: async () => null,
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    // Check for demo user in localStorage
    const savedDemoUser = localStorage.getItem("demo_user_session");
    if (savedDemoUser) {
      try {
        setUser(JSON.parse(savedDemoUser));
        setLoading(false);
        return;
      } catch {
        localStorage.removeItem("demo_user_session");
      }
    }

    if (!auth) {
      setLoading(false);
      return;
    }

    const unsubscribe = onAuthStateChanged(auth, (fbUser: FirebaseUser | null) => {
      if (fbUser) {
        setUser({
          uid: fbUser.uid,
          email: fbUser.email,
          displayName: fbUser.displayName || fbUser.email?.split("@")[0] || "Developer",
          photoURL: fbUser.photoURL,
          isDemo: false,
        });
      } else {
        const demo = localStorage.getItem("demo_user_session");
        if (demo) {
          try {
            setUser(JSON.parse(demo));
          } catch {
            setUser(null);
          }
        } else {
          setUser(null);
        }
      }
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const signInWithGoogle = async () => {
    try {
      if (!auth) throw new Error("Firebase Auth not initialized");
      const result = await signInWithPopup(auth, googleProvider);
      const fbUser = result.user;
      localStorage.removeItem("demo_user_session");
      setUser({
        uid: fbUser.uid,
        email: fbUser.email,
        displayName: fbUser.displayName,
        photoURL: fbUser.photoURL,
        isDemo: false,
      });
    } catch (err: unknown) {
      console.error("Google Sign-In Error:", err);
      throw err;
    }
  };

  const signInWithEmail = async (email: string, pass: string) => {
    if (!auth) throw new Error("Firebase Auth not initialized");
    const result = await signInWithEmailAndPassword(auth, email, pass);
    const fbUser = result.user;
    localStorage.removeItem("demo_user_session");
    setUser({
      uid: fbUser.uid,
      email: fbUser.email,
      displayName: fbUser.displayName || fbUser.email?.split("@")[0] || "Developer",
      photoURL: fbUser.photoURL,
      isDemo: false,
    });
  };

  const signUpWithEmail = async (email: string, pass: string) => {
    if (!auth) throw new Error("Firebase Auth not initialized");
    const result = await createUserWithEmailAndPassword(auth, email, pass);
    const fbUser = result.user;
    localStorage.removeItem("demo_user_session");
    setUser({
      uid: fbUser.uid,
      email: fbUser.email,
      displayName: fbUser.email?.split("@")[0] || "Developer",
      isDemo: false,
    });
  };

  const signInDemo = () => {
    const demoUser: UserProfile = {
      uid: "test-user-001",
      email: "senior.reviewer@acme.dev",
      displayName: "Alex Rivera (Staff Eng)",
      isDemo: true,
    };
    localStorage.setItem("demo_user_session", JSON.stringify(demoUser));
    setUser(demoUser);
  };

  const signOut = async () => {
    localStorage.removeItem("demo_user_session");
    if (auth) {
      await fbSignOut(auth);
    }
    setUser(null);
  };

  const getIdToken = async (): Promise<string | null> => {
    if (user?.isDemo) {
      return "mock-test-token-test-user-001";
    }
    if (auth?.currentUser) {
      return await auth.currentUser.getIdToken();
    }
    return null;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        signInWithGoogle,
        signInWithEmail,
        signUpWithEmail,
        signInDemo,
        signOut,
        getIdToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
