$(document).ready(function () {

    // Display Speak Message
    eel.expose(DisplayMessage)
    function DisplayMessage(message) {
        $(".siri-message li:first").text(message);
        $('.siri-message').textillate('start');
    }

    // Display hood
    eel.expose(ShowHood)
    function ShowHood() {
        $("#Oval").attr("hidden", false);
        $("#SiriWave").attr("hidden", true);
    }

    eel.expose(senderText)
    function senderText(message) {
        var chatBox = document.getElementById("chat-canvas-body");
        $(".welcome-message").remove();
        
        if (message.trim() !== "") {
            chatBox.innerHTML += `<div class="chat-message user-message">
                <div class="message-content">
                    <span class="message-text">${escapeHtml(message)}</span>
                </div>
            </div>`; 
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }

    eel.expose(receiverText)
    function receiverText(message) {
        var chatBox = document.getElementById("chat-canvas-body");
        $(".welcome-message").remove();
        
        if (message.trim() !== "") {
            chatBox.innerHTML += `<div class="chat-message bot-message">
                <div class="message-content">
                    <span class="message-text">${escapeHtml(message)}</span>
                </div>
            </div>`; 
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }

    // Clear chat button
    $("#clearChatBtn").click(function() {
        $("#chat-canvas-body").html(`<div class="welcome-message text-center text-muted mt-5">
            <i class="bi bi-chat-dots fs-1"></i>
            <p class="mt-2">Start a conversation with INTELLI</p>
        </div>`);
    });

    function escapeHtml(text) {
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Show system capabilities in browser console
    eel.getSystemCapabilities()().then((capabilities) => {
        console.log("INTELLI capabilities:", capabilities);
    }).catch(() => {
        console.log("Could not fetch system capabilities.");
    });
});
