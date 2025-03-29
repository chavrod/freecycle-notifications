import { useState } from "react";
import { UseFormReturnType } from "@mantine/form";
import * as Sentry from "@sentry/react";

import { isStandardApiError, convertArrayValuesToStrings } from "./apiClient";
import { STANDARD_ERROR_MESSAGE } from "../constants";

interface useApiSubmitProps {
  apiFunc?: (formData: any) => Promise<any>;
  form: UseFormReturnType<any, any>;
  onSuccess: (res: any) => void;
}

/**
 * Used when a form is sent as part of a POST request to backend
 */
const useApiSubmit = ({ apiFunc, form, onSuccess }: useApiSubmitProps) => {
  const [nonFieldErrors, setNonFieldErrors] = useState<
    string | string[] | null
  >(null);
  const [loading, setLoading] = useState(false);
  const handleSubmit = async (formData: typeof form.values) => {
    if (apiFunc === undefined) return;
    try {
      setLoading(true);
      resetErrors();
      const res = await apiFunc(formData);
      onSuccess(res);
    } catch (e: any) {
      if (!isStandardApiError(e)) {
        Sentry.withScope((scope) => {
          scope.setContext("error_obj", e);
          Sentry.captureMessage(
            "useApiSubmit received non-standard Error",
            "warning"
          );
        });
        setNonFieldErrors(STANDARD_ERROR_MESSAGE);
        return;
      }
      const parsedErrors = convertArrayValuesToStrings(e.data);
      // Filter out keys that match the ones in the form
      const nonFieldErrors =
        typeof parsedErrors === "string"
          ? parsedErrors
          : Object.entries(parsedErrors)
              .filter(([key, _]) => form.getInputProps(key).value === undefined)
              .map(([_, value]) => value)
              .join("; ");
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
