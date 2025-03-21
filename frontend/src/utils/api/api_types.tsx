export interface Keyword {
  id: number;
  name: string;
  created: string;
  messages_count: number;
}

export enum ChatStateType {
  SETUP = "SETUP",
  ACTIVE = "ACTIVE",
  INACTIVE = "INACTIVE",
}

export enum ChatProviderType {
  TELEGRAM = "TELEGRAM",
}

export interface Chat {
  id: number;
  name: string;
  number: string | null;
  reference: string;
  provider: ChatProviderType;
  state: ChatStateType;
  created_at: string;
}
