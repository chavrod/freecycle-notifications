import getClientSideCSRF from "../utils/getCSRF";

const BASE_URL = `${import.meta.env.VITE_API_URL}/users/_allauth/browser/v1`;

console.log("BASE_URL: ", BASE_URL);

export const AuthProcess = Object.freeze({
  LOGIN: "login",
  CONNECT: "connect",
});

export const Flows = Object.freeze({
  VERIFY_EMAIL: "verify_email",
  LOGIN: "login",
  SIGNUP: "signup",
});

export const URLs = Object.freeze({
  // Meta
  CONFIG: BASE_URL + "/config",

  // Account management
  CHANGE_PASSWORD: BASE_URL + "/account/password/change",
  EMAIL: BASE_URL + "/account/email",

  // Auth: Basics
  LOGIN: BASE_URL + "/auth/login",
  SESSION: BASE_URL + "/auth/session",
  REQUEST_PASSWORD_RESET: BASE_URL + "/auth/password/request",
  RESET_PASSWORD: BASE_URL + "/auth/password/reset",
  SIGNUP: BASE_URL + "/auth/signup",
  VERIFY_EMAIL: BASE_URL + "/auth/email/verify",
});

// // Define the interface for a successful response (HTTP 200)
// type SuccessResponse = {
//   status: 200;
//   data: {
//     email: string;
//     user: {
//       id: number;
//       display: string;
//       has_usable_password: boolean;
//       email: string;
//       username: string;
//     };
//   };
//   meta: {
//     is_authenticating: boolean;
//   };
// };

// // Define the interface for a client error response (HTTP 400)
// type ErrorResponse = {
//   status: 400;
//   errors: Array<{
//     message: string;
//     code: string;
//     param: string;
//   }>;
// };

async function request(
  method: string,
  path: string,
  data?: any,
  headers?: any
) {
  const options: any = {
    method,
    headers: {
      ...headers,
    },
    credentials: "include",
  };

  // Don't pass along authentication related headers to the config endpoint.
  if (path !== URLs.CONFIG) {
    options.headers["X-CSRFToken"] = await getClientSideCSRF();
  }

  if (typeof data !== "undefined") {
    options.body = JSON.stringify(data);
    options.headers["Content-Type"] = "application/json";
  }

  const resp = await fetch(path, options);
  let msg;
  try {
    msg = await resp.json();
  } catch {
    msg = {
      status: 500,
      errors: [
        {
          message: "Server Error. Please try again later",
        },
      ],
      meta: { is_authenticated: null },
    };
  }
  if (msg.status == 401 || (msg.status === 200 && msg.meta?.is_authenticated)) {
    const event = new CustomEvent("allauth.auth.change", { detail: msg });
    document.dispatchEvent(event);
  }
  return msg;
}

export async function getConfig() {
  return await request("GET", URLs.CONFIG);
}

export async function getAuth() {
  return await request("GET", URLs.SESSION);
}

export async function login(data: any) {
  return await request("POST", URLs.LOGIN, data);
}

export async function logout() {
  return await request("DELETE", URLs.SESSION);
}

export async function signUp(data: any) {
  return await request("POST", URLs.SIGNUP, data);
}

export async function requestPasswordReset(email: any) {
  return await request("POST", URLs.REQUEST_PASSWORD_RESET, { email });
}

export async function getPasswordReset(key: any) {
  return await request("GET", URLs.RESET_PASSWORD, undefined, {
    "X-Password-Reset-Key": key,
  });
}

export async function resetPassword(data: any) {
  return await request("POST", URLs.RESET_PASSWORD, data);
}

export async function verifyEmail(key: any) {
  return await request("POST", URLs.VERIFY_EMAIL, { key });
}

export async function getEmailVerification(key: any) {
  return await request("GET", URLs.VERIFY_EMAIL, undefined, {
    "X-Email-Verification-Key": key,
  });
}

interface ErrorObject {
  message: string;
  code: string;
  param: string;
}
type CustomMapping = Record<string, string>;

export function formatAuthErrors(
  errorList: ErrorObject[],
  customMapping: CustomMapping = {}
): Record<string, string> {
  const formattedErrors: Record<string, string> = {};

  errorList.forEach((error) => {
    const { message, param } = error;
    // Use the custom mapping to determine the correct key, otherwise use the original param
    const key = customMapping[param] || param;

    if (formattedErrors[key]) {
      formattedErrors[key] += `; ${message}`;
    } else {
      formattedErrors[key] = message;
    }
  });

  return formattedErrors;
}
