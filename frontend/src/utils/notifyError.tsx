import { notifications } from "@mantine/notifications";
import { IconX } from "@tabler/icons-react";

type NotiftErrorProps = {
  message: string;
  title?: string;
};

export default function notifyError({ message, title }: NotiftErrorProps) {
  notifications.show({
    title: title || "Error",
    message,
    icon: <IconX size="1rem" />,
    color: "red",
    withBorder: true,
  });
}
