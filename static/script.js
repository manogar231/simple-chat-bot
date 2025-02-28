async function sendMessage() {
    let messageInput = document.getElementById("message");
    let message = messageInput.value.trim();
    if (!message) return;  // Don't send empty messages

    let response = await fetch("/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `message=${encodeURIComponent(message)}`
    });

    let data = await response.json();
    let chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `<p class="user"><b>You:</b> ${message}</p>`;
    chatBox.innerHTML += `<p class="bot"><b>Bot:</b> ${data.response}</p>`;

    messageInput.value = "";  // Clear input after sending
    chatBox.scrollTop = chatBox.scrollHeight;  // Auto-scroll to the latest message
}

// Listen for "Enter" key press in the input field
document.getElementById("message").addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();  // Prevent newline in input field
        sendMessage();  // Call send function
    }
});
