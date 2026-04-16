$(document).ready(function () {

    // Load settings
    function loadSettings() {
        const settings = {
            voiceSpeed: localStorage.getItem('intelli_voiceSpeed'),
            voiceName: localStorage.getItem('intelli_voiceName'),
            startupSound: localStorage.getItem('intelli_startupSound'),
            permissionPrompts: localStorage.getItem('intelli_permissionPrompts'),
            aiModel: localStorage.getItem('intelli_aiModel'),
            groqModel: localStorage.getItem('intelli_groqModel')
        };

        if (settings.voiceSpeed) $('#voiceSpeed').val(settings.voiceSpeed);
        if (settings.voiceName) $('#voiceName').val(settings.voiceName);
        if (settings.startupSound !== null) {
            $('#startupSound').prop('checked', settings.startupSound === 'true');
        }
        if (settings.permissionPrompts !== null) {
            $('#permissionPrompts').prop('checked', settings.permissionPrompts === 'true');
        }
        if (settings.aiModel) $('#aiModel').val(settings.aiModel);
        if (settings.groqModel) $('#groqModel').val(settings.groqModel);

        checkApiKeysStatus();
    }
    loadSettings();

    // Save settings
    $('#saveSettingsBtn').click(function () {
        const settings = {
            voiceSpeed: $('#voiceSpeed').val(),
            voiceName: $('#voiceName').val(),
            startupSound: $('#startupSound').is(':checked'),
            permissionPrompts: $('#permissionPrompts').is(':checked'),
            aiModel: $('#aiModel').val(),
            groqModel: $('#groqModel').val()
        };

        localStorage.setItem('intelli_voiceSpeed', settings.voiceSpeed);
        localStorage.setItem('intelli_voiceName', settings.voiceName);
        localStorage.setItem('intelli_startupSound', String(settings.startupSound));
        localStorage.setItem('intelli_permissionPrompts', String(settings.permissionPrompts));
        localStorage.setItem('intelli_aiModel', settings.aiModel);
        localStorage.setItem('intelli_groqModel', settings.groqModel);

        eel.updateVoiceSettings(settings.voiceName, settings.voiceSpeed);
        eel.updateAiSettings(settings.aiModel, settings.groqModel);

        const btn = $(this);
        btn.text('Saved!').addClass('saved');
        setTimeout(() => {
            btn.text('Save Settings').removeClass('saved');
        }, 1500);
    });

    // Theme toggle
    $('#themeToggle').click(function () {
        const currentTheme = $('body').hasClass('light-theme') ? 'dark' : 'light';
        applyTheme(currentTheme);
    });

    function applyTheme(theme) {
        if (theme === 'light') {
            $('body').addClass('light-theme');
        } else {
            $('body').removeClass('light-theme');
        }
        localStorage.setItem('intelli_theme', theme);
    }

    // Check API keys status
    async function checkApiKeysStatus() {
        try {
            const status = await eel.checkApiKeysStatus()();
            updateKeyStatus('geminiStatus', status.gemini);
            updateKeyStatus('groqStatus', status.groq);
        } catch (e) {
            console.log('Could not fetch API key status');
        }
    }

    function updateKeyStatus(elementId, isSet) {
        const el = $('#' + elementId);
        if (el.length) {
            if (isSet) {
                el.removeClass('inactive').addClass('active');
            } else {
                el.removeClass('active').addClass('inactive');
            }
        }
    }

    // Mic button - main mic button
    $('#MicBtn').click(function () {
        console.log('Mic clicked');
        const startupSnd = localStorage.getItem('intelli_startupSound');
        if (startupSnd === null || startupSnd === 'true') {
            eel.playAssistantSound();
        }
        eel.allCommands();
    });

    // Mic button in Siri mode
    $('#MicBtnSiri').click(function () {
        console.log('Siri Mic clicked');
        const startupSnd = localStorage.getItem('intelli_startupSound');
        if (startupSnd === null || startupSnd === 'true') {
            eel.playAssistantSound();
        }
        eel.allCommands();
    });

    // Record button for wake word
    $('#RecordBtn').click(function () {
        console.log('Record clicked');
        const startupSnd = localStorage.getItem('intelli_startupSound');
        if (startupSnd === null || startupSnd === 'true') {
            eel.playAssistantSound();
        }
        eel.allCommands();
    });

    // Stop button
    $('#stopBtn').click(function () {
        console.log('Stop clicked');
        eel.stopCurrentAction();
    });

    // End button
    $('#endBtn').click(function () {
        if (confirm('End session?')) {
            console.log('End clicked');
            eel.endSession();
        }
    });

    // Send message from main input
    $('#SendBtn').click(function () {
        const message = $('#chatbox').val();
        if (message.trim() !== '') {
            const startupSnd = localStorage.getItem('intelli_startupSound');
            if (startupSnd === null || startupSnd === 'true') {
                eel.playAssistantSound();
            }
            eel.allCommands(message);
            $('#chatbox').val('');
        }
    });

    // Send message from Siri input
    $('#SendBtnSiri').click(function () {
        const message = $('#chatbox-siri').val();
        if (message.trim() !== '') {
            const startupSnd = localStorage.getItem('intelli_startupSound');
            if (startupSnd === null || startupSnd === 'true') {
                eel.playAssistantSound();
            }
            eel.allCommands(message);
            $('#chatbox-siri').val('');
        }
    });

    // Enter key for main input
    $('#chatbox').keypress(function (e) {
        if (e.which === 13) {
            const message = $(this).val();
            if (message.trim() !== '') {
                const startupSnd = localStorage.getItem('intelli_startupSound');
                if (startupSnd === null || startupSnd === 'true') {
                    eel.playAssistantSound();
                }
                eel.allCommands(message);
                $(this).val('');
            }
        }
    });

    // Enter key for Siri input
    $('#chatbox-siri').keypress(function (e) {
        if (e.which === 13) {
            const message = $(this).val();
            if (message.trim() !== '') {
                const startupSnd = localStorage.getItem('intelli_startupSound');
                if (startupSnd === null || startupSnd === 'true') {
                    eel.playAssistantSound();
                }
                eel.allCommands(message);
                $(this).val('');
            }
        }
    });

    // ========== KEYBOARD SHORTCUTS ==========
    
    $(document).keydown(function (e) {
        // Ignore if typing in input
        if ($(e.target).is('input, textarea')) {
            if (e.key === 'Escape') {
                e.target.blur();
                return;
            }
            return;
        }

        // Ctrl/Cmd + J - Voice input
        if ((e.ctrlKey || e.metaKey) && e.key === 'j') {
            e.preventDefault();
            $('#MicBtn').click();
            return;
        }

        // Escape - Stop/Cancel
        if (e.key === 'Escape') {
            e.preventDefault();
            eel.stopCurrentAction();
            return;
        }

        // Ctrl/Cmd + L - Clear chat
        if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
            e.preventDefault();
            eel.clearChat();
            return;
        }

        // Ctrl/Cmd + , - Open settings
        if ((e.ctrlKey || e.metaKey) && e.key === ',') {
            e.preventDefault();
            new bootstrap.Offcanvas($('#settingsPanel')[0]).show();
            return;
        }

        // T - Toggle theme
        if (e.key === 't' || e.key === 'T') {
            const newTheme = $('body').hasClass('light-theme') ? 'dark' : 'light';
            applyTheme(newTheme);
            return;
        }
    });
});
