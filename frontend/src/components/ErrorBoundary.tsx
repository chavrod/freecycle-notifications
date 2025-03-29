import { useEffect } from "react";
import { useRouteError, isRouteErrorResponse, Link } from "react-router-dom";
import { IconZoomExclamation } from "@tabler/icons-react";
import { Text, Button, Stack } from "@mantine/core";
import * as Sentry from "@sentry/react";

import AppShellComponent from "./AppShell";
import CentredFlexPaper from "./CenteredFlexPaper";

const ErrorBoundary = () => {
  const rawError = useRouteError();
  const routing_error = isRouteErrorResponse(rawError) ? rawError : null;

  // Send the error to Sentry when the component mounts
  useEffect(() => {
    // Only capture non-route errors or non-404 route errors
    if (!routing_error || routing_error.status !== 404) {
      Sentry.captureException(rawError);
    }
  }, [rawError, routing_error]);

  return (
    <AppShellComponent>
      <CentredFlexPaper title="Something Went Wrong!">
        <Stack align="center" mx="sm">
          <IconZoomExclamation
            size={120}
            style={{ color: "#fb8080", marginBottom: "10px" }}
          />
          <Text
            size="lg"
            w="100%"
            style={{
              textAlign: "center",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
          >
            {routing_error?.data || "It is an error. That is all we know."}
          </Text>
        </Stack>
        <Link to="/" style={{ textDecoration: "none" }}>
          <Button fullWidth>Back to Homepage</Button>
        </Link>
      </CentredFlexPaper>
    </AppShellComponent>
  );
};

export default ErrorBoundary;
