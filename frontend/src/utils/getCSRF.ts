const getCookie = (name: string): string | null => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(";").shift() || null;
  return null;
};

const setCookie = (name: string, value: string, days?: number) => {
  let expires = "";
  if (days) {
    const date = new Date();
    date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
    expires = `; expires=${date.toUTCString()}`;
  }
  document.cookie = `${name}=${value || ""}${expires}; path=/`;
};

export default async function getClientSideCSRF(): Promise<string | null> {
  const currentCSRF = getCookie("csrftoken");
  if (currentCSRF) return currentCSRF;

  // Make a request to the Django endpoint
  const response = await fetch(`${import.meta.env.VITE_API_URL}/ping/`);
  // Check if response is okay
  if (!response.ok) throw new Error("Failed to get CSRF token from server");
  // Extract the CSRF token from the response body
  const data = await response.json();
  const { csrfToken } = data;
  if (!csrfToken) {
    throw new Error("Failed to get CSRF token");
  }

  // Set new CSRF token as a cookie
  setCookie("csrftoken", csrfToken, 1); // The token will expire in 1 day

  return csrfToken;
}
