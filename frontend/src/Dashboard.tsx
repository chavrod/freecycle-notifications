import {
  Stack,
  Title,
  Text,
  Paper,
  Group,
  ActionIcon,
  Button,
  Loader,
} from "@mantine/core";
import {
  IconTrash,
  IconBrandTelegram,
  IconClock,
  IconBellPlus,
  IconKeyOff,
} from "@tabler/icons-react";
import { useDisclosure } from "@mantine/hooks";
import TimeAgo from "javascript-time-ago";
import en from "javascript-time-ago/locale/en";
import { notifications } from "@mantine/notifications";

import { useUser } from "./auth/hooks";
import useApi from "./utils/api/useApi";
import coreApi from "./utils/api/coreApi";
import { Keyword } from "./utils/api/api_types";
import AddKeywordModal from "./components/AddKeywordModal";
import { useState } from "react";
import { STANDARD_ERROR_MESSAGE } from "./utils/constants";

export default function DashboardPage() {
  const [opened, { open, close }] = useDisclosure(false);

  TimeAgo.addLocale(en);
  const timeAgo = new TimeAgo("en-US");

  const user = useUser();

  const keywordsRes = useApi<Keyword[]>({
    apiFunc: coreApi.keywordsList,
    unpackName: "keywords",
    defaultData: [],
  });
  const keywordsData = keywordsRes.data;

  const [loadingIndices, setLoadingIndices] = useState<number[]>([]);
  const handleDelete = async (id: number, index: number, name: string) => {
    setLoadingIndices((prev) => [...prev, index]);
    try {
      await coreApi.keywordsDestroy(id.toString());
      keywordsRes.refresh();
      notifications.show({
        title: "Key removed",
        message: `🪦 Removed Key: ${name}`,
        color: "#326950",
      });
    } catch (e) {
      notifications.show({
        title: "Error occured!",
        message: STANDARD_ERROR_MESSAGE,
        color: "red",
      });
    } finally {
      setLoadingIndices((prev) => prev.filter((i) => i !== index));
    }
  };
  return (
    <>
      <AddKeywordModal
        opened={opened}
        onClose={close}
        onSuccess={() => {
          keywordsRes.refresh();
          close();
        }}
      />
      {/* Main Content */}
      <Stack align="center">
        <Paper my="md" p="md" w={{ base: "100%", xs: 400 }}>
          <Title order={3}>Welcome back, {user?.username}</Title>

          <Group wrap="nowrap" justify="space-between" mt="sm">
            <Text>No Number Linked 📵</Text>
            <Button variant="outline">Link Number</Button>
          </Group>
        </Paper>
        {/* TODO: Disabled if no phone is added  - TELL USER TO LINK PHOE IN TOOLTIP */}
        <Button
          w={{ base: "100%", xs: 400 }}
          leftSection={<IconBellPlus />}
          onClick={open}
        >
          Add Keyword
        </Button>

        {keywordsRes.loading ? (
          <Group gap="md" mt="xl" style={{ height: "calc(100vh - 450px)" }}>
            <Loader />
            <Text c="grey">Loading Keywords...</Text>
          </Group>
        ) : keywordsData.length > 0 ? (
          keywordsData.map((keyword, index) => (
            <Paper my={5} p="md" w={{ base: "100%", xs: 400 }} key={index}>
              <Group justify="space-between" wrap="nowrap">
                <Stack>
                  <Text>{keyword.name}</Text>

                  <Group>
                    <Group gap={8}>
                      <IconClock color="grey" size={20} stroke={1.8} />
                      <Text c="grey">
                        {timeAgo.format(
                          new Date(keyword.created),
                          "twitter-minute-now"
                        )}
                      </Text>
                    </Group>

                    <Text c="grey">•</Text>
                    <Group gap={8}>
                      <IconBrandTelegram color="grey" size={20} stroke={1.8} />
                      <Text c="grey">12,000</Text>
                    </Group>
                  </Group>
                </Stack>
                <Stack>
                  <ActionIcon
                    variant="subtle"
                    color="#fb8080"
                    loading={loadingIndices.includes(index)}
                    onClick={() =>
                      handleDelete(keyword.id, index, keyword.name)
                    }
                  >
                    <IconTrash />
                  </ActionIcon>
                </Stack>
              </Group>
            </Paper>
          ))
        ) : (
          <Group gap="md" mt="xl" style={{ height: "calc(100vh - 450px)" }}>
            <IconKeyOff size={36} color="grey" />
            <Text c="grey">You have no keywrods</Text>
          </Group>
        )}
      </Stack>
    </>
  );
}
