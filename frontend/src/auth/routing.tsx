import { Navigate, useLocation } from "react-router-dom";
import { useAuthChange, AuthChangeEvent, useAuthStatus } from "./hooks";
import { Flows } from "./api";
import { AuthRes, AuthFlow } from "./AuthContext";

export const URLs = Object.freeze({
  LOGIN_URL: "/account/login",
  LOGIN_REDIRECT_URL: "/",
  LOGOUT_REDIRECT_URL: "/",
});

export const Flow2Path = Object.freeze({
  [Flows.LOGIN]: "/account/login",
  [Flows.SIGNUP]: "/account/signup",
  [Flows.VERIFY_EMAIL]: "/account/verify-email",
});

export function pathForFlow(flow?: AuthFlow) {
  if (!flow) {
    throw new Error("No flow provided");
  }

  const path = Flow2Path[flow.id];
  if (path === undefined) {
    throw new Error(`Unknown path for flow: ${flow.id}`);
  }
  return path;
}

export function AuthenticatedRoute({
  children,
}: {
  children: React.ReactNode;
}) {
  const location = useLocation();
  const [, status] = useAuthStatus();
  const next = `next=${encodeURIComponent(
    location.pathname + location.search
  )}`;

  if (status?.isAuthenticated) {
    return children;
  } else {
    return <Navigate to={`${URLs.LOGIN_URL}?${next}`} />;
  }
}

export function AnonymousRoute({ children }: { children: React.ReactNode }) {
  const [, status] = useAuthStatus();
  if (!status.isAuthenticated) {
    return children;
  } else {
    return <Navigate to={URLs.LOGIN_REDIRECT_URL} />;
  }
}

// Define a type guard for AuthRes
function isAuthRes(auth: any): auth is AuthRes {
  return (
    auth && typeof auth === "object" && "data" in auth && "flows" in auth.data
  );
}

export function AuthChangeRedirector({
  children,
}: {
  children: React.ReactNode;
}) {
  const [auth, event] = useAuthChange();
  const location = useLocation();
  switch (event) {
    case AuthChangeEvent.LOGGED_OUT:
      return <Navigate to={URLs.LOGOUT_REDIRECT_URL} />;
    case AuthChangeEvent.LOGGED_IN:
      return <Navigate to={URLs.LOGIN_REDIRECT_URL} />;
    case AuthChangeEvent.REAUTHENTICATION_REQUIRED: {
      // Use the custom type guard
      if (!isAuthRes(auth)) {
        throw new Error(
          "Expected auth to be AuthRes but got an unexpected value."
        );
      }

      const next = `next=${encodeURIComponent(
        location.pathname + location.search
      )}`;
      const path = pathForFlow(auth.data.flows?.[0]);
      return <Navigate to={`${path}?${next}`} state={{ reauth: auth }} />;
    }
    default:
      break;
  }
  // ...stay where we are
  return children;
}
