import { Link } from "react-router-dom";
import { Text, Title, Button } from "@mantine/core";
import { IconCircleCheckFilled } from "@tabler/icons-react";

import CentredFlexPaper from "../components/CenteredFlexPaper";

export default function VerificationEmailSent() {
  return (
    <CentredFlexPaper>
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
    </CentredFlexPaper>
  );
}
