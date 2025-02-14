export const audioSocket = io("/audio_stream", { path: "/socket.io" });
export const chatSocket = io("/chat", { path: "/socket.io" });

audioSocket.on("connect", () => {
  console.log("Connected to /audio_stream, id:", audioSocket.id);
});
audioSocket.on("disconnect", (reason) => {
  console.log("Disconnected from /audio_stream, reason:", reason);
});
audioSocket.on("error", (err) => {
  console.error("Socket error:", err);
});