import { ChatStateType } from "./api/api_types";

export const ChatProviderNamesAndEmoji: Record<ChatStateType, string> = {
  ACTIVE: "🟢 Receiving Notifications",
  INACTIVE: "🔴 Inactive",
  SETUP: "📲 Setup",
};
