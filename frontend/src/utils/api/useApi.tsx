import { useEffect, useState } from "react";
import { showNotification } from "@mantine/notifications";
import { IconX } from "@tabler/icons-react";

import { isApiError } from "./apiClient";

export type Params = { [name: string]: any };

export interface useApiProps<DataType> {
  apiFunc?: () => Promise<any>;
  unpackName: string;
  defaultData: DataType;
}

export interface useApiReturnType<DataType> {
  data: DataType;
  error: boolean;
  loading: boolean;
  refresh: () => void;
}

function useApi<DataType>({
  apiFunc,
  unpackName,
  defaultData,
}: useApiProps<DataType>): useApiReturnType<DataType> {
  const [data, setData] = useState<DataType>(defaultData);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(false);

  const request = async () => {
    try {
      if (apiFunc === undefined) return;
      setLoading(true);
      const res = await apiFunc();
      const data = res[unpackName] as DataType;
      setData(data);
      setError(false);
    } catch (e) {
      let errorMessage;
      if (isApiError(e)) {
        errorMessage = e.data;
      } else {
        // TODO: REPORT TO SENTRY
        console.error("An unexpected error occurred:", e);
      }
      setData(defaultData);
      setError(true);
      showNotification({
        message:
          typeof errorMessage === "string"
            ? errorMessage
            : "Error fetching data",
        color: "red",
        title: "Error",
        icon: <IconX size={18} />,
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    request();
  }, []);

  return {
    data,
    error,
    loading,
    refresh: request,
  };
}

export default useApi;
