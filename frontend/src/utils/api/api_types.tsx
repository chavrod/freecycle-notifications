export interface Keyword {
  id: number;
  name: string;
  created: string;
}

export enum ChatStateType {
  SETUP = "SETUP",
  ACTIVE = "ACTIVE",
  INACTIVE = "INACTIVE",
}

export interface Chat {
  id: number;
  name: string;
  number: string;
  reference: string;
  provider: string;
  state: ChatStateType;
  created_at: string;
}
