document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    // The FastAPI backend URL
    const API_URL = 'http://127.0.0.1:8000/chat/';

    /**
     * Utility: Auto-scroll to the bottom of the chat container
     */
    const scrollToBottom = () => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    /**
     * Listen for input changes to toggle the disabled state of the send button
     */
    userInput.addEventListener('input', () => {
        sendBtn.disabled = userInput.value.trim() === '';
    });

    /**
     * Listen for "Enter" keypress in the input field to send a message
     */
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !sendBtn.disabled) {
            sendMessage();
        }
    });

    /**
     * Listen for click on the send button
     */
    sendBtn.addEventListener('click', sendMessage);

    /**
     * Creates and appends a message element to the chat UI
     * @param {string} text - The message body
     * @param {string} sender - 'user' or 'bot'
     */
    function appendMessage(text, sender) {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message');
        msgDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
        msgDiv.textContent = text;
        
        chatMessages.appendChild(msgDiv);
        scrollToBottom();
    }

    /**
     * Displays a temporary typing indicator to simulate processing time
     */
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.classList.add('message', 'bot-message', 'typing-indicator');
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        chatMessages.appendChild(typingDiv);
        scrollToBottom();
    }

    /**
     * Removes the typing indicator before placing the actual message
     */
    function removeTypingIndicator() {
        const typingDiv = document.getElementById('typing-indicator');
        if (typingDiv) {
            typingDiv.remove();
        }
    }

    /**
     * Core function to handle sending the message and fetching the API
     */
    async function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Display user message
        appendMessage(message, 'user');
        
        // Reset and disable input area
        userInput.value = '';
        sendBtn.disabled = true;

        // Show typing indicator
        showTypingIndicator();

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                // Build JSON payload expected by ChatRequest schema
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                throw new Error(`Server returned status: ${response.status}`);
            }

            const data = await response.json();
            
            // Artificial delay (optional) for a more human feel, 
            // but we can remove it to make it instantly responsive
            removeTypingIndicator();
            
            // Extract the 'reply' from the response
            if (data.reply) {
                appendMessage(data.reply, 'bot');
            } else {
                appendMessage("I couldn't generate a response. Please try again.", 'bot');
            }

        } catch (error) {
            console.error('Error hitting chat API:', error);
            removeTypingIndicator();
            // Handle network or down-server errors gracefully
            appendMessage("Sorry, I'm having trouble connecting to my servers right now. Are they running?", 'bot');
        }
    }
});
