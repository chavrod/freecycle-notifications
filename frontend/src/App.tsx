import "@mantine/core/styles.css";
import { MantineProvider } from "@mantine/core";
import { emotionTransform, MantineEmotionProvider } from "@mantine/emotion";

import { AuthContextProvider } from "./auth/AuthContext";
import RouterFn from "./Router";

function App() {
  return (
    <AuthContextProvider>
      <MantineProvider stylesTransform={emotionTransform}>
        <MantineEmotionProvider>
          <RouterFn />
        </MantineEmotionProvider>
      </MantineProvider>
    </AuthContextProvider>
  );
}

export default App;
