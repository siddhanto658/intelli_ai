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
            $('#themeToggle i').removeClass('bi-moon-fill').addClass('bi-sun-fill');
        } else {
            $('body').removeClass('light-theme');
            $('#themeToggle i').removeClass('bi-sun-fill').addClass('bi-moon-fill');
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

    // Clear chat
    $('#clearChatBtn').click(function () {
        eel.clearChat();
        showToast('info', 'Chat cleared');
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

    // Mic button
    $('#micBtn').click(function () {
        const startupSnd = localStorage.getItem('intelli_startupSound');
        if (startupSnd === null || startupSnd === 'true') {
            eel.playAssistantSound();
        }
        eel.allCommands();
    });

    // Input field - toggle send/mic button
    function updateInputState(value) {
        if (value.length === 0) {
            $('#micBtn').removeClass('hidden');
            $('#sendBtn').addClass('hidden');
        } else {
            $('#micBtn').addClass('hidden');
            $('#sendBtn').removeClass('hidden');
        }
    }

    $('#chatInput').on('input', function () {
        updateInputState($(this).val());
    });

    // Send message
    function sendMessage(message) {
        if (message.trim() === '') return;
        
        const startupSnd = localStorage.getItem('intelli_startupSound');
        if (startupSnd === null || startupSnd === 'true') {
            eel.playAssistantSound();
        }
        
        eel.allCommands(message);
        $('#chatInput').val('');
        updateInputState('');
    }

    $('#sendBtn').click(function () {
        sendMessage($('#chatInput').val());
    });

    $('#chatInput').keypress(function (e) {
        if (e.which === 13) {
            sendMessage($(this).val());
        }
    });

    // ========== KEYBOARD SHORTCUTS ==========
    
    $(document).keydown(function (e) {
        // Ignore if typing in input
        if ($(e.target).is('input, textarea')) {
            // Allow Escape to blur
            if (e.key === 'Escape') {
                e.target.blur();
                return;
            }
            return;
        }

        // Ctrl/Cmd + J - Voice input
        if ((e.ctrlKey || e.metaKey) && e.key === 'j') {
            e.preventDefault();
            $('#micBtn').click();
            return;
        }

        // Ctrl/Cmd + Enter - Send text
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            if ($('#chatInput').val().trim()) {
                sendMessage($('#chatInput').val());
            }
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
            showToast('info', 'Chat cleared');
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

        // M - Toggle mute (stop listening)
        if (e.key === 'm' || e.key === 'M') {
            e.preventDefault();
            eel.stopCurrentAction();
            showToast('info', 'Stopped');
            return;
        }

        // ? - Show shortcuts help
        if (e.key === '?') {
            showShortcutsHelp();
            return;
        }
    });

    function showShortcutsHelp() {
        showToast('info', `
            <strong>Shortcuts:</strong><br>
            Ctrl+J - Voice input<br>
            Ctrl+Enter - Send message<br>
            Escape - Stop/Cancel<br>
            Ctrl+L - Clear chat<br>
            T - Toggle theme<br>
            M - Stop action<br>
            ? - This help
        `, 6000);
    }

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
});
