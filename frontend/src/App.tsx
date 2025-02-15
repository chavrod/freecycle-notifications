import "@mantine/core/styles.css";
import { MantineProvider } from "@mantine/core";
import { emotionTransform, MantineEmotionProvider } from "@mantine/emotion";

import { AuthContextProvider } from "./auth/AuthContext";
import RouterFn from "./Router";

function App() {
  return (
    <AuthContextProvider>
      <MantineProvider
        stylesTransform={emotionTransform}
        theme={{
          colors: {
            brand: [
              "#c4d5bf",
              "#b6dbb8",
              "#a0ceaf",
              "#a3d6c7",
              "#75b1a7",
              "#5fa08a",
              "#498f6e",
              "#326950",
              "#1c5242",
              "#053c34",
            ],
          },
          primaryColor: "brand",

          shadows: {
            md: "1px 1px 3px rgba(0, 0, 0, .25)",
            xl: "5px 5px 3px rgba(0, 0, 0, .25)",
          },

          headings: {
            fontFamily: "Roboto, sans-serif",
            sizes: {
              h1: { fontSize: "2rem" },
            },
          },
        }}
      >
        <MantineEmotionProvider>
          <RouterFn />
        </MantineEmotionProvider>
      </MantineProvider>
    </AuthContextProvider>
  );
}

export default App;
