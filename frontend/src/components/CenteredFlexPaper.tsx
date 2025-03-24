import { Paper, Stack, Flex, Title, Group, ActionIcon } from "@mantine/core";
import { ReactNode } from "react";
import { IconX } from "@tabler/icons-react";
import { Link } from "react-router";

export default function CentredFlexPaper({
  children,
  title,
  closeButtonPath,
}: {
  children: ReactNode;
  title?: string;
  closeButtonPath?: string;
}) {
  return (
    <Flex
      gap="md"
      justify="center"
      align="center"
      direction="column"
      style={{ height: "calc(100vh - 180px)" }}
    >
      <img
        src="/logo_main.svg"
        alt=""
        style={{
          width: "150px",
          height: "75px",
        }}
      ></img>
      <img
        src="/name_header_cropped.svg"
        alt=""
        style={{
          width: "150px",
          height: "50px",
        }}
      ></img>
      <Paper w={{ base: "300px", sm: "400px" }} radius="xs" p="md">
        <Stack>
          <Group justify="space-between" wrap="nowrap">
            {title ? <Title order={3}>{title}</Title> : <></>}
            {closeButtonPath ? (
              <Link to={closeButtonPath}>
                <ActionIcon variant="outline">
                  <IconX />
                </ActionIcon>
              </Link>
            ) : (
              <></>
            )}
          </Group>

          {children}
        </Stack>
      </Paper>
    </Flex>
  );
}
