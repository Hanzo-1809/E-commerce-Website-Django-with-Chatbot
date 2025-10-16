/**
 * Enhanced Chatbot for JBook.com
 * Supports multi-turn conversations, message history, and product queries
 */

const chatbotToggle = document.querySelector('.chatbot-toggle');
const chatbotContainer = document.querySelector('.chatbot-container');
const sendBtn = document.getElementById('send-btn');
const userInput = document.getElementById('user-input');
const chatbotBody = document.getElementById('chatbot-body');

// Track if this is first open
let firstOpen = true;

// Format and display messages
function addMessage(text, isUser = false) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

  // Process text to handle URLs and line breaks
  const processedText = text
    .replace(/\n/g, '<br>')
    // Make URLs clickable
    .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');

  messageDiv.innerHTML = processedText;
  chatbotBody.appendChild(messageDiv);
  chatbotBody.scrollTop = chatbotBody.scrollHeight;

  return messageDiv;
}

// Add loading animation when chatbot is processing
function showLoadingAnimation() {
  const loadingDiv = document.createElement('div');
  loadingDiv.className = 'message bot-message loading';
  loadingDiv.id = 'loading-message';
  loadingDiv.innerHTML = '<div class="dot-flashing"></div>';
  chatbotBody.appendChild(loadingDiv);
  chatbotBody.scrollTop = chatbotBody.scrollHeight;
}

function removeLoadingAnimation() {
  const loadingMessage = document.getElementById('loading-message');
  if (loadingMessage) {
    loadingMessage.remove();
  }
}

// Save chat history to local storage
function saveChatHistory() {
  if (chatbotBody.childElementCount > 0) {
    const messages = [];
    chatbotBody.querySelectorAll('.message').forEach(msg => {
      messages.push({
        text: msg.innerText,
        isUser: msg.classList.contains('user-message')
      });
    });

    if (messages.length > 0) {
      localStorage.setItem('jbook_chat_history', JSON.stringify(messages));
    }
  }
}

// Load chat history from local storage
function loadChatHistory() {
  try {
    const savedHistory = localStorage.getItem('jbook_chat_history');
    if (savedHistory) {
      const messages = JSON.parse(savedHistory);
      messages.forEach(msg => {
        addMessage(msg.text, msg.isUser);
      });
      return messages.length > 0;
    }
  } catch (e) {
    console.error('Error loading chat history:', e);
    // Clear possibly corrupted history
    localStorage.removeItem('jbook_chat_history');
  }
  return false;
}

// Initial greeting when chatbot is opened
function showInitialGreeting() {
  const initialGreeting = "Xin chào! Tôi là trợ lý ảo của JBook.com. Tôi có thể giúp bạn tìm sách, trả lời câu hỏi về đơn hàng hoặc cung cấp thông tin về cửa hàng. Bạn cần giúp gì?";
  addMessage(initialGreeting);
}

// Add suggestions for common queries
function addSuggestionButtons() {
  const suggestionsDiv = document.createElement('div');
  suggestionsDiv.className = 'chatbot-suggestions';

  const suggestions = [
    "Sách mới nhất?",
    "Cách đặt hàng",
    "Phí vận chuyển",
    "Khuyến mãi hiện tại"
  ];

  suggestions.forEach(text => {
    const button = document.createElement('button');
    button.className = 'suggestion-btn';
    button.textContent = text;
    button.addEventListener('click', () => {
      userInput.value = text;
      sendBtn.click();
    });
    suggestionsDiv.appendChild(button);
  });

  chatbotBody.appendChild(suggestionsDiv);
}

// Show or hide chatbot
chatbotToggle.addEventListener('click', () => {
  const isVisible = chatbotContainer.style.display === 'flex';

  chatbotContainer.style.display = isVisible ? 'none' : 'flex';

  if (!isVisible) {
    // If opening the chatbot
    const hasHistory = loadChatHistory();

    // Show greeting and suggestions only on first open or if no history
    if (firstOpen || !hasHistory) {
      showInitialGreeting();
      addSuggestionButtons();
      firstOpen = false;
    }

    // Focus the input field
    userInput.focus();
  } else {
    // If closing the chatbot, save the chat history
    saveChatHistory();
  }
});

// Send message to the chatbot
sendBtn.addEventListener('click', () => {
  const userText = userInput.value.trim();
  if (!userText) return;

  // Remove suggestion buttons if present
  const suggestions = document.querySelector('.chatbot-suggestions');
  if (suggestions) {
    suggestions.remove();
  }

  // Add user message to chat
  addMessage(userText, true);

  // Clear input and disable button while waiting
  userInput.value = '';
  sendBtn.disabled = true;
  userInput.disabled = true;

  // Show loading animation
  showLoadingAnimation();
  // Send request to server
  console.log('Gửi yêu cầu đến DeepSeek API với tin nhắn:', userText);
  
  const requestData = { message: userText };
  console.log('Dữ liệu gửi đi:', requestData);
  console.log('CSRF Token:', csrf_token);
  
  fetch('/chat/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrf_token
    },
    body: JSON.stringify(requestData)
  })
    .then(response => {
      console.log('Nhận phản hồi từ server với mã trạng thái:', response.status);
      return response.json();
    })
    .then(data => {
      console.log('Dữ liệu phản hồi từ server:', data);
      
      // Remove loading animation
      removeLoadingAnimation();

      // Add bot's response to chat
      addMessage(data.reply);

      // Save chat history
      saveChatHistory();

      // Re-enable button and input
      sendBtn.disabled = false;
      userInput.disabled = false;
      userInput.focus();
    })    .catch(error => {
      console.error('Lỗi khi gọi API chatbot:', error);
      console.error('Chi tiết lỗi:', JSON.stringify(error, null, 2));
      removeLoadingAnimation();
      addMessage("Xin lỗi, có lỗi xảy ra khi gửi yêu cầu đến chatbot. Vui lòng thử lại sau.", false);
      sendBtn.disabled = false;
      userInput.disabled = false;
    });
});

// Send message when Enter key is pressed
userInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter' && !sendBtn.disabled) {
    sendBtn.click();
  }
});

// Close chatbot when clicking outside of it
document.addEventListener('click', (e) => {
  if (!chatbotContainer.contains(e.target) &&
    !chatbotToggle.contains(e.target) &&
    chatbotContainer.style.display === 'flex') {
    chatbotContainer.style.display = 'none';
    saveChatHistory();
  }
});

// Clear chat history functionality
function addClearChatButton() {
  const headerDiv = document.querySelector('.chatbot-header');

  const clearButton = document.createElement('button');
  clearButton.className = 'chatbot-clear-btn';
  clearButton.innerHTML = '<i class="fa fa-trash"></i>';
  clearButton.title = 'Xóa lịch sử trò chuyện';

  clearButton.addEventListener('click', (e) => {
    e.stopPropagation(); // Prevent chatbot from closing

    if (confirm('Bạn có chắc chắn muốn xóa lịch sử trò chuyện?')) {
      chatbotBody.innerHTML = ''; // Clear all messages
      localStorage.removeItem('jbook_chat_history');
      showInitialGreeting();
      addSuggestionButtons();
    }
  });

  headerDiv.appendChild(clearButton);
}

// Initialize clear button once DOM is fully loaded
document.addEventListener('DOMContentLoaded', addClearChatButton);