import createApiClient from "./apiClient";

const coreApiClient = createApiClient();

const keywordsList = () => coreApiClient.get("keywords");

const keywordsCreate = (data: {}) => coreApiClient.post(`keywords`, data);

const keywordsDestroy = (id: string) => coreApiClient.delete(`keywords/${id}`);

const coreApi = {
  keywordsList,
  keywordsCreate,
  keywordsDestroy,
};

export default coreApi;
