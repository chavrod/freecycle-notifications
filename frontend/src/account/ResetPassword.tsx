import { useState } from "react";

import { Navigate, useLoaderData, LoaderFunctionArgs } from "react-router-dom";
import { Button, Text, Stack, Modal, Paper } from "@mantine/core";
import { useForm } from "@mantine/form";
import { notifications } from "@mantine/notifications";
import { useDisclosure } from "@mantine/hooks";

import PasswordStrengthInput from "../auth/PasswordStrengthInput";
import { getPasswordReset, resetPassword, formatAuthErrors } from "../auth/api";
import { AuthRes } from "../auth/AuthContext";

export async function loader({ params }: LoaderFunctionArgs) {
  const key = params.key;

  const resp = await getPasswordReset(key);
  return { key, keyResponse: resp };
}

export default function ResetPassword() {
  const { key, keyResponse } = useLoaderData();

  const [visible, { toggle }] = useDisclosure(false);

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
      setConfirmationRes({ ...confirmationRes, fetching: true });

      const { password1 } = form.values;
      const res = await resetPassword({ key, password: password1 });
      setConfirmationRes({ fetching: false, content: res });

      if (res.status === 400) {
        form.setErrors(formatAuthErrors(res.errors, { password: "password1" }));
      } else if (res.status !== 401) {
        // TODO: REPORT TO SENTRY
        notifications.show({
          title: "Server Error!",
          message:
            "Unexpected error. Please try again later or contact help@shopwiz.ie",
          color: "red",
        });
      }
    } catch (error) {
      // TODO: REPORT UNKNOW ERROR TO SENTRY
      notifications.show({
        title: "Server Error!",
        message: "Unexpected error. Please try again later.",
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
    return <Navigate to="/account/login" />;
  }

  if (!keyResponse) {
    return <></>;
  }

  return (
    <Modal
      opened={true}
      onClose={() => {}}
      fullScreen
      transitionProps={{ transition: "fade", duration: 200 }}
      withCloseButton={false}
    >
      <Stack
        align="center"
        justify="center"
        style={{ height: "calc(100vh - 130px)" }}
      >
        <Paper radius="md" p="md">
          {keyResponse.status === 200 ? (
            <form onSubmit={form.onSubmit(handleFormSubmit)}>
              <Text>
                Set new password for your{" "}
                <Text td="underline" c="blue" span>
                  {keyResponse.data.user?.email}
                </Text>{" "}
                account.
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
            </form>
          ) : (
            <Text>Invalid password reset token.</Text>
          )}
        </Paper>
      </Stack>
    </Modal>
  );
}
