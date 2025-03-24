import { ReactNode } from "react";
import { AppShell, Group } from "@mantine/core";

import { Link } from "react-router-dom";
import { useUser } from "../auth/hooks";

type AppShellComponentProps = {
  navItems?: ReactNode;
  children: ReactNode;
};

export default function AppShellComponent({
  navItems,
  children,
}: AppShellComponentProps) {
  const user = useUser();

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
      {user ? (
        <AppShell.Header
          h="75px"
          style={{
            backgroundColor: "rgba(196,213,191,255)",
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
            {navItems}
          </Group>
        </AppShell.Header>
      ) : (
        <></>
      )}

      <AppShell.Main
        style={{
          backgroundColor: `${
            user ? "rgb(237, 237, 237)" : "rgba(196,213,191,255)"
          }`,
        }}
      >
        {children}
      </AppShell.Main>
    </AppShell>
  );
}
