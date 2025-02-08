import { useState } from "react";

import { TextInput, Text, Button, PasswordInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { notifications } from "@mantine/notifications";
import { Link } from "react-router-dom";

import { login, formatAuthErrors } from "../auth/api";
import { AuthFlow } from "../auth/AuthContext";

function LoginForm() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const form = useForm({
    initialValues: {
      email: "",
      password: "",
    },
    validate: {
      email: (value) =>
        !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i.test(value)
          ? "Invalid email."
          : null,
      password: (value) =>
        value.trim().length === 0 ? "Password is required." : null,
    },
  });

  const handleFormSubmit = async () => {
    try {
      setIsLoading(true);

      const { email, password } = form.values;

      const res = await login({ email, password });
      const resCode: number | undefined = res?.status;
      console.log("LOGIN RES: ", res);

      if (resCode === 400) {
        form.setErrors(formatAuthErrors(res.errors));
      } else if (resCode === 401) {
        const verifyEmailPending = res.data.flows.find(
          (flow: AuthFlow) =>
            flow.id === "verify_email" && flow.is_pending === true
        );
        // TODO: REPORT TO SENTRY
        setError(
          verifyEmailPending
            ? "You must verify your email first"
            : "Unexpected error. Please try again later or contact help@fcalerts.io"
        );
      } else {
        // TODO: REPORT TO SENTRY
        setError(
          "Unexpected error. Please try again later or contacthelp@fcalerts.io"
        );
      }
    } catch (err: any) {
      notifications.show({
        title: "Server Error!",
        message: err?.message || "Unknown error. Please try again later.",
        color: "red",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={form.onSubmit(handleFormSubmit)}>
      <TextInput
        id="login_email"
        label="Email"
        placeholder="Your email address"
        required
        {...form.getInputProps("email")}
        disabled={isLoading}
      />
      <PasswordInput
        id="login_password"
        label="Password"
        placeholder="Your password"
        required
        style={{ marginTop: 15 }}
        {...form.getInputProps("password")}
        disabled={isLoading}
      />
      {error && (
        <Text size="sm" color="red" mt="md">
          {error}
        </Text>
      )}
      <Button
        type="submit"
        disabled={isLoading}
        loading={isLoading}
        style={{ marginTop: 20 }}
        fullWidth
      >
        Login
      </Button>
      <Link to="account/password/reset">
        <Text
          mt="xs"
          size="sm"
          c="brand.9"
          sx={{
            cursor: "pointer",
            "&:hover": {
              textDecoration: "underline",
            },
          }}
        >
          Forgot Password?
        </Text>
      </Link>
    </form>
  );
}

export default LoginForm;
