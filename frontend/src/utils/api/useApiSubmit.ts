import { UseFormReturnType } from "@mantine/form";
import { useState } from "react";

import { isApiError, ApiError } from "./apiClient";
import { STANDARD_ERROR_MESSAGE } from "../constants";

interface useApiSubmitProps {
  apiFunc?: (formData: any) => Promise<any>;
  form: UseFormReturnType<any, any>;
  onSuccess: (res: Promise<any>) => void;
}

function convertValuesToString(
  obj: object | string
): Record<string, string> | string {
  if (typeof obj == "string") return obj;

  const result: Record<string, string> = {};

  for (const [key, value] of Object.entries(obj)) {
    if (Array.isArray(value)) {
      // If the value is an array, join the elements
      result[key] = value.join("; ");
    } else {
      // If the value is a string, use it directly
      result[key] = value;
    }
  }

  return result;
}

const useApiSubmit = ({ apiFunc, form, onSuccess }: useApiSubmitProps) => {
  const [nonFieldErrors, setNonFieldErrors] = useState<
    string | string[] | null
  >(null);
  const [loading, setLoading] = useState(false);
  const handleSubmit = async (formData: typeof form.values) => {
    if (apiFunc === undefined) return;
    try {
      resetErrors();
      const res = await apiFunc(formData);
      onSuccess(res);
    } catch (e) {
      // TODO: Nicer way...
      if (!isApiError(e)) {
        // TODO: REPORT TO SENTRY
        console.error("An unexpected error occurred:", e);
        setNonFieldErrors(STANDARD_ERROR_MESSAGE);
        return;
      }
      const parsedErrors = convertValuesToString(e.data);
      console.log("NON-PARSED ERRORS:", e.data);
      console.log("PARSED ERRORS:", parsedErrors);
      // Filter out keys that match the ones in the form
      const nonFieldErrors = Object.entries(parsedErrors)
        .filter(([key, _]) => form.getInputProps(key).value === undefined)
        .map(([_, value]) => value);
      // Set errors
      setNonFieldErrors(nonFieldErrors);
      if (typeof parsedErrors !== "string") form.setErrors(parsedErrors);
    } finally {
      setLoading(false);
    }
  };

  const resetErrors = () => {
    setNonFieldErrors([]);
    form.setErrors({});
  };

  const resetAll = () => {
    resetErrors();
    form.reset();
  };

  return { loading, handleSubmit, nonFieldErrors, resetAll };
};

export default useApiSubmit;
