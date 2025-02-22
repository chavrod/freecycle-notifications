import {
  Stack,
  Title,
  Text,
  Paper,
  Group,
  ActionIcon,
  Button,
} from "@mantine/core";
import TimeAgo from "javascript-time-ago";
import en from "javascript-time-ago/locale/en";

import { useUser } from "./auth/hooks";
import useApi from "./utils/api/useApi";
import coreApi from "./utils/api/coreApi";
import { Keyword } from "./utils/api/api_types";
import {
  IconTrash,
  IconBrandTelegram,
  IconClock,
  IconBellPlus,
} from "@tabler/icons-react";

export default function DashboardPage() {
  TimeAgo.addLocale(en);
  const timeAgo = new TimeAgo("en-US");

  const user = useUser();

  const keywordsRes = useApi<Keyword[]>({
    apiFunc: coreApi.keywordsList,
    unpackName: "keywords",
    defaultData: [],
  });
  const keywordsData = keywordsRes.data;

  return (
    <Stack align="center">
      <Paper my="md" p="md" w={{ base: "100%", xs: 400 }}>
        <Title order={3}>Welcome back, {user?.username}</Title>

        <Group wrap="nowrap" justify="space-between" mt="sm">
          <Text>No Number Linked 📵</Text>
          <Button variant="outline">Link Number</Button>
        </Group>
      </Paper>
      {/* TODO: Disabled if no phone is added  - TELL USER TO LINK PHOE IN TOOLTIP */}
      <Button w={{ base: "100%", xs: 400 }} leftSection={<IconBellPlus />}>
        Add Keyword
      </Button>

      {keywordsData.length > 0 ? (
        keywordsData.map((keyword, index) => (
          <Paper my={5} p="md" w={{ base: "100%", xs: 400 }} key={index}>
            <Group justify="space-between" wrap="nowrap">
              <Stack>
                <Text>{keyword.name}</Text>

                <Group>
                  <Group gap={8}>
                    <IconClock color="grey" size={20} stroke={1.8} />
                    <Text c="grey">
                      {timeAgo.format(new Date(keyword.created), "twitter")}
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
                <ActionIcon variant="subtle" color="#fb8080">
                  <IconTrash />
                </ActionIcon>
              </Stack>
            </Group>
          </Paper>
        ))
      ) : (
        <></>
      )}
    </Stack>
  );
}
