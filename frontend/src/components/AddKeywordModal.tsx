import { Text, Button, Modal, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { notifications } from "@mantine/notifications";

import useApiSubmit from "./../utils/api/useApiSubmit";
import coreApi from "./../utils/api/coreApi";
import { Keyword } from "../utils/api/api_types";

export default function AddKeywordModal({
  opened,
  onClose,
  onSuccess,
}: {
  opened: boolean;
  onClose: () => void;
  onSuccess: (keyword: Keyword) => void;
}) {
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
    onSuccess: (addKeywrodRes) => {
      close();
      resetAll();
      notifications.show({
        title: "Key added!",
        message: `🔑 New Keywrod Added: ${addKeywrodRes.keyword.name}`,
        color: "#326950",
      });
      onSuccess(addKeywrodRes.keyword);
    },
  });

  return (
    <Modal
      opened={opened}
      centered
      onClose={() => {
        onClose();
        resetAll();
      }}
      title="Add new keyword"
    >
      <form onSubmit={form.onSubmit(handleSubmit)}>
        <TextInput
          {...form.getInputProps("name")}
          description="Be specific! For example, instead of 'furniture', use 'wooden chair'."
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
  );
}
