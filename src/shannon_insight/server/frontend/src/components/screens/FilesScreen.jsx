/**
 * Files screen - delegates to FileListView or FileDetailView
 * based on whether a file detail path is selected.
 */

import useStore from "../../state/store.js";
import { FileListView } from "./files/FileListView.jsx";
import { FileDetailView } from "./files/FileDetailView.jsx";

export function FilesScreen() {
  const currentFileDetail = useStore((s) => s.currentFileDetail);

  if (currentFileDetail) {
    return <FileDetailView path={currentFileDetail} />;
  }

  return <FileListView />;
}
