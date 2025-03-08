import React, { useEffect } from "react";

import {
  Stack,
  Text,
  Paper,
  Group,
  Button,
  Loader,
  Title,
  SegmentedControl,
  ThemeIcon,
} from "@mantine/core";
import { IconLinkOff, IconInfoCircle } from "@tabler/icons-react";
import { useDisclosure } from "@mantine/hooks";
import { notifications } from "@mantine/notifications";

import LinkChatModal from "../components/LinkChatModal";
import useApi from "../utils/api/useApi";
import coreApi from "../utils/api/coreApi";
import { Chat, ChatStateType } from "../utils/api/api_types";
import { useState } from "react";
import { STANDARD_ERROR_MESSAGE } from "../utils/constants";
import {
  ChatProviderIcon,
  ChatProviderColor,
  ChatStateEmoji,
} from "../utils/enum_records";
import UnlinkChatModal from "../components/UnlinkChatModal";

export default function ManageChats() {
  const [
    openedChatUnlinkModal,
    { open: openChatUnlinkModal, close: closeChatUnlinkModal },
  ] = useDisclosure(false);
  const [chatToUnlink, setChatToUnlink] = useState<Chat | null>(null);

  const [
    openedChatLinkModal,
    { open: openChatLinkModal, close: closeChatLinkModal },
  ] = useDisclosure(false);

  const chatsRes = useApi<Chat[]>({
    apiFunc: coreApi.chatsList,
    unpackName: "chats",
    defaultData: [],
  });
  const [chatsData, setChatsData] = useState<Chat[]>(chatsRes.data);
  useEffect(() => {
    setChatsData(chatsRes.data);
  }, [JSON.stringify(chatsRes.data)]);

  const [loadingToggleStateIndices, setLoadingToggleStateIndices] = useState<
    number[]
  >([]);

  const toggleChatState = (index: number) =>
    setChatsData((prevChats) =>
      prevChats.map((chat, idx) =>
        idx === index
          ? {
              ...chat,
              state:
                chat.state === ChatStateType.ACTIVE
                  ? ChatStateType.INACTIVE
                  : ChatStateType.ACTIVE,
            }
          : chat
      )
    );

  const handleToggleState = async (id: number, index: number) => {
    setLoadingToggleStateIndices((prev) => [...prev, index]);
    // Optimistically update chat state
    toggleChatState(index);

    try {
      const res = await coreApi.chatsToggleState(id.toString());
      const updatedState = res.chat.state;
      notifications.show({
        title: "Notifications Updated",
        message: `Notifications are turned ${
          updatedState === ChatStateType.ACTIVE ? "on" : "off"
        }`,
        color: "#326950",
      });
    } catch (e) {
      notifications.show({
        title: "Error occured!",
        message: STANDARD_ERROR_MESSAGE,
        color: "red",
      });
      // Revert on error
      toggleChatState(index);
    } finally {
      setLoadingToggleStateIndices((prev) => prev.filter((i) => i !== index));
    }
  };

  return (
    <>
      <LinkChatModal
        opened={openedChatLinkModal}
        onClose={closeChatLinkModal}
        onSuccess={chatsRes.refresh}
      />
      <UnlinkChatModal
        chat={chatToUnlink}
        opened={openedChatUnlinkModal}
        onClose={() => {
          setChatToUnlink(null);
          closeChatUnlinkModal();
        }}
        onSuccess={chatsRes.refresh}
      />
      {/* Main Content */}
      <Stack align="center">
        <Title order={3} mt="xl">
          Manage Chats
        </Title>

        {chatsRes.loading ? (
          <Group gap="md" mt="xl" justify="center">
            <Loader />
            <Text>Loading Chats...</Text>
          </Group>
        ) : chatsData.length > 0 ? (
          <Stack align="center" mb="md">
            {chatsData.map((chat, index) => (
              <Paper p="md" w={{ base: "100%", xs: 400 }} key={chat.id}>
                <Stack>
                  <Group justify="space-between">
                    <Stack gap={0}>
                      <Group>
                        {ChatProviderIcon[chat.provider] &&
                          React.createElement(ChatProviderIcon[chat.provider], {
                            size: 30,
                            color: ChatProviderColor[chat.provider],
                          })}
                        <Text>{chat.provider}</Text>
                      </Group>
                      <Text c="dimmed" size="sm">
                        {`${chat.name} ${
                          chat.number !== null
                            ? `(${chat.number})`
                            : `(no username)`
                        }`}
                      </Text>
                    </Stack>
                    {loadingToggleStateIndices.includes(index) ? (
                      <Loader size="sm" />
                    ) : (
                      ChatStateEmoji[chat.state]
                    )}
                  </Group>

                  <Stack gap={0}>
                    <Group gap="xs">
                      <Text>Notifications</Text>
                    </Group>
                    <SegmentedControl
                      transitionDuration={500}
                      disabled={loadingToggleStateIndices.includes(index)}
                      value={chat.state}
                      onChange={() => handleToggleState(chat.id, index)}
                      data={[
                        { label: "ON", value: "ACTIVE" },
                        { label: "OFF", value: "INACTIVE" },
                      ]}
                    />
                  </Stack>
                  <Group gap="xs">
                    <Button
                      leftSection={<IconLinkOff size={20} />}
                      color="#fb8080"
                      fullWidth
                      variant="light"
                      onClick={() => {
                        setChatToUnlink(chat);
                        openChatUnlinkModal();
                      }}
                    >
                      Unlink Chat
                    </Button>
                  </Group>
                </Stack>
              </Paper>
            ))}
            <Paper my="md" p="md" w={{ base: "100%", xs: 400 }}>
              <Stack>
                <Group gap="xs">
                  <ThemeIcon variant="light">
                    <IconInfoCircle size={"1.2rem"} />
                  </ThemeIcon>
                  <Text fw={700}>Info</Text>
                </Group>
                <Text size="md">
                  At the moment, we only allow 1 chat per account.
                </Text>
              </Stack>
            </Paper>
          </Stack>
        ) : (
          <Paper my="md" p="md" w={{ base: "100%", xs: 400 }}>
            <Group wrap="nowrap" justify="space-between">
              <Text>No Chats Linked 📵</Text>
              <Button onClick={openChatLinkModal} variant="outline">
                Link Chat
              </Button>
            </Group>
          </Paper>
        )}
      </Stack>
    </>
  );
}
