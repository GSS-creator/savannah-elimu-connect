const socket = io();
const messagesDiv = document.getElementById('messages');
const messageInput = document.getElementById('message');

// Handle receiving messages
socket.on('receive_message', (data) => {
    addMessageToChat(data);
});

function sendMessage() {
    const message = messageInput.value.trim();
    
    if (message) {
        const messageData = {
            message: message,
            timestamp: new Date().toLocaleTimeString()
        };
        
        socket.emit('send_message', messageData);
        messageInput.value = '';
    }
}

function addMessageToChat(data) {
    const messageElement = document.createElement('div');
    messageElement.className = 'message';
    
    messageElement.innerHTML = `
        <div class="user">${data.user}</div>
        <div class="content">${data.message}</div>
        <div class="time">${data.timestamp}</div>
    `;
    
    messagesDiv.appendChild(messageElement);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Send message when Enter key is pressed
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Handle post interactions
document.addEventListener('DOMContentLoaded', () => {
    // Like button functionality
    const likeButtons = document.querySelectorAll('.like-button');
    likeButtons.forEach(button => {
        button.addEventListener('click', () => {
            const postCard = button.closest('.post-card');
            const postId = postCard.dataset.postId;
            // TODO: Implement like functionality with backend
            button.classList.toggle('liked');
        });
    });

    // Comment button functionality
    const commentButtons = document.querySelectorAll('.comment-button');
    commentButtons.forEach(button => {
        button.addEventListener('click', () => {
            const postCard = button.closest('.post-card');
            const postId = postCard.dataset.postId;
            // TODO: Implement comment functionality with backend
            toggleCommentSection(postCard);
        });
    });
});

function toggleCommentSection(postCard) {
    let commentSection = postCard.querySelector('.comment-section');
    
    if (!commentSection) {
        commentSection = document.createElement('div');
        commentSection.className = 'comment-section';
        commentSection.innerHTML = `
            <div class="comment-input">
                <input type="text" placeholder="Write a comment..." class="form-control">
                <button class="btn-primary">Post</button>
            </div>
            <div class="comments-list"></div>
        `;
        postCard.appendChild(commentSection);
    } else {
        commentSection.style.display = commentSection.style.display === 'none' ? 'block' : 'none';
    }
}
