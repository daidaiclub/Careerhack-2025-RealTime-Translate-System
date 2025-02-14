import { chatSocket } from "./socket.js";

export function chat(val) {
  // 使用者送出訊息後，先將訊息加入畫面
  addChatMessage(val, "user");
  const loadingMessage = addLoadingMessage();
  $("#chat-messages").append(loadingMessage);
  $("#chat-input").val("");
  
  chatSocket.emit("user_message", {
    message: val,
  });
  chatSocket.once("bot_message", (data) => {
    loadingMessage.remove(); // 移除「AI 思考中...」
    addChatMessage(data["message"], "ai"); // 顯示 AI 回應
  });
}

chatSocket.on("bot_message", (data) => {
  // 收到 AI 回傳的訊息後，將訊息加入畫面
  console.log(data);
  addChatMessage(data["message"], "ai");
});

function addRetrivalMessage(messages) {
  const $container = $(`
    <div class="message-container ai">
      <div class="message-ai">
        <ul>
          ${messages.map(message => `
          <li>
            <span class="clickable" data-id="${message.id}"
              style="cursor: pointer; color: white; text-decoration: underline;">
              ${message.title}
            </span>
            </a>
          </li>
          `).join('')}
        </ul>
      </div>
    </div>
  `);

  $container.on('click', '.clickable', function () {
    const id = $(this).data('id');
    window.history.pushState({}, "", "/" + id);
  });

  return $container;
}


function addSummarizationMessage(message) {
  // 讓 **粗體** 文字的前面加上換行
  const formattedMessage = message
    .replace(/\*\*(.*?)\*\*/g, "<br><strong>$1</strong>") // 替換 **粗體** 為 <strong> 並在前面加 <br>
    .replace(/(<br>)+/g, "<br>"); // 避免多個 <br> 連續出現

  return $(`
    <div class="message-container ai">
      <div class="message-ai">${formattedMessage}</div>
    </div>
  `);
}

function addChatMessage(message, type) {
  const $chatMessages = $("#chat-messages");
  let messageElement;

  if (type === "user") {
    messageElement = $(`
      <div class="message-container user">
        <div class="message-user">${message}</div>
      </div>
    `);
  } else {
    if (message instanceof Array) {
      messageElement = addRetrivalMessage(message);
    } else {
      messageElement = addSummarizationMessage(message);
    }
  }

  $chatMessages.append(messageElement);
  // 保持捲動在最底部
  $chatMessages.scrollTop($chatMessages[0].scrollHeight);
}

function addLoadingMessage() {
  return $(`
    <div class="message-container ai">
      <div class="message-ai">AI is typing...</div>
    </div>
  `);
}