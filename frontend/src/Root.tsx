import { useState } from "react";

import { Menu, Button } from "@mantine/core";
import { useMediaQuery } from "@mantine/hooks";
import { useLocation, Link, Outlet } from "react-router-dom";
import { IconLogout, IconSettings, IconUser } from "@tabler/icons-react";

import { useUser } from "./auth/hooks";
import { logout } from "./auth/api";
import AppShellComponent from "./components/AppShell";

type NavBarItemProps = {
  to: string;
  text: string;
  isMobile: boolean | undefined;
};

export const NavBarItem: React.FC<NavBarItemProps> = ({
  to,
  text,
  isMobile,
}) => {
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

  const [opened, setOpened] = useState(false);

  return (
    <AppShellComponent
      navItems={
        <Menu
          position="bottom-end"
          shadow="md"
          width={200}
          opened={opened}
          onChange={setOpened}
        >
          <Menu.Target>
            <Button
              variant={opened ? "filled" : "outline"}
              size={isMobile ? "sm" : "md"}
            >
              Account
            </Button>
          </Menu.Target>

          <Menu.Dropdown>
            <Menu.Label>{user?.email}</Menu.Label>
            <Link to="/manage-account" style={{ textDecoration: "none" }}>
              <Menu.Item leftSection={<IconUser size={14} />}>
                Manage Account
              </Menu.Item>
            </Link>
            <Link to="/manage-chats" style={{ textDecoration: "none" }}>
              <Menu.Item leftSection={<IconSettings size={14} />}>
                Manage Chats
              </Menu.Item>
            </Link>
            <Menu.Item
              color="red"
              leftSection={<IconLogout size={14} />}
              onClick={logout}
            >
              Logout
            </Menu.Item>
          </Menu.Dropdown>
        </Menu>
      }
    >
      <Outlet />
    </AppShellComponent>
  );
}
