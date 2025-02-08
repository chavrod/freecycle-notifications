import { AppShell, Group, ActionIcon } from "@mantine/core";
import { IconKey, IconUser, IconLock, IconHome } from "@tabler/icons-react";

import { useUser } from "./auth/hooks";
import { useLocation, Link, Outlet } from "react-router-dom";

type NavBarItemProps = {
  to: string;
  icon: React.ReactNode;
};

const NavBarItem: React.FC<NavBarItemProps> = ({ to, icon }) => {
  const location = useLocation();
  const isActive = location.pathname.startsWith(to);
  return (
    <Link to={to}>
      <ActionIcon variant={isActive ? "filled" : "outline"} size="md">
        {icon}
      </ActionIcon>
    </Link>
  );
};

export default function Root() {
  const user = useUser();
  const anonNav = (
    <Group justify="flex-end">
      <NavBarItem to="/account/login" icon={<IconKey />} />
      <NavBarItem to="/account/signup" icon={<IconUser />} />
      <NavBarItem to="/account/password/reset" icon={<IconLock />} />
    </Group>
  );
  const authNav = (
    <NavBarItem to="/account/password/change" icon={<IconLock />} />
  );
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
      <AppShell.Header>
        <Group justify="space-between">
          <NavBarItem to="/" icon={<IconHome />} />
          {user ? authNav : anonNav}
        </Group>
      </AppShell.Header>

      <AppShell.Main>
        <Outlet />
      </AppShell.Main>
    </AppShell>
  );
}
