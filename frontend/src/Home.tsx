import { useUser } from "./auth/hooks";
import Dashboard from "./components/Dashboard";
import Landing from "./components/Landing";

export default function Home() {
  const user = useUser();
  return user ? <Dashboard /> : <Landing />;
}
