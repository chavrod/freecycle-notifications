import createApiClient from "./apiClient";

const coreApiClient = createApiClient();

const keywordsList = () => coreApiClient.get("keywords/");

const keywordsCreate = (data: {}) => coreApiClient.post(`keywords/`, data);

const keywordsDestroy = (id: string) => coreApiClient.delete(`keywords/${id}/`);

const linkChat = () => coreApiClient.post("chats/link_chat/");

const coreApi = {
  keywordsList,
  keywordsCreate,
  keywordsDestroy,
  linkChat,
};

export default coreApi;
