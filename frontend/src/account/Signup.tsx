import { useState } from "react";
import {
  TextInput,
  Button,
  Center,
  Stack,
  Text,
  Title,
  Flex,
  Paper,
} from "@mantine/core";
import { useForm } from "@mantine/form";
import { notifications } from "@mantine/notifications";
import { useDisclosure } from "@mantine/hooks";
import { IconCircleCheckFilled } from "@tabler/icons-react";

import { signUp, formatAuthErrors } from "../auth/api";
import PasswordStrengthInput from "../auth/PasswordStrengthInput";

function Signup() {
  const [visible, { toggle }] = useDisclosure(false);

  const [isLoading, setIsLoading] = useState(false);
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
      setIsLoading(true);

      const { email, password1 } = form.values;

      const res = await signUp({ email, password: password1 });

      console.log("SIGNUP RES: ", res);

      if (res.status === 400) {
        form.setErrors(formatAuthErrors(res.errors, { password: "password1" }));
        // 401 indicates that email verificaiton is required
      } else if (res.status != 401) {
        setIsRegistrationSubmitted(true);
      } else {
        throw new Error(res.errors[0].message);
      }
    } catch (error: any) {
      setIsLoading(false);
      notifications.show({
        title: "Server Error!",
        message: error?.message || "Unknown error. Please try again later.",
        color: "red",
      });
    } finally {
      setIsLoading(false);
    }

    // Handle the response data as required (e.g., show a success message or error message)
  };

  return (
    <Flex
      gap="md"
      justify="center"
      align="center"
      direction="column"
      style={{ height: "calc(100vh - 130px)" }}
    >
      {!isRegistrationSubmitted ? (
        <Paper w={{ base: "320px", sm: "480px" }} radius="md" p="md">
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
          </form>
        </Paper>
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
              style={{ color: "green", marginBottom: "10px" }}
            />
            <Title order={2}>You are registered!</Title>
            <Text>
              We have sent a confirmation email to{" "}
              <strong>{form.values.email}</strong>. Please head to your inbox to
              verify.
            </Text>

            {/* <Button variant="outline" onClick={handleMoveToLogin} fullWidth>
              Go to Login
            </Button> */}
          </Stack>
        </Center>
      )}
    </Flex>
  );
}

export default Signup;
