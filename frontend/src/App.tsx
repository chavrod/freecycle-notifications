import "@mantine/core/styles.css";
import { MantineProvider } from "@mantine/core";
import { Paper } from "@mantine/core";

import { AuthContextProvider } from "./auth";

function App() {
  return (
    <AuthContextProvider>
      <MantineProvider>
        <Paper>Click on the Vite and React logos to learn more</Paper>
      </MantineProvider>
    </AuthContextProvider>
  );
}

export default App;
