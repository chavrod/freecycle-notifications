import { Text, Button, TextInput } from "@mantine/core";
import { useForm } from "@mantine/form";
import { notifications } from "@mantine/notifications";
import { IconBellPlus } from "@tabler/icons-react";

import useApiSubmit from "../utils/api/useApiSubmit";
import coreApi from "../utils/api/coreApi";
import { Keyword } from "../utils/api/api_types";

export default function AddKeywordForm({
  submitButtonDisabled,
  onSuccess,
}: {
  submitButtonDisabled: boolean;
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
    <form onSubmit={form.onSubmit(handleSubmit)}>
      <TextInput
        {...form.getInputProps("name")}
        description="Be specific! For example, instead of 'furniture', use 'chair'."
        placeholder="Enter a new keyword"
        mb="md"
      />
      {nonFieldErrors && (
        <Text size="sm" c="red" my="md">
          {nonFieldErrors}
        </Text>
      )}
      <Button
        type="submit"
        fullWidth
        loading={loading}
        w={{ base: "100%", xs: 400 }}
        leftSection={<IconBellPlus />}
        disabled={submitButtonDisabled}
      >
        Add Keyword
      </Button>
    </form>
  );
}
