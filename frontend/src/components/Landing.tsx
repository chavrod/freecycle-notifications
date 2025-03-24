import { Link } from "react-router";
import { Stack, Flex, Title, Box, Group, Button } from "@mantine/core";
import { useMediaQuery } from "@mantine/hooks";

type ButtonLinkProps = {
  to: string;
  text: string;
  isMobile: boolean | undefined;
};

export default function Landing() {
  const isMobile = useMediaQuery("(max-width: 48em)");

  const ButtonLink: React.FC<ButtonLinkProps> = ({ to, text, isMobile }) => {
    return (
      <Link to={to}>
        <Button variant="filled" size={isMobile ? "sm" : "md"}>
          {text}
        </Button>
      </Link>
    );
  };

  return (
    <Flex
      gap="md"
      justify="center"
      align="center"
      direction="column"
      style={{ height: "calc(100vh - 130px)" }}
    >
      <Box
        w={{ base: "300px", sm: "400px" }}
        p="md"
        style={{
          backgroundColor: "rgba(196,213,191,255)",
          // border: "1px sold #073b31",
        }}
      >
        <Stack align="center">
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
          <Title
            order={4}
            style={{
              color: "#073b31",
              textAlign: "center",
            }}
            mb="sm"
          >
            🔔 Get a Telegram message when your item pops up on freecycle.org
          </Title>
          <Group gap={isMobile ? "md" : "lg"} justify="flex-end" wrap="nowrap">
            <ButtonLink to="/account/login" text="Login" isMobile={isMobile} />
            <ButtonLink
              to="/account/signup"
              text="Signup"
              isMobile={isMobile}
            />
          </Group>
          <Box
            my="md"
            style={{
              width: "180px",
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
                width: "224px",
                height: "112px",
              }}
            />
          </a>
        </Stack>
      </Box>
    </Flex>
  );
}
