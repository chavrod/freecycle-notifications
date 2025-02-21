import { useRouteError, isRouteErrorResponse, Link } from "react-router-dom";
import { Text, Button, Stack } from "@mantine/core";
import { IconZoomExclamation } from "@tabler/icons-react";

import AppShellComponent from "./AppShell";
import CentredFlexPaper from "./CenteredFlexPaper";

const ErrorBoundary = () => {
  const rawError = useRouteError();
  const error_res = isRouteErrorResponse(rawError) ? rawError : null;

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
            {error_res?.data || "It is an error. That is all we know."}
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
