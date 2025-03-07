import createApiClient from "./apiClient";

const coreApiClient = createApiClient();

const keywordsList = () => coreApiClient.get("keywords/");

const keywordsCreate = (data: {}) => coreApiClient.post(`keywords/`, data);

const keywordsDestroy = (id: string) => coreApiClient.delete(`keywords/${id}/`);

const chatsList = () => coreApiClient.get("chats/");

const chatsLink = () => coreApiClient.post("chats/link_chat/");

const chatsGetBySessionUuid = (uuid: string) =>
  coreApiClient.get(`chats/${uuid}/get_chat_by_session_uuid/`);

const coreApi = {
  keywordsList,
  keywordsCreate,
  keywordsDestroy,
  chatsList,
  chatsLink,
  chatsGetBySessionUuid,
};

export default coreApi;
