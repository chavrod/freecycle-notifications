import { ReactNode } from "react";
import { AppShell, Group } from "@mantine/core";

import { Link } from "react-router-dom";

type AppShellComponentProps = {
  navItems?: ReactNode;
  children: ReactNode;
};

export default function AppShellComponent({
  navItems,
  children,
}: AppShellComponentProps) {
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
          {navItems}
        </Group>
      </AppShell.Header>

      <AppShell.Main style={{ backgroundColor: "#ededed" }}>
        {children}
      </AppShell.Main>
    </AppShell>
  );
}
