import { useEffect, createContext, useState, ReactNode, FC } from "react";
import { getAuth, getConfig, Flows } from "./api";

interface AuthContextProviderProps {
  children: ReactNode;
}

// type FlowId = (typeof Flows)[keyof typeof Flows];
export type AuthFlow = {
  id: (typeof Flows)[keyof typeof Flows];
  is_pending: boolean;
};

export type User = {
  id: string;
  username: string;
  email: string;
};

export type AuthRes = {
  status: number;
  data: {
    flows?: AuthFlow[];
    user?: User;
    methods?: any;
    email?: string;
  };
  meta: {
    is_authenticated: boolean;
    access_token?: string;
  };
};

interface AuthContextType {
  auth?: AuthRes | null;
  config?: any;
}

export const AuthContext = createContext<AuthContextType | null>(null);

export const AuthContextProvider: FC<AuthContextProviderProps> = ({
  children,
}) => {
  console.log("AuthContextProvider render");
  const [auth, setAuth] = useState<AuthRes | null | undefined>(undefined);
  const [config, setConfig] = useState<any | null>(null);

  useEffect(() => {
    console.log("UseEffect triggered");
    function onAuthChanged(e: CustomEvent) {
      setAuth((auth: AuthRes | null | undefined) => {
        if (typeof auth === "undefined") {
          console.log("Authentication status loaded");
        } else {
          console.log("Authentication status updated");
        }
        return e.detail;
      });
    }

    document.addEventListener(
      "allauth.auth.change",
      onAuthChanged as EventListener
    );
    console.log("Getting getAuth...");
    getAuth()
      .then((data) => setAuth(data))
      .catch((e) => {
        console.error(e);
        setAuth(null);
      });
    console.log("Getting getConfig...");
    getConfig()
      .then((data) => setConfig(data))
      .catch((e) => {
        console.error(e);
      });
    return () => {
      document.removeEventListener(
        "allauth.auth.change",
        onAuthChanged as EventListener
      );
    };
  }, []);

  const loading = typeof auth === "undefined" || config?.status !== 200;

  return (
    <AuthContext.Provider value={{ auth, config }}>
      {loading ? (
        <div
          style={{
            height: "100vh",
            width: "100vw",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            backgroundColor: "rgba(196,213,191,255)",
          }}
        >
          <img
            src="/logo_main.svg"
            alt=""
            style={{
              width: "120px",
              height: "120px",
            }}
          ></img>
        </div>
      ) : (
        children
      )}
    </AuthContext.Provider>
  );
};
