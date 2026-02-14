/**
 * WebSocket hook - manages connection lifecycle, auto-reconnect,
 * and message dispatch to the store.
 */

import { useEffect, useRef } from "preact/hooks";
import useStore from "../state/store.js";

export function useWebSocket() {
  const wsRef = useRef(null);
  const retryDelayRef = useRef(1000);
  const { setData, setConnectionStatus, setProgress, setReconnectActive } = useStore();

  useEffect(() => {
    function connect() {
      const proto = location.protocol === "https:" ? "wss:" : "ws:";
      const ws = new WebSocket(proto + "//" + location.host + "/ws");
      wsRef.current = ws;

      ws.onopen = () => {
        retryDelayRef.current = 1000;
        setReconnectActive(false);
        setConnectionStatus("connected", "");
      };

      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data);
          if (msg.type === "complete") {
            setData(msg.state);
            setConnectionStatus("connected", "");
            setProgress(false, null, "");
          } else if (msg.type === "progress") {
            setConnectionStatus("analyzing", msg.message || "analyzing");
            setProgress(true, msg.percent, msg.message);
          } else if (msg.type === "error") {
            setConnectionStatus("disconnected", "error");
            setProgress(false, null, "");
          }
          // Ignore "ping" messages silently
        } catch (err) {
          console.error("ws parse:", err);
        }
      };

      ws.onclose = () => {
        setConnectionStatus("disconnected", "");
        setReconnectActive(true);
        const delay = retryDelayRef.current;
        retryDelayRef.current = Math.min(delay * 1.5, 15000);
        setTimeout(connect, delay);
      };

      ws.onerror = () => {
        setConnectionStatus("disconnected", "");
      };
    }

    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.onclose = null; // Prevent reconnect on cleanup
        wsRef.current.close();
      }
    };
  }, []);
}
