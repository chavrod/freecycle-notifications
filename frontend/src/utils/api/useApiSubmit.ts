import { UseFormReturnType } from "@mantine/form";
import { showNotification } from "@mantine/notifications";
import { useState } from "react";

import { isApiError, ApiError } from "./apiClient";

interface useApiSubmitProps {
  apiFunc?: (formData: any) => Promise<any>;
  form: UseFormReturnType<any, any>;
  onSuccess: (res: Promise<any>) => void;
  onError?: (res: ApiError) => void;
}

function flattenObject(obj: object, prefix = '') {
  const flattened: any = {};

  for (const [key, value] of Object.entries(obj)) {
    const prefixedKey = prefix ? `${prefix}.${key}` : key;

    if (typeof value === 'object' && value !== null) {
      if (Array.isArray(value) && typeof value[0] === 'string') {
        flattened[prefixedKey] = value[0];
      } else {
        Object.assign(flattened, flattenObject(value, prefixedKey));
      }
    } else {
      flattened[prefixedKey] = value;
    }
  }

  return flattened;
}

const useApiSubmit = ({
  apiFunc,
  form,
  onSuccess,
  onError = () => {},
}: useApiSubmitProps) => {
  const [error, setError] = useState(false);
  const [nonFieldErrors, setNonFieldErrors] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const handleSubmit = async (formData: typeof form.values) => {
    if (apiFunc === undefined) return;
    try {
      setNonFieldErrors(null)
      setLoading(true);
      const res = await apiFunc(formData);
      onSuccess(res);
    } catch (e) {
      if (isApiError(e)) {
        if (e.statusCode === 500) {
          // "Unexpected error. Please try again later or contact help@pingcycle.org"
          setNonFieldErrors("Unexpected error. Please try again later or contact help@pingcycle.org")
        } else if (e.statusCode === 400) {
          const allErrors = e.data;
          console.log('ALL ERRORS:', allErrors);

          form.setErrors(allErrors);

          const nonFieldErrors = Object.entries(allErrors)
            .filter(([key, _]) => form.getInputProps(key).value === undefined)
            .map(([key, value]) => value);
          setError(true);
          onError(e);
          form.setErrors(e.data);
        else {
          setNonFieldErrors(e.data);
        }

        }
      } else {
        // TODO: REPORT TO SENTRY
        console.error("An unexpected error occurred:", e);
      }
    } finally {
      setLoading(false);
    }
  };

  const resetErrors = () => {
    setNonFieldErrors([]);
    form.setErrors({});
    setError(false);
  };

  return { loading, errors: nonFieldErrors, handleSubmit, resetErrors, error };
};

export default useApiSubmit;
