import { Link } from "react-router-dom";
import { Center, Stack, Text, Title, Button } from "@mantine/core";
import { IconCircleCheckFilled } from "@tabler/icons-react";

export default function VerificationEmailSent() {
  return (
    <Center>
      <Stack justify="center" style={{ textAlign: "center" }} align="center">
        <IconCircleCheckFilled
          size={80}
          style={{ color: "green", marginBottom: "10px" }}
        />
        <Title order={2}>You are registered!</Title>
        {/* TODO: Tell them what email address to confirm... */}
        <Text>
          We have sent you a confirmation email. Please head to your inbox to
          verify.
        </Text>

        <Link to="/account/login">
          <Button variant="outline" fullWidth>
            Go to Login
          </Button>
        </Link>
      </Stack>
    </Center>
  );
}
