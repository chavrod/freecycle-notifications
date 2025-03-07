export interface Keyword {
  id: number;
  name: string;
  created: string;
}

export interface Chat {
  id: number;
  name: string;
  number: string;
  reference: string;
  provider: string;
  state: string;
  created_at: string;
}
