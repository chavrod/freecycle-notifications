import { useState } from "react";
import { Modal, Button, Text, Input, Stack, Group } from "@mantine/core";
import { IconCircleCheckFilled } from "@tabler/icons-react";

import { logout } from "../auth/api";
import useApiAction from "../utils/api/useApiAction";
import coreApi from "../utils/api/coreApi";

interface DeleteAccountModalProps {
  isOpen: boolean;
  onClose: Function;
}

function DeleteAccountModal({ isOpen, onClose }: DeleteAccountModalProps) {
  const [confirmed, setConfirmed] = useState(false);
  const [isDeleted, setIsDeleted] = useState(false);

  const {
    handleSubmit: handleDelete,
    loading,
    errors,
    resetAll,
  } = useApiAction({
    apiFunc: coreApi.accountDelete,
    onSuccess: () => {
      setIsDeleted(true);
      setTimeout(() => {
        logout();
      }, 3000);
    },
  });

  return (
    <Modal
      opened={isOpen}
      onClose={() => {
        onClose();
        resetAll();
      }}
      title="Delete Account"
      centered
    >
      {isDeleted ? (
        <Stack justify="center" style={{ textAlign: "center" }} align="center">
          <IconCircleCheckFilled
            size={80}
            style={{ color: "#326950", marginBottom: "10px" }}
          />
          <Text style={{ textAlign: "center" }}>
            Your account has been successfully deleted. You will be redirected
            to the homepage.
          </Text>
        </Stack>
      ) : (
        <>
          <Text>
            Deleting your account is a permanent action and cannot be undone.
            Please type &apos;DELETE&apos; below to confirm.
          </Text>
          <Input
            mt="sm"
            placeholder="Type DELETE to confirm"
            onChange={(e: any) => setConfirmed(e.target.value === "DELETE")}
          />
          <Group align="right">
            <Button
              mt="sm"
              color="red"
              fullWidth
              loading={loading}
              disabled={!confirmed || loading}
              onClick={handleDelete}
            >
              Confirm Deletion
            </Button>
            {errors && (
              <Text size="sm" c="red" my="md">
                {errors}
              </Text>
            )}
          </Group>
        </>
      )}
    </Modal>
  );
}

export default DeleteAccountModal;
