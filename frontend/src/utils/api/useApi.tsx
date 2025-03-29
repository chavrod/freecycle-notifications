import { useEffect, useState } from "react";
import { showNotification } from "@mantine/notifications";
import { IconX } from "@tabler/icons-react";

import { isStandardApiError, convertArrayValuesToStrings } from "./apiClient";
import * as Sentry from "@sentry/react";
import { STANDARD_ERROR_MESSAGE } from "../constants";

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
    } catch (e: any) {
      let errorMessage;
      // TODO: Refacotor this logic and document...
      if (isStandardApiError(e)) {
        const tempMessage = convertArrayValuesToStrings(e.data);
        errorMessage =
          typeof tempMessage === "string"
            ? tempMessage
            : Object.values(tempMessage).join("; ");
      } else {
        Sentry.withScope((scope) => {
          scope.setContext("error_obj", e);
          Sentry.captureMessage(
            "useApi received non-standard Error",
            "warning"
          );
        });
        errorMessage = STANDARD_ERROR_MESSAGE;
      }
      setData(defaultData);
      setError(true);
      showNotification({
        message: errorMessage,
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
