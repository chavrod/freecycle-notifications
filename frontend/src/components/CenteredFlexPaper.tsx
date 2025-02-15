import { Paper, Stack, Flex, Title } from "@mantine/core";
import { ReactNode } from "react";

export default function CentredFlexPaper({
  children,
  title,
}: {
  children: ReactNode;
  title?: string;
}) {
  return (
    <Flex
      gap="md"
      justify="center"
      align="center"
      direction="column"
      style={{ height: "calc(100vh - 130px)" }}
    >
      <Paper w={{ base: "300px", sm: "400px" }} radius="xs" p="md">
        <Stack>
          {title ? <Title order={3}>{title}</Title> : <></>}
          {children}
        </Stack>
      </Paper>
    </Flex>
  );
}
