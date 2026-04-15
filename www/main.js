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

    // ---- Load settings from localStorage ----
    function loadSettings() {
        var speed = localStorage.getItem('intelli_voiceSpeed');
        var voice = localStorage.getItem('intelli_voiceName');
        var startupSnd = localStorage.getItem('intelli_startupSound');
        var perms = localStorage.getItem('intelli_permissionPrompts');

        if (speed) $('#voiceSpeed').val(speed);
        if (voice) $('#voiceName').val(voice);
        if (startupSnd !== null) $('#startupSound').prop('checked', startupSnd === 'true');
        if (perms !== null) $('#permissionPrompts').prop('checked', perms === 'true');
    }
    loadSettings();

    // ---- Save settings ----
    $("#saveSettingsBtn").click(function () {
        var speed = $('#voiceSpeed').val();
        var voice = $('#voiceName').val();
        var startupSnd = $('#startupSound').is(':checked');
        var perms = $('#permissionPrompts').is(':checked');

        localStorage.setItem('intelli_voiceSpeed', speed);
        localStorage.setItem('intelli_voiceName', voice);
        localStorage.setItem('intelli_startupSound', String(startupSnd));
        localStorage.setItem('intelli_permissionPrompts', String(perms));

        // Send voice settings to Python backend
        eel.updateVoiceSettings(voice, speed);

        // Visual save feedback
        var btn = $(this);
        btn.text('Saved!').removeClass('btn-outline-info').addClass('btn-success');
        setTimeout(function() {
            btn.text('Save Settings').removeClass('btn-success').addClass('btn-outline-info');
        }, 1500);
    });


    // ---- Main screen mic button ----
    $("#MicBtn").click(function () { 
        var startupSnd = localStorage.getItem('intelli_startupSound');
        if (startupSnd === null || startupSnd === 'true') {
            eel.playAssistantSound()
        }
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);
        eel.allCommands()
    });


    function doc_keyUp(e) {
        if (e.key === 'j' && e.metaKey) {
            var startupSnd = localStorage.getItem('intelli_startupSound');
            if (startupSnd === null || startupSnd === 'true') {
                eel.playAssistantSound()
            }
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            eel.allCommands()
        }
    }
    document.addEventListener('keyup', doc_keyUp, false);

    // Record button click event
    $("#RecordBtn").click(async function () {
        let status = await eel.toggleScreenRecording()();
        if (status === "recording") {
            $("#RecordBtn i").removeClass("bi-record-circle text-danger").addClass("bi-stop-circle text-warning");
            eel.playAssistantSound();
        } else if (status === "stopped") {
            $("#RecordBtn i").removeClass("bi-stop-circle text-warning").addClass("bi-record-circle text-danger");
            eel.playAssistantSound();
        }
    });

    // ---- Play assistant helper for typed messages ----
    function PlayAssistant(message) {
        if (message != "") {
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            eel.allCommands(message);
            $("#chatbox").val("")
            $("#chatbox-siri").val("")
            $("#MicBtn").attr('hidden', false);
            $("#SendBtn").attr('hidden', true);
        }
    }

    // ---- Main screen text input toggle (mic/send) ----
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

    $("#chatbox").keyup(function () {
        let message = $("#chatbox").val();
        ShowHideButton(message)
    });
    
    $("#SendBtn").click(function () {
        let message = $("#chatbox").val()
        PlayAssistant(message)
    });

    $("#chatbox").keypress(function (e) {
        key = e.which;
        if (key == 13) {
            let message = $("#chatbox").val()
            PlayAssistant(message)
        }
    });

    // ---- SiriWave screen text input (type during voice mode) ----
    function ShowHideButtonSiri(message) {
        if (message.length == 0) {
            $("#MicBtnSiri").attr('hidden', false);
            $("#SendBtnSiri").attr('hidden', true);
        }
        else {
            $("#MicBtnSiri").attr('hidden', true);
            $("#SendBtnSiri").attr('hidden', false);
        }
    }

    $("#chatbox-siri").keyup(function () {
        let message = $("#chatbox-siri").val();
        ShowHideButtonSiri(message)
    });

    $("#SendBtnSiri").click(function () {
        let message = $("#chatbox-siri").val()
        PlayAssistant(message)
    });

    $("#chatbox-siri").keypress(function (e) {
        if (e.which == 13) {
            let message = $("#chatbox-siri").val()
            PlayAssistant(message)
        }
    });

    // SiriWave mic button - same as main mic
    $("#MicBtnSiri").click(function () {
        eel.allCommands()
    });

    // Back button - return to home/oval screen
    $("#BackBtn").click(function () {
        $("#Oval").attr("hidden", false);
        $("#SiriWave").attr("hidden", true);
    });


});