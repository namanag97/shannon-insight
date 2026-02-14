/**
 * Root application component. Composes header, progress bar,
 * screen router, and keyboard overlay.
 */

import { useEffect } from "preact/hooks";
import useStore from "../../state/store.js";
import { useWebSocket } from "../../hooks/useWebSocket.js";
import { useKeyboard } from "../../hooks/useKeyboard.js";
import { useHashRouter } from "../../hooks/useHashRouter.js";
import { Header } from "./Header.jsx";
import { ProgressBar } from "./ProgressBar.jsx";
import { KeyboardOverlay } from "./KeyboardOverlay.jsx";
import { OverviewScreen } from "../screens/OverviewScreen.jsx";
import { IssuesScreen } from "../screens/IssuesScreen.jsx";
import { FilesScreen } from "../screens/FilesScreen.jsx";
import { ModulesScreen } from "../screens/ModulesScreen.jsx";
import { HealthScreen } from "../screens/HealthScreen.jsx";
import { GraphScreen } from "../screens/GraphScreen.jsx";
import { ChurnScreen } from "../screens/ChurnScreen.jsx";
import { SignalInspectorScreen } from "../screens/SignalInspectorScreen.jsx";

export function App() {
  const currentScreen = useStore((s) => s.currentScreen);
  const setData = useStore((s) => s.setData);

  // Initialize hooks
  useWebSocket();
  useKeyboard();
  useHashRouter();

  // Fetch initial state
  useEffect(() => {
    fetch("/api/state")
      .then((r) => r.json())
      .then((data) => {
        if (data && data.health != null) {
          setData(data);
        }
      })
      .catch(() => {});
  }, []);

  return (
    <>
      <ProgressBar />
      <Header />
      <div class="main">
        <div class={`screen${currentScreen === "overview" ? " active" : ""}`} id="screen-overview">
          {currentScreen === "overview" && <OverviewScreen />}
        </div>
        <div class={`screen${currentScreen === "issues" ? " active" : ""}`} id="screen-issues">
          {currentScreen === "issues" && <IssuesScreen />}
        </div>
        <div class={`screen${currentScreen === "files" ? " active" : ""}`} id="screen-files">
          {currentScreen === "files" && <FilesScreen />}
        </div>
        <div class={`screen${currentScreen === "modules" ? " active" : ""}`} id="screen-modules">
          {currentScreen === "modules" && <ModulesScreen />}
        </div>
        <div class={`screen${currentScreen === "health" ? " active" : ""}`} id="screen-health">
          {currentScreen === "health" && <HealthScreen />}
        </div>
        <div class={`screen${currentScreen === "graph" ? " active" : ""}`} id="screen-graph">
          {currentScreen === "graph" && <GraphScreen />}
        </div>
        <div class={`screen${currentScreen === "churn" ? " active" : ""}`} id="screen-churn">
          {currentScreen === "churn" && <ChurnScreen />}
        </div>
        <div class={`screen${currentScreen === "signals" ? " active" : ""}`} id="screen-signals">
          {currentScreen === "signals" && <SignalInspectorScreen />}
        </div>
      </div>
      <KeyboardOverlay />
    </>
  );
}
