import { apiRequest } from "../../shared/api/client";
import { fileResponseSchema, type FileAccessScope } from "./file.schema";

export type UploadFilePayload = {
  file: File;
  access_scope?: FileAccessScope;
};

export type UpdateFilePayload = {
  access_scope: FileAccessScope;
};

export async function uploadFile(payload: UploadFilePayload) {
  const formData = new FormData();
  formData.set("file", payload.file);
  formData.set("access_scope", payload.access_scope ?? "private");

  return apiRequest("/files", { method: "POST", body: formData }, fileResponseSchema);
}

export async function updateFile(fileId: number, payload: UpdateFilePayload) {
  return apiRequest(`/files/${fileId}`, { method: "PATCH", body: payload }, fileResponseSchema);
}

export async function deleteFile(fileId: number) {
  return apiRequest<{ message: string }>(`/files/${fileId}`, { method: "DELETE" });
}
