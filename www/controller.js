$(document).ready(function () {

    let currentTypewriter = null;
    let streamingActive = false;
    let streamBuffer = "";

    // Theme management
    let currentTheme = localStorage.getItem('intelli_theme') || 'dark';

    function applyTheme(theme) {
        if (theme === 'light') {
            document.body.classList.add('light-theme');
            $('#themeToggle i').removeClass('bi-moon-fill').addClass('bi-sun-fill');
        } else {
            document.body.classList.remove('light-theme');
            $('#themeToggle i').removeClass('bi-sun-fill').addClass('bi-moon-fill');
        }
        currentTheme = theme;
        localStorage.setItem('intelli_theme', theme);
    }

    // Apply saved theme
    applyTheme(currentTheme);

    // AI State management
    const AI_STATES = {
        IDLE: 'idle',
        LISTENING: 'listening',
        PROCESSING: 'processing',
        SPEAKING: 'speaking',
        STREAMING: 'streaming'
    };

    const STATE_LABELS = {
        idle: 'Ready',
        listening: 'Listening...',
        processing: 'Thinking...',
        speaking: 'Speaking...',
        streaming: 'Responding...'
    };

    function setAIState(state) {
        const stateEl = $('#aiState');
        stateEl.removeClass('idle listening processing speaking streaming').addClass(state);
        stateEl.find('.state-text').text(STATE_LABELS[state] || 'Ready');
    }

    // Toast notification system
    eel.expose(showToast);
    function showToast(type, message, duration = 4000) {
        const container = $('#toastContainer');
        const toast = $(`
            <div class="toast ${type}">
                <i class="bi toast-icon ${getToastIcon(type)}"></i>
                <span class="toast-message">${message}</span>
                <button class="toast-close"><i class="bi bi-x"></i></button>
            </div>
        `);
        
        container.append(toast);
        
        toast.find('.toast-close').click(() => removeToast(toast));
        
        if (duration > 0) {
            setTimeout(() => removeToast(toast), duration);
        }
    }

    function getToastIcon(type) {
        const icons = {
            error: 'bi-x-circle-fill',
            success: 'bi-check-circle-fill',
            warning: 'bi-exclamation-circle-fill',
            info: 'bi-info-circle-fill'
        };
        return icons[type] || icons.info;
    }

    function removeToast(toast) {
        toast.addClass('toast-out');
        setTimeout(() => toast.remove(), 200);
    }

    // System notifications
    eel.expose(showSystemNotification);
    function showSystemNotification(title, body) {
        if ('Notification' in window) {
            if (Notification.permission === 'granted') {
                new Notification(title, { body, icon: 'assets/img/iNTELLI AI.png' });
            } else if (Notification.permission !== 'denied') {
                Notification.requestPermission().then(permission => {
                    if (permission === 'granted') {
                        new Notification(title, { body, icon: 'assets/img/iNTELLI AI.png' });
                    }
                });
            }
        }
    }

    // Streaming response
    eel.expose(startStream);
    function startStream() {
        streamingActive = true;
        streamBuffer = "";
        showResponseCard("");
        setAIState('streaming');
    }

    eel.expose(streamToken);
    function streamToken(token) {
        if (!streamingActive) return;
        streamBuffer += token;
        updateResponseText(streamBuffer);
    }

    eel.expose(endStream);
    function endStream(finalText) {
        streamingActive = false;
        if (finalText) {
            streamBuffer = finalText;
            updateResponseText(finalText);
        }
        setAIState('speaking');
    }

    function showResponseCard(text) {
        const card = $('#responseCard');
        const textEl = $('#responseText');
        
        card.removeClass('hidden');
        textEl.text('');
        
        addToChat('assistant', '');
    }

    function updateResponseText(text) {
        const textEl = $('#responseText');
        textEl.text(text);
        
        const lastAssistant = $('#chatMessages .chat-message.assistant').last();
        if (lastAssistant.length) {
            lastAssistant.find('.message-bubble').text(text);
        }
    }

    function stopTypewriter() {
        if (currentTypewriter) {
            clearTimeout(currentTypewriter);
            currentTypewriter = null;
        }
        streamingActive = false;
    }

    eel.expose(DisplayMessage);
    function DisplayMessage(message) {
        showResponseCard();
        typewriterEffect(message, $('#responseText'));
    }

    eel.expose(stopTypewriterDisplay);
    function stopTypewriterDisplay() {
        stopTypewriter();
        $('#responseCard').addClass('hidden');
    }

    function typewriterEffect(text, element, index = 0) {
        if (currentTypewriter) {
            clearTimeout(currentTypewriter);
        }

        function type() {
            if (index < text.length) {
                element.text(text.substring(0, index + 1));
                index++;
                currentTypewriter = setTimeout(type, 20);
            } else {
                currentTypewriter = null;
            }
        }

        type();
    }

    eel.expose(ShowHood);
    function ShowHood() {
        stopTypewriter();
        setAIState('idle');
        showIdleVisual();
    }

    eel.expose(senderText);
    function senderText(message) {
        addToChat('user', message);
        showProcessingVisual();
        setAIState('processing');
    }

    eel.expose(receiverText);
    function receiverText(message) {
        showSpeakingVisual();
        setAIState('speaking');
    }

    function showIdleVisual() {
        hideAllVisuals();
        $('#idleVisual').removeClass('hidden');
    }

    function showListeningVisual() {
        hideAllVisuals();
        $('#listeningDisplay').removeClass('hidden');
        setAIState('listening');
    }

    function showProcessingVisual() {
        hideAllVisuals();
        $('#processingVisual').removeClass('hidden');
    }

    function showSpeakingVisual() {
        hideAllVisuals();
        $('#speakingVisual').removeClass('hidden');
    }

    function hideAllVisuals() {
        $('#idleVisual, #listeningVisual, #listeningDisplay, #processingVisual, #speakingVisual').addClass('hidden');
    }

    eel.expose(updateListeningText);
    function updateListeningText(text) {
        if (text) {
            $('#listeningText').text(text);
        }
    }

    eel.expose(updateTranscript);
    function updateTranscript(text) {
        $('#transcriptPreview').text(text);
    }

    function addToChat(type, message) {
        const chatMessages = $('#chatMessages');
        chatMessages.find('.chat-empty').remove();
        
        const lastMsg = chatMessages.find('.chat-message:last-child');
        if (lastMsg.hasClass(type)) {
            lastMsg.find('.message-bubble').text(message);
        } else {
            const msg = $(`
                <div class="chat-message ${type}">
                    <div class="message-bubble">${escapeHtml(message)}</div>
                </div>
            `);
            chatMessages.append(msg);
        }
        chatMessages.scrollTop(chatMessages[0].scrollHeight);
    }

    eel.expose(clearChat);
    function clearChat() {
        $('#chatMessages').html(`
            <div class="chat-empty">
                <i class="bi bi-chat"></i>
                <p>Start a conversation</p>
            </div>
        `);
    }

    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Initialize
    showIdleVisual();
    setAIState('idle');

    eel.getSystemCapabilities().then((capabilities) => {
        console.log('INTELLI capabilities:', capabilities);
    }).catch(() => {
        console.log('Could not fetch system capabilities.');
    });
});
