import { useState } from "react";

import { Navigate, useLoaderData, LoaderFunctionArgs } from "react-router-dom";
import { Button, Text } from "@mantine/core";
import { useForm } from "@mantine/form";
import { notifications } from "@mantine/notifications";
import { useDisclosure } from "@mantine/hooks";
import * as Sentry from "@sentry/react";

import { STANDARD_ERROR_MESSAGE } from "../utils/constants";
import PasswordStrengthInput from "../auth/PasswordStrengthInput";
import { getPasswordReset, resetPassword, formatAuthErrors } from "../auth/api";
import { AuthRes } from "../auth/AuthContext";
import CentredFlexPaper from "../components/CenteredFlexPaper";

export async function loader({ params }: LoaderFunctionArgs) {
  const key = params.key;

  const resp = await getPasswordReset(key);
  return { key, keyResponse: resp };
}

export default function ResetPassword() {
  const { key, keyResponse } = useLoaderData();

  const [visible, { toggle }] = useDisclosure(false);

  const [error, setError] = useState<string | null>(null);

  const [confirmationRes, setConfirmationRes] = useState<{
    fetching: boolean;
    content: AuthRes | null;
  }>({ fetching: false, content: null });

  const form = useForm({
    initialValues: {
      password1: "",
      password2: "", // repeat password
    },
    validate: {
      password1: (value) =>
        value.trim().length === 0 ? "Password is required." : null,
      password2: (value, values) =>
        value !== values.password1 ? "Passwords must match." : null,
    },
  });

  const handleFormSubmit = async () => {
    try {
      setError(null);
      setConfirmationRes({ ...confirmationRes, fetching: true });

      const { password1 } = form.values;
      const res = await resetPassword({ key, password: password1 });
      setConfirmationRes({ fetching: false, content: res });

      if (res.status === 400) {
        form.setErrors(formatAuthErrors(res.errors, { password: "password1" }));
        // TODO: Temp workaround as param 'password' is missing
        setError(res.errors.map((error: any) => error.message).join("\n"));
      } else if (res.status !== 401) {
        Sentry.withScope((scope) => {
          scope.setTag("auth_stage", "reset_password");
          scope.setContext("error_res", res);
          Sentry.captureMessage(
            `Unexpected authentication response at ResetPassword: ${res.status}`,
            "warning"
          );
        });
        notifications.show({
          title: "Server Error!",
          message: STANDARD_ERROR_MESSAGE,
          color: "red",
        });
      }
    } catch (error) {
      Sentry.withScope((scope) => {
        scope.setTag("auth_stage", "reset_password");
        Sentry.captureException(error);
      });
      notifications.show({
        title: "Server Error!",
        message: STANDARD_ERROR_MESSAGE,
        color: "red",
      });
    } finally {
      if (confirmationRes.fetching)
        setConfirmationRes({ ...confirmationRes, fetching: false });
    }
  };

  if (
    confirmationRes.content?.status &&
    confirmationRes.content?.status === 401
  ) {
    return <Navigate to="/account/login?password=confirmed" />;
  }

  if (!keyResponse) {
    return <></>;
  }

  return (
    <CentredFlexPaper title="Reset Password">
      {keyResponse.status === 200 ? (
        <form onSubmit={form.onSubmit(handleFormSubmit)}>
          <Text mt="sm" style={{ textAlign: "center" }}>
            Set new password for your{" "}
            <Text td="underline" c="blue" span>
              {keyResponse.data.user?.email}
            </Text>{" "}
            account
          </Text>
          <PasswordStrengthInput
            form={form}
            isLoading={confirmationRes.fetching}
            visible={visible}
            toggle={toggle}
          />
          <Button
            type="submit"
            disabled={confirmationRes.fetching}
            loading={confirmationRes.fetching}
            fullWidth
            my="md"
          >
            Reset Password
          </Button>
          {error && (
            <Text size="sm" c="red" mt="md">
              {error}
            </Text>
          )}
        </form>
      ) : (
        <Text>Invalid password reset token.</Text>
      )}
    </CentredFlexPaper>
  );
}
