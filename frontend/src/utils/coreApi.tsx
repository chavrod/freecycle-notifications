import createApiClient from "./apiClient";

const coreApiClient = createApiClient("/core/");

const list = () => coreApiClient.get("products");

const create = (data: {}) => coreApiClient.post(`products`, data);

const update = (id: string, data: {}) =>
  coreApiClient.delete(`products/${id}`, data);

const destroy = (id: string) => coreApiClient.delete(`products/${id}`);

const coreApi = {
  list,
  create,
  update,
  destroy,
};

export default coreApi;
