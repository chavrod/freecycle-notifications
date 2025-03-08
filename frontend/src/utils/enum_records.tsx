import { ChatStateType, ChatProviderType } from "./api/api_types";
import { Icon, IconBrandTelegram } from "@tabler/icons-react";

export const ChatStateNameAndEmoji: Record<ChatStateType, string> = {
  ACTIVE: "🟢 Notifications ON",
  INACTIVE: "🔴 Notifications OFF",
  SETUP: "📲 Setup",
};

export const ChatStateEmoji: Record<ChatStateType, string> = {
  ACTIVE: "🟢",
  INACTIVE: "🔴",
  SETUP: "📲",
};

export const ChatProviderIcon: Record<ChatProviderType, Icon> = {
  TELEGRAM: IconBrandTelegram,
};

export const ChatProviderColor: Record<ChatProviderType, string> = {
  TELEGRAM: "	#24A1DE",
};
