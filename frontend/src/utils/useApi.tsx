import { useState } from "react";
import { showNotification } from "@mantine/notifications";

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
    if (apiFunc === undefined) return;
    setLoading(true);
    const res = await apiFunc();
    setLoading(false);
    if (res.ok) {
      const data = res.data as { [unpackName: string]: DataType };
      const unpacked = data[unpackName];
      setData(unpacked);
      setError(false);
    } else {
      showNotification({
        message: capitalize(res.problem.replaceAll("_", " ")),
        color: "red",
        title: "Error",
        icon: <IconX size={18} />,
      });
      setData(defaultData);
      setError(true);
    }
  };

  return {
    data,
    setData,
    error,
    loading,
    refresh: request,
    setLoading,
    params,
    setParams,
  };
}

export default useApi;
