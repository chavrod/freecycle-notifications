import { STANDARD_ERROR_MESSAGE } from "../constants";

type RequestOptions = Omit<RequestInit, "body"> & { body?: any };

interface ApiClient {
  get(url: string, config?: RequestOptions): Promise<any>;
  post(url: string, data: any, config?: RequestOptions): Promise<any>;
  delete(url: string, config?: RequestOptions): Promise<any>;
}

export type ApiError = {
  data: object | string;
  statusCode: number;
};

export function isApiError(error: any): error is ApiError {
  return (
    error &&
    (typeof error.data === "object" || typeof error.data === "string") &&
    typeof error.statusCode === "number"
  );
}

const createApiClient = (appPath?: string): ApiClient => {
  const BASE_URL = `${import.meta.env.VITE_API_URL}/${appPath || ""}`;

  const request = async (
    url: string,
    options: RequestOptions = {}
  ): Promise<any> => {
    const { body, ...rest } = options;
    const headers = {
      "Content-Type": "application/json",
      ...rest.headers,
    };
    const response = await fetch(`${BASE_URL}${url}`, {
      ...rest,
      body: body ? JSON.stringify(body) : undefined,
      headers,
      credentials: "include",
    });

    if (!response.ok) {
      let errorData = null;
      try {
        errorData = await response.json();
      } catch {
        // TODO: REPORT TO SENTRY
        errorData = STANDARD_ERROR_MESSAGE;
      }
      throw {
        data: errorData,
        statusCode: response.status,
      };
    }

    return await response.json();
  };

  return {
    get(url, config) {
      return request(url, { ...config, method: "GET" });
    },
    post(url, data, config) {
      return request(url, { ...config, method: "POST", body: data });
    },
    delete(url, config) {
      return request(url, { ...config, method: "DELETE" });
    },
  };
};

export default createApiClient;
