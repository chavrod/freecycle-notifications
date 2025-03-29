import { useState } from "react";
import * as Sentry from "@sentry/react";

import { isStandardApiError, convertArrayValuesToStrings } from "./apiClient";
import { STANDARD_ERROR_MESSAGE } from "../constants";

interface useApiSubmitProps {
  apiFunc?: () => Promise<any>;
  onSuccess: (res: any) => void;
}

/**
 * Used for simple POST requests without a form
 */
const useApiAction = ({ apiFunc, onSuccess }: useApiSubmitProps) => {
  const [errors, setErrors] = useState<string | string[] | null>(null);
  const [loading, setLoading] = useState(false);
  const handleSubmit = async () => {
    if (apiFunc === undefined) return;
    try {
      setLoading(true);
      resetErrors();
      const res = await apiFunc();
      onSuccess(res);
    } catch (e: any) {
      if (!isStandardApiError(e)) {
        Sentry.withScope((scope) => {
          scope.setContext("error_obj", e);
          Sentry.captureMessage(
            "useApiAction received non-standard Error",
            "warning"
          );
        });
        setErrors(STANDARD_ERROR_MESSAGE);
        return;
      }
      // Parse errors
      const parsedErrors = convertArrayValuesToStrings(e.data);
      const nonFieldErrors =
        typeof parsedErrors === "string"
          ? parsedErrors
          : Object.entries(parsedErrors)
              .map(([_, value]) => value)
              .join("; ");
      // Set errors
      setErrors(nonFieldErrors);
    } finally {
      setLoading(false);
    }
  };

  const resetErrors = () => {
    setErrors([]);
  };

  const resetAll = () => {
    resetErrors();
  };

  return { loading, handleSubmit, errors, resetAll };
};

export default useApiAction;
