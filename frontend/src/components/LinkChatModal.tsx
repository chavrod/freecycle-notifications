import {
  Text,
  Button,
  Modal,
  Stack,
  Group,
  ThemeIcon,
  Loader,
} from "@mantine/core";
import { IconInfoCircle, IconCirclesRelation } from "@tabler/icons-react";

import useApiAction from "../utils/api/useApiAction";
import coreApi from "./../utils/api/coreApi";
import { useEffect, useState } from "react";

export default function LinkChatModal({
  opened,
  onClose,
  onSuccess,
}: {
  opened: boolean;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [linkingSessionState, setLinkingSessionState] = useState<
    "not_started" | "started" | "complete"
  >("not_started");
  const [sessionUuid, setSessionUuid] = useState<string | null>(null);

  const {
    handleSubmit: requestToLinkChat,
    loading,
    errors,
    resetAll,
  } = useApiAction({
    apiFunc: coreApi.chatsLink,
    onSuccess: (linkingSessionRes) => {
      const linkingSessionUuid = linkingSessionRes.linking_session;
      // Construct Telegram URL with the UUID
      const telegramUrl = `https://t.me/${
        import.meta.env.VITE_TELEGRAM_BOT_USERNAME
      }?start=${linkingSessionUuid}`;
      // Redirect user to the Telegram bot with the UUID
      window.open(telegramUrl, "_blank");
      setSessionUuid(linkingSessionUuid);
      setLinkingSessionState("started");
    },
  });

  // Used to check if chat is linked
  useEffect(() => {
    if (linkingSessionState !== "started") return;

    let attemptCount = 0;
    const maxAttempts = 5;

    const fetchChatState = async () => {
      if (sessionUuid === null) return;

      try {
        await coreApi.chatsGetBySessionUuid(sessionUuid);
        setLinkingSessionState("complete");
      } catch (e) {
        console.log("Waiting for chat to link...");
      }
    };

    const intervalId = setInterval(() => {
      attemptCount += 1;
      if (attemptCount > maxAttempts) {
        clearInterval(intervalId);
        return;
      }
      fetchChatState();
    }, 5000);

    // Cleanup function to clear the interval
    return () => clearInterval(intervalId);
  }, [linkingSessionState, sessionUuid]);

  // Used to check if chat is linked
  useEffect(() => {
    if (linkingSessionState !== "complete") return;
    onSuccess();
  }, [linkingSessionState]);

  return (
    <Modal
      opened={opened}
      centered
      onClose={() => {
        setLinkingSessionState("not_started");
        setSessionUuid(null);
        onClose();
        resetAll();
      }}
      title="Link Chat"
    >
      {linkingSessionState === "not_started" ? (
        <>
          <Stack>
            <Group gap="xs">
              <ThemeIcon variant="light">
                <IconInfoCircle size={"1.2rem"} />
              </ThemeIcon>
              <Text fw={700}>Info</Text>
            </Group>
            <Text size="md">You must have a Telegram account setup.</Text>
            <Text size="md">
              If using from mobile, also make sure you have Telegram app
              installed.
            </Text>
          </Stack>
          {errors && (
            <Text size="sm" c="red" my="md">
              {errors}
            </Text>
          )}
          <Button
            type="submit"
            fullWidth
            loading={loading}
            onClick={requestToLinkChat}
            mt="md"
          >
            Start Linking
          </Button>
        </>
      ) : linkingSessionState == "started" ? (
        <Stack align="center">
          <Loader size={40} />
          <Text>Linking is in Progress </Text>

          <Button
            variant="subtle"
            onClick={() => setLinkingSessionState("not_started")}
          >
            Retry
          </Button>
        </Stack>
      ) : (
        <Stack align="center">
          <IconCirclesRelation
            size={80}
            style={{ color: "#326950", marginBottom: "10px" }}
          />
          <Text>Good stuff! Your chat has been linked.</Text>
          <Button variant="subtle" onClick={onClose}>
            Close
          </Button>
        </Stack>
      )}
    </Modal>
  );
}
