let chatSocket;

function initializeWebSocket() {
    const messageContainer = document.getElementById('chat-messages');
    const threadId = messageContainer.dataset.threadId;
    const userName = messageContainer.dataset.userName;

    const wsUrl = 'ws://' + window.location.host + '/ws/messaging/thread/' + threadId + '/';
    console.log("Initializing WebSocket connection to:", wsUrl);

    if (chatSocket && chatSocket.readyState !== WebSocket.CLOSED) {
        console.log("WebSocket connection already active.");
        return;
    }

    chatSocket = new WebSocket(wsUrl);

    chatSocket.onopen = function () {
        console.log("WebSocket connection established.");
    };

    chatSocket.onerror = function (e) {
        console.error("WebSocket encountered an error:", e);
    };

    chatSocket.onmessage = function (e) {
        console.log("Message received from WebSocket:", e.data);
        const data = JSON.parse(e.data);
        const messageContainer = document.getElementById('chat-messages');
        const msgDiv = document.createElement('div');
        const isCurrentUser = data.sender === userName;

        // Generar timestamp local si no está presente en el mensaje recibido
        const timestamp = data.timestamp || new Date().toLocaleString('es-ES', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });

        // Aplica las mismas clases y estilos que los mensajes renderizados desde el servidor
        msgDiv.className = `mb-2 d-flex ${isCurrentUser ? 'justify-content-end' : 'justify-content-start'}`;
        msgDiv.innerHTML = `
            <div class="p-2 ${isCurrentUser ? 'bg-warning text-dark' : 'bg-light text-dark'} rounded">
                <span class="fw-bold">${data.sender.split(' ')[0]}:</span>
                <span>${data.message}</span>
                <small class="text-muted d-block">${timestamp}</small>
            </div>
        `;

        messageContainer.appendChild(msgDiv);
        messageContainer.scrollTop = messageContainer.scrollHeight;
        console.log("Message appended to chat and scrolled to bottom.");
    };

    chatSocket.onclose = function (e) {
        console.warn("WebSocket connection closed:", e);
        if (!window.isUnloading) {
            console.log("Attempting to reconnect WebSocket...");
            setTimeout(initializeWebSocket, 3000);
        }
    };
}

// Función para habilitar/deshabilitar el botón "Enviar"
function setupMessageInput() {
    const inputField = document.getElementById('chat-message-input');
    const submitButton = document.getElementById('chat-submit-button');

    inputField.addEventListener('input', function () {
        submitButton.disabled = inputField.value.trim() === '';
    });
}

// Manejar el envío de mensajes
document.getElementById('chat-form').onsubmit = function (e) {
    e.preventDefault();
    const input = document.getElementById('chat-message-input');
    const message = input.value;
    console.log("Attempting to send message:", message);

    if (message.trim() !== '' && chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        console.log("WebSocket is open. Sending message...");

        // Envía solo el mensaje al servidor; el servidor generará el timestamp
        chatSocket.send(JSON.stringify({
            'message': message
        }));

        input.value = '';
        console.log("Message sent successfully.");

        // Recargar la página después de enviar el mensaje
        location.reload();
    } else {
        console.warn("Message not sent. WebSocket is not open or message is empty.");
        console.log("WebSocket readyState:", chatSocket ? chatSocket.readyState : "No WebSocket instance");
    }
};

// Inicializar WebSocket y configurar el botón "Enviar" cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM fully loaded. Initializing WebSocket and setting up message input.");
    initializeWebSocket();
    scrollToLastMessage();
    setupMessageInput();
});

// Función para hacer scroll al último mensaje
function scrollToLastMessage() {
    const messageList = document.getElementById('chat-messages');
    if (messageList) {
        console.log("Scrolling to the last message.");
        messageList.scrollTop = messageList.scrollHeight;
    } else {
        console.error("Element #chat-messages not found.");
    }
}

// Marcar cuando la página se está descargando para evitar reconexiones innecesarias
window.addEventListener('beforeunload', function () {
    console.log("Page is unloading. Closing WebSocket connection.");
    window.isUnloading = true;
    if (chatSocket) {
        chatSocket.close();
    }
});