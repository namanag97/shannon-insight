/**
 * Hash-based router hook. Syncs location.hash with store navigation state.
 */

import { useEffect } from "preact/hooks";
import useStore from "../state/store.js";

export function useHashRouter() {
  const navigate = useStore((s) => s.navigate);

  useEffect(() => {
    function onHashChange() {
      const h = location.hash.slice(1) || "overview";
      const slashIdx = h.indexOf("/");
      // Pass skipHashUpdate=true to avoid infinite loop
      if (slashIdx > -1) {
        navigate(h.slice(0, slashIdx), decodeURIComponent(h.slice(slashIdx + 1)), true);
      } else {
        navigate(h, undefined, true);
      }
    }

    window.addEventListener("hashchange", onHashChange);

    // Process initial hash
    onHashChange();

    return () => window.removeEventListener("hashchange", onHashChange);
  }, [navigate]);
}
