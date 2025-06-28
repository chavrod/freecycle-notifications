import { Stack, Text, Paper, Group, Button, Title } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";

import DeleteAccountModal from "../components/DeleteAccountModal";
import { useState } from "react";

export default function ManageAccount() {
  const [modalMode, setModalMode] = useState("");
  const [opened, { open, close }] = useDisclosure(false);

  const handleModalClose = () => {
    setModalMode("");
    close();
  };

  return (
    <>
      {modalMode === "delete_account" && (
        <DeleteAccountModal isOpen={opened} onClose={handleModalClose} />
      )}
      {/* Main Content */}
      <Stack align="center">
        <Title order={3} mt="xl">
          Account Settings
        </Title>

        <Text style={{ textAlign: "center" }}>
          Not much you can do here atm.
        </Text>

        <Paper my="md" p="md" w={{ base: "100%", xs: 400 }}>
          <Group wrap="nowrap" justify="space-between">
            <Text>Delete Your Account</Text>
            <Button
              onClick={() => {
                setModalMode("delete_account");
                open();
              }}
              variant="outline"
              color="red"
            >
              Proceed
            </Button>
          </Group>
        </Paper>
      </Stack>
    </>
  );
}
