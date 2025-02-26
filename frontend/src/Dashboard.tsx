import {
  Stack,
  Title,
  Text,
  Paper,
  Group,
  ActionIcon,
  Button,
  Modal,
  TextInput,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import TimeAgo from "javascript-time-ago";
import en from "javascript-time-ago/locale/en";

import { useUser } from "./auth/hooks";
import useApi from "./utils/api/useApi";
import useApiSubmit from "./utils/api/useApiSubmit";
import coreApi from "./utils/api/coreApi";
import { Keyword } from "./utils/api/api_types";
import {
  IconTrash,
  IconBrandTelegram,
  IconClock,
  IconBellPlus,
} from "@tabler/icons-react";
import { useForm } from "@mantine/form";

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

  const form = useForm({
    initialValues: {
      name: "",
    },

    validate: {
      name: (value) =>
        value.trim().length < 3 ? "3 letters minimum please." : null,
    },
  });

  const { handleSubmit, loading, nonFieldErrors, resetAll } = useApiSubmit({
    form: form,
    apiFunc: (formData: typeof form.values) => coreApi.keywordsCreate(formData),
    onSuccess: () => {
      close();
      resetAll();
      // TODO: Potnetially just add new keyowrd to the top as oppose to refetching?
      keywordsRes.refresh();
    },
  });

  return (
    <>
      {/* Modal for Adding Keywords */}
      <Modal
        opened={opened}
        onClose={() => {
          close();
          resetAll();
        }}
        title="Add new keyword"
      >
        {/* TODO: Refactor into its own component....  */}
        <form onSubmit={form.onSubmit(handleSubmit)}>
          <TextInput
            {...form.getInputProps("name")}
            label="Keyword"
            placeholder="Enter a new keyword"
            mb="md"
          />
          {nonFieldErrors && (
            <Text size="sm" c="red" my="md">
              {nonFieldErrors}
            </Text>
          )}
          <Button type="submit" fullWidth loading={loading}>
            Add Keyword
          </Button>
        </form>
      </Modal>
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
    </>
  );
}
