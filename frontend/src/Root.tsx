import { AppShell, Group, Button } from "@mantine/core";
import { useMediaQuery } from "@mantine/hooks";

import { useUser } from "./auth/hooks";
import { useLocation, Link, Outlet } from "react-router-dom";

type NavBarItemProps = {
  to: string;
  text: string;
  isMobile: boolean | undefined;
};

const NavBarItem: React.FC<NavBarItemProps> = ({ to, text, isMobile }) => {
  const location = useLocation();
  const isActive = location.pathname.startsWith(to);
  return (
    <Link to={to}>
      <Button
        variant={isActive ? "filled" : "outline"}
        size={isMobile ? "sm" : "md"}
      >
        {text}
      </Button>
    </Link>
  );
};

export default function Root() {
  const user = useUser();

  const isMobile = useMediaQuery("(max-width: 48em)");

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{
        width: 300,
        breakpoint: "sm",
        collapsed: { desktop: true, mobile: true },
      }}
      padding="md"
    >
      <AppShell.Header
        h="75px"
        style={{
          backgroundColor: "rgba(196,213,191,255)", // Set the background color here
        }}
      >
        <Group
          mx={{ base: "xs", sm: "xl" }}
          h="100%"
          justify="space-between"
          wrap="nowrap"
        >
          <Link to="/">
            <Group gap={0} wrap="nowrap">
              <img
                src="/logo_header.svg"
                alt=""
                style={{
                  width: "60px",
                  height: "60px",
                  objectFit: "cover",
                  objectPosition: "-47px 0px",
                }}
              ></img>
              <img
                src="/name_header.svg"
                alt=""
                style={{
                  width: "120px",
                  height: "60px",
                  objectFit: "cover",
                  objectPosition: "0px -5px",
                }}
              ></img>
            </Group>
          </Link>
          {user ? (
            <NavBarItem
              to="/account/password/change"
              text="Account"
              isMobile={isMobile}
            />
          ) : (
            <Group gap={isMobile ? 2 : "md"} justify="flex-end" wrap="nowrap">
              <NavBarItem
                to="/account/login"
                text="Login"
                isMobile={isMobile}
              />
              <NavBarItem
                to="/account/signup"
                text="Signup"
                isMobile={isMobile}
              />
            </Group>
          )}
        </Group>
      </AppShell.Header>

      <AppShell.Main style={{ backgroundColor: "#ededed" }}>
        <Outlet />
      </AppShell.Main>
    </AppShell>
  );
}
