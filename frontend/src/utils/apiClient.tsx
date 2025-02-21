type RequestOptions = Omit<RequestInit, "body"> & { body?: any };

interface ApiClient {
  get(url: string, config?: RequestOptions): Promise<any>;
  post(url: string, data: any, config?: RequestOptions): Promise<any>;
  patch(url: string, data: any, config?: RequestOptions): Promise<any>;
  delete(url: string, config?: RequestOptions): Promise<any>;
}

const createApiClient = (appPath?: string): ApiClient => {
  // /core/
  const BASE_URL = `${import.meta.env.VITE_API_URL}${appPath}`;

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
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || "Error fetching data");
    }

    return response.json();
  };

  return {
    get(url, config) {
      return request(url, { ...config, method: "GET" });
    },
    post(url, data, config) {
      return request(url, { ...config, method: "POST", body: data });
    },
    patch(url, data, config) {
      return request(url, { ...config, method: "POST", body: data });
    },
    delete(url, config) {
      return request(url, { ...config, method: "DELETE" });
    },
  };
};

export default createApiClient;
