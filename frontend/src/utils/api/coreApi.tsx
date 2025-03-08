import createApiClient from "./apiClient";

const coreApiClient = createApiClient();

const keywordsList = () => coreApiClient.get("keywords/");

const keywordsCreate = (data: {}) => coreApiClient.post(`keywords/`, data);

const keywordsDestroy = (id: string) => coreApiClient.delete(`keywords/${id}/`);

const chatsList = () => coreApiClient.get("chats/");

const chatsCreate = () => coreApiClient.post("chats/");

const chatsDestroy = (id: string) => coreApiClient.delete(`chats/${id}/`);

const chatsGetBySessionUuid = (uuid: string) =>
  coreApiClient.get(`chats/${uuid}/get_chat_by_session_uuid/`);

const chatsToggleState = (id: string) =>
  coreApiClient.post(`chats/${id}/toggle_state/`);

const coreApi = {
  keywordsList,
  keywordsCreate,
  keywordsDestroy,
  chatsList,
  chatsCreate,
  chatsDestroy,
  chatsGetBySessionUuid,
  chatsToggleState,
};

export default coreApi;
