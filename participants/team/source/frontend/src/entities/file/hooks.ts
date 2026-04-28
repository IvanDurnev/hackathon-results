import { useMutation } from "@tanstack/react-query";

import { deleteFile, updateFile, uploadFile } from "./api";

export function useUploadFile() {
  return useMutation({
    mutationFn: uploadFile
  });
}

export function useUpdateFile() {
  return useMutation({
    mutationFn: ({ fileId, payload }: { fileId: number; payload: Parameters<typeof updateFile>[1] }) =>
      updateFile(fileId, payload)
  });
}

export function useDeleteFile() {
  return useMutation({
    mutationFn: deleteFile
  });
}
