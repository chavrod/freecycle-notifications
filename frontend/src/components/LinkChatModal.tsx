import { Text, Button, Modal, Stack, Group, ThemeIcon } from "@mantine/core";
import { IconInfoCircle } from "@tabler/icons-react";

import useApiAction from "../utils/api/useApiAction";
import coreApi from "./../utils/api/coreApi";
import { Keyword } from "../utils/api/api_types";

export default function LinkChatModal({
  opened,
  onClose,
  onSuccess,
}: {
  opened: boolean;
  onClose: () => void;
  onSuccess: (keyword: Keyword) => void;
}) {
  // TODO: we should check if chat is linked, and force close the chat
  // ALSO from the outside do not allow opening chat if linked..

  // TODO:
  // Think how user may fuck up
  // Chat linking in Progress... then allow to re-initiate?
  // BUT do check every 5 sec if chat is linked??? - RATE LIMIT?

  const {
    handleSubmit: requestToLinkChat,
    loading,
    errors,
    resetAll,
  } = useApiAction({
    apiFunc: coreApi.linkChat,
    onSuccess: (linkingSessionRes) => {
      const linkingSessionUuid = linkingSessionRes.linking_session;
      console.log("linkingSessionUuid: ", linkingSessionUuid);
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
      title="Link Number"
    >
      <Stack>
        <Group gap="xs">
          <ThemeIcon variant="light">
            <IconInfoCircle size={"1.2rem"} />
          </ThemeIcon>
          <Text fw={700}>Info</Text>
        </Group>
        <Text size="md">You must have a Telegram account setup.</Text>
        <Text size="md">
          If using from mobile, make sure you have Telegram app installed.
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
      >
        Confirm
      </Button>
    </Modal>
  );
}
