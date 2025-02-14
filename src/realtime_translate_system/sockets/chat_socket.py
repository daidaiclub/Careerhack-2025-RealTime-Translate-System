from flask_socketio import SocketIO, Namespace
from realtime_translate_system.services import MeetingProcessor


class ChatNamespace(Namespace):
    def __init__(
        self,
        namespace,
        socketio: SocketIO,
        meeting_processor: MeetingProcessor,
    ):
        super().__init__(namespace)
        self.socketio = socketio
        self.meeting_processor = meeting_processor
    
    def on_connect(self):
        print("✅ User connected to chat namespace")

    def on_disconnect(self):
        print("❌ User disconnected from chat namespace")

    def on_user_message(self, data):
        """
        處理使用者傳入的訊息
        """
        print(f"👤 User message: {data['message']}")
        # try:
        response = self.meeting_processor.gen_meeting_summarize(data["message"])
        self.emit("bot_message", {"message": response})
        # except Exception as e:
        #     print(f"❌ Error processing user message: {e}")

    
def init_socketio(
    socketio: SocketIO,
    meeting_processor: MeetingProcessor,
):
    socketio.on_namespace(
        ChatNamespace("/chat", socketio, meeting_processor)
    )
