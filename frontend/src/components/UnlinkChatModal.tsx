import {
  Text,
  Button,
  Modal,
  Stack,
  Group,
  ThemeIcon,
  TextInput,
} from "@mantine/core";
import { IconInfoCircle } from "@tabler/icons-react";
import { notifications } from "@mantine/notifications";
import coreApi from "./../utils/api/coreApi";
import { useState } from "react";

import { Chat } from "../utils/api/api_types";
import { STANDARD_ERROR_MESSAGE } from ".././utils/constants";

export default function UnlinkChatModal({
  chat,
  opened,
  onClose,
  onSuccess,
}: {
  chat: Chat | null;
  opened: boolean;
  onClose: () => void;
  onSuccess: () => void;
}) {
  const [confirmationText, setConfirmationText] = useState("");

  const [loading, setLoading] = useState(false);
  const handleUnlinkChat = async (chat: Chat | null) => {
    if (!chat) return;

    setLoading(true);
    try {
      await coreApi.chatsDestroy(chat.id.toString());
      notifications.show({
        title: "Chat unlinked",
        message: "🪦 We have deleted this chat from our records",
        color: "#326950",
      });
      onSuccess();
      onClose();
      setConfirmationText("");
    } catch (e) {
      notifications.show({
        title: "Error occured!",
        message: STANDARD_ERROR_MESSAGE,
        color: "red",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      opened={opened}
      centered
      onClose={() => {
        if (loading) return;
        onClose();
      }}
      title="Unink Chat"
    >
      <Stack mb="sm">
        <Group gap="xs">
          <ThemeIcon variant="light" color="#fb8080">
            <IconInfoCircle size={"1.2rem"} />
          </ThemeIcon>
          <Text fw={700}>Info</Text>
        </Group>
        <Text size="md">
          This action will delete the chat from our records.
        </Text>
        {chat ? (
          <Text size="md" fw={700}>
            {chat?.provider}
            {" - "}
            {`${chat.name} ${
              chat.number !== null ? `(${chat.number})` : `(no username)`
            }`}
          </Text>
        ) : (
          <></>
        )}

        <Text size="md">Please type 'UNLINK' to confirm.</Text>
      </Stack>
      <TextInput
        placeholder="Type UNLINK to confirm"
        value={confirmationText}
        onChange={(event) => setConfirmationText(event.currentTarget.value)}
        disabled={loading}
        styles={() => ({
          input: {
            "&:focus": {
              borderColor: "#fb8080",
            },
          },
        })}
      />

      <Button
        color="#fb8080"
        type="submit"
        fullWidth
        loading={loading}
        disabled={confirmationText !== "UNLINK"}
        onClick={() => handleUnlinkChat(chat)}
        mt="md"
      >
        Unlink Chat
      </Button>
    </Modal>
  );
}
