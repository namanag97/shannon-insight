/**
 * Files screen - delegates to FileListView or FileDetailView
 * based on whether a file detail path is selected.
 */

import useStore from "../../state/store.js";
// Import v2 redesigned views
import { FileListViewV2 as FileListView } from "./files/FileListView.v2.jsx";
import { FileDetailViewV2 as FileDetailView } from "./files/FileDetailView.v2.jsx";

export function FilesScreen() {
  const currentFileDetail = useStore((s) => s.currentFileDetail);

  if (currentFileDetail) {
    return <FileDetailView path={currentFileDetail} />;
  }

  return <FileListView />;
}
