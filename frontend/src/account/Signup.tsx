import { useState } from "react";
import { TextInput, Button, Center, Stack, Text, Title } from "@mantine/core";
import { useForm } from "@mantine/form";
import { useDisclosure } from "@mantine/hooks";
import { IconCircleCheckFilled } from "@tabler/icons-react";
import * as Sentry from "@sentry/react";

import { STANDARD_ERROR_MESSAGE } from "../utils/constants";
import { signUp, formatAuthErrors } from "../auth/api";
import PasswordStrengthInput from "../auth/PasswordStrengthInput";
import CentredFlexPaper from "../components/CenteredFlexPaper";

function Signup() {
  const [visible, { toggle }] = useDisclosure(false);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isRegistrationSubmitted, setIsRegistrationSubmitted] = useState(false);

  const form = useForm({
    initialValues: {
      email: "",
      username: "",
      password1: "",
      password2: "", // repeat password
    },
    validate: {
      email: (value) =>
        !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i.test(value)
          ? "Invalid email."
          : null,
      password1: (value) =>
        value.trim().length === 0 ? "Password is required." : null,
      password2: (value, values) =>
        value !== values.password1 ? "Passwords must match." : null,
    },
  });

  const handleFormSubmit = async () => {
    try {
      setError(null);
      setIsLoading(true);

      const { email, password1 } = form.values;

      const res = await signUp({ email, password: password1 });

      if (res.status === 400) {
        form.setErrors(formatAuthErrors(res.errors, { password: "password1" }));
        // 401 indicates that email verificaiton is required
      } else if (res.status == 403) {
        setError(res.errors?.[0]?.message || STANDARD_ERROR_MESSAGE);
      } else if (res.status == 401) {
        setIsRegistrationSubmitted(true);
      } else {
        Sentry.withScope((scope) => {
          scope.setTag("auth_stage", "signup");
          scope.setContext("error_res", res);
          Sentry.captureMessage(
            `Unexpected authentication response at Signup: ${res.status}`,
            "warning"
          );
        });
        setError(STANDARD_ERROR_MESSAGE);
      }
    } catch (error: any) {
      Sentry.withScope((scope) => {
        scope.setTag("auth_stage", "login");
        Sentry.captureException(error);
      });
      setError(STANDARD_ERROR_MESSAGE);
    } finally {
      setIsLoading(false);
    }

    // Handle the response data as required (e.g., show a success message or error message)
  };

  return (
    <CentredFlexPaper title="Signup" closeButtonPath="/">
      {!isRegistrationSubmitted ? (
        <form onSubmit={form.onSubmit(handleFormSubmit)}>
          <TextInput
            id="email"
            label="Email"
            placeholder="Your email address"
            required
            {...form.getInputProps("email")}
            disabled={isLoading}
          />
          <PasswordStrengthInput
            form={form}
            isLoading={isLoading}
            visible={visible}
            toggle={toggle}
          />
          <Button
            type="submit"
            disabled={isLoading}
            loading={isLoading}
            style={{ marginTop: 20 }}
            fullWidth
          >
            Signup
          </Button>
          {error && (
            <Text size="sm" c="red" mt="md">
              {error}
            </Text>
          )}
        </form>
      ) : (
        // Email verification message UI
        <Center>
          <Stack
            justify="center"
            style={{ textAlign: "center" }}
            align="center"
          >
            <IconCircleCheckFilled
              size={80}
              style={{ color: "#326950", marginBottom: "10px" }}
            />
            <Title order={2}>You are registered!</Title>
            <Text>
              We have sent a confirmation email to{" "}
              <strong>{form.values.email}</strong>. Please head to your inbox to
              verify.
            </Text>
          </Stack>
        </Center>
      )}
    </CentredFlexPaper>
  );
}

export default Signup;
