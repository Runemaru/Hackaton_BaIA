const WS_URL = import.meta.env.VITE_WS_URL;

export function createPredictionSocket({
  onMessage,
  onOpen,
  onClose,
  onError,
}) {
  const socket = new WebSocket(WS_URL);

  socket.onopen = () => {
    console.log("WebSocket conectado");
    onOpen?.();
  };

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    onMessage?.(data);
  };

  socket.onerror = (error) => {
    console.error("Erro no WebSocket:", error);
    onError?.(error);
  };

  socket.onclose = () => {
    console.log("WebSocket desconectado");
    onClose?.();
  };

  return socket;
}
