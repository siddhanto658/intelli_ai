$(document).ready(function () {

    $('.text').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "bounceIn",
        },
        out: {
            effect: "bounceOut",
        },

    });

    // Siri configuration
    var siriWave = new SiriWave({
        container: document.getElementById("siri-container"),
        width: 800,
        height: 200,
        style: "ios9",
        amplitude: "1",
        speed: "0.30",
        autostart: true
      });

    // Siri message animation
    $('.siri-message').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "fadeInUp",
            sync: true,
        },
        out: {
            effect: "fadeOutUp",
            sync: true,
        },

    });

    // Load microphones
    async function loadMicrophones() {
        try {
            var mics = await eel.get_available_mics()();
            var select = document.getElementById("micSelect");
            select.innerHTML = "";
            if (mics && mics.length > 0) {
                mics.forEach(function(mic) {
                    var option = document.createElement("option");
                    option.value = mic.index;
                    option.text = mic.name;
                    select.appendChild(option);
                });
            } else {
                var option = document.createElement("option");
                option.value = "0";
                option.text = "No microphones found";
                select.appendChild(option);
            }
        } catch (e) {
            console.error("Error loading microphones:", e);
        }
    }

    // Load saved settings
    async function loadSavedSettings() {
        try {
            var settings = await eel.get_settings()();
            if (settings) {
                document.getElementById("micSelect").value = settings.mic_index || 0;
                document.getElementById("speechRate").value = settings.speech_rate || 174;
                document.getElementById("speechRateValue").text = settings.speech_rate || 174;
            }
        } catch (e) {
            console.error("Error loading settings:", e);
        }
    }

    // Initialize microphones on load
    setTimeout(loadMicrophones, 1000);

    // Refresh microphones button
    $("#refreshMicsBtn").click(function() {
        loadMicrophones();
    });

    // Test microphone button
    $("#testMicBtn").click(function() {
        var micIndex = parseInt(document.getElementById("micSelect").value);
        
        // Show testing indicator
        $("#testMicBtn").html('<span class="spinner-border spinner-border-sm" role="status"></span> Testing...');
        
        // Try to listen for 3 seconds
        eel.test_microphone(micIndex)(function(result) {
            if (result === "success") {
                alert("Microphone is working! Say something.");
            } else {
                alert("Could not detect microphone. Please try another.");
            }
            $("#testMicBtn").html('<i class="bi bi-mic"></i> Test Mic');
        });
    });

    // Update speech rate value display
    $("#speechRate").on("input", function() {
        $("#speechRateValue").text($(this).val());
    });

    // Settings button click
    $("#SettingsBtn").click(function() {
        var myModal = new bootstrap.Modal(document.getElementById("settingsModal"));
        myModal.show();
    });

    // When modal is shown, load microphones
    $('#settingsModal').on('shown.bs.modal', function () {
        loadMicrophones();
        loadSavedSettings();
    });

    // Save settings
    $("#saveSettingsBtn").click(async function() {
        var micIndex = parseInt(document.getElementById("micSelect").value);
        var speechRate = parseInt(document.getElementById("speechRate").value);
        
        try {
            await eel.set_mic_index(micIndex)();
            await eel.set_speech_rate(speechRate)();
        } catch (e) {
            console.error("Error saving settings:", e);
        }
        
        var myModal = bootstrap.Modal.getInstance(document.getElementById("settingsModal"));
        myModal.hide();
        
        alert("Settings saved! Microphone: " + micIndex + ", Speech Rate: " + speechRate);
    });

    // Back button to return to text input
    $("#BackBtn").click(function() {
        $("#Oval").attr("hidden", false);
        $("#SiriWave").attr("hidden", true);
    });

    // Escape key to go back
    document.addEventListener("keydown", function(e) {
        if (e.key === "Escape") {
            $("#Oval").attr("hidden", false);
            $("#SiriWave").attr("hidden", true);
        }
    });

    // mic button click event
    $("#MicBtn").click(function () { 
        eel.playAssistantSound()
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);
        eel.allCommands()()
    });

    // keyboard shortcut Ctrl+J
    function doc_keyUp(e) {
        if (e.key === 'j' && e.metaKey) {
            eel.playAssistantSound()
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            eel.allCommands()()
        }
    }
    document.addEventListener('keyup', doc_keyUp, false);

    // to play assistant 
    function PlayAssistant(message) {
        if (message && message.trim() !== "") {
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            eel.allCommands(message);
            $("#chatbox").val("")
            $("#MicBtn").attr('hidden', false);
            $("#SendBtn").attr('hidden', true);
        }
    }

    // toggle function to hide and display mic and send button 
    function ShowHideButton(message) {
        if (message.length == 0) {
            $("#MicBtn").attr('hidden', false);
            $("#SendBtn").attr('hidden', true);
        }
        else {
            $("#MicBtn").attr('hidden', true);
            $("#SendBtn").attr('hidden', false);
        }
    }

    // key up event handler on text box
    $("#chatbox").keyup(function () {
        let message = $("#chatbox").val();
        ShowHideButton(message)
    });
    
    // send button event handler
    $("#SendBtn").click(function () {
        let message = $("#chatbox").val()
        PlayAssistant(message)
    });

    // enter press event handler on chat box
    $("#chatbox").keypress(function (e) {
        key = e.which;
        if (key == 13) {
            e.preventDefault();
            let message = $("#chatbox").val()
            PlayAssistant(message)
        }
    });

});
