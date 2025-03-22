import { Paper, Stack, Flex, Title, Box } from "@mantine/core";

export default function Home() {
  return (
    <Flex
      gap="md"
      justify="center"
      align="center"
      direction="column"
      style={{ height: "calc(100vh - 130px)" }}
    >
      <Paper
        w={{ base: "300px", sm: "400px" }}
        radius="xs"
        p="md"
        style={{
          backgroundColor: "rgba(196,213,191,255)",
          // border: "1px sold #073b31",
        }}
        withBorder
      >
        <Stack align="center">
          <Title
            order={4}
            style={{
              color: "#073b31",
              textAlign: "center",
            }}
          >
            🔔 Get a Telegram message when your item pops up on freecycle.org
          </Title>
          <Stack gap={0}>
            <img
              src="/logo_main.svg"
              alt=""
              style={{
                width: "250px",
                height: "120px",
              }}
            ></img>
            <img
              src="/name_header_cropped.svg"
              alt=""
              style={{
                width: "250px",
                height: "80px",
              }}
            ></img>
          </Stack>
          <Box
            my={0}
            style={{
              width: "120px",
              border: "2px solid #073b31",
            }}
          />
          <a
            href="https://www.freecycle.org"
            target="_blank"
            rel="noopener noreferrer"
          >
            <img
              src="/freecycle.png"
              alt="Freecycle Logo"
              style={{
                width: "280px",
                height: "140px",
              }}
            />
          </a>
        </Stack>
      </Paper>
    </Flex>
  );
}
