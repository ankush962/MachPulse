export function connectMonitor({
  machineId = "M01",
  demo = true,
  onMessage,
  onOpen,
  onClose,
  onError,
}) {
  const baseUrl =
    import.meta.env.VITE_WS_URL ||
    "ws://localhost:8000";

  const path = demo
    ? `/ws/demo/${machineId}`
    : `/ws/monitor/${machineId}`;

  const socket = new WebSocket(
    `${baseUrl}${path}`
  );

  socket.onopen = () => {
    onOpen?.();
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(
        event.data
      );

      onMessage?.(data);
    } catch (error) {
      console.error(
        "Invalid WebSocket message:",
        error
      );
    }
  };

  socket.onclose = () => {
    onClose?.();
  };

  socket.onerror = (event) => {
    onError?.(event);
  };

  return socket;
}