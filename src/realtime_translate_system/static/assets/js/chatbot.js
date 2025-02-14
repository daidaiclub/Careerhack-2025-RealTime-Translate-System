import { chatSocket } from "./socket.js";

export function chat(val) {
  // 使用者送出訊息後，先將訊息加入畫面
  addChatMessage(val, "user");
  chatSocket.emit("user_message", {
    message: val,
  });
  const $chatInput = $("#chat-input");
  $chatInput.val("");
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
  return $(`
    <div class="message-container ai">
      <div class="message-ai">${message}</div>
    </div>
  `)
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
