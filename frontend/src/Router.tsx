import { useState, useEffect } from "react";
import {
  AuthChangeRedirector,
  AnonymousRoute,
  AuthenticatedRoute,
} from "./auth/routing";
import {
  createBrowserRouter,
  RouterProvider,
  DataRouter,
} from "react-router-dom";
import Login from "./account/Login";
// import Logout from "./account/Logout";
import Signup from "./account/Signup";
import VerifyEmail, {
  loader as verifyEmailLoader,
} from "./account/VerifyEmail";
import VerificationEmailSent from "./account/VerificationEmailSent";
import RequestPasswordReset from "./account/RequestPasswordReset";
// import ChangePassword from "./account/ChangePassword";
import ResetPassword, {
  loader as resetPasswordLoader,
} from "./account/ResetPassword";
import Root from "./Root";
import Home from "./Home";
import { useConfig } from "./auth/hooks";
import ErrorBoundary from "./components/ErrorBoundary";
import ManageChats from "./settings/ManageChats";

function createRouter() {
  return createBrowserRouter([
    {
      path: "/",
      element: (
        <AuthChangeRedirector>
          <Root />
        </AuthChangeRedirector>
      ),
      errorElement: <ErrorBoundary />,
      children: [
        {
          path: "/",
          element: <Home />,
        },
        {
          path: "manage-chats",
          element: (
            <AuthenticatedRoute>
              <ManageChats />
            </AuthenticatedRoute>
          ),
        },
        {
          path: "/account/login",
          element: (
            <AnonymousRoute>
              <Login />
            </AnonymousRoute>
          ),
        },
        {
          path: "/account/signup",
          element: (
            <AnonymousRoute>
              <Signup />
            </AnonymousRoute>
          ),
        },
        {
          path: "/account/verify-email",
          element: <VerificationEmailSent />,
        },
        {
          path: "/account/verify-email/:key",
          element: <VerifyEmail />,
          loader: verifyEmailLoader,
        },
        {
          path: "/account/password/reset",
          element: (
            <AnonymousRoute>
              <RequestPasswordReset />
            </AnonymousRoute>
          ),
        },
        {
          path: "/account/password/key/:key",
          element: (
            <AnonymousRoute>
              <ResetPassword />
            </AnonymousRoute>
          ),
          loader: resetPasswordLoader,
        },
      ],
    },
  ]);
}

export default function RouterFn() {
  // If we create the router globally, the loaders of the routes already trigger
  // even before the <AuthContext/> trigger the initial loading of the auth.
  // state.
  const [router, setRouter] = useState<DataRouter | null>(null);
  const config = useConfig();
  useEffect(() => {
    setRouter(createRouter());
  }, [config]);
  return router ? <RouterProvider router={router} /> : null;
}
