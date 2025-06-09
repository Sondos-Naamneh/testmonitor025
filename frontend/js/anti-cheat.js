class AntiCheat {
    constructor() {
        this.isQuizActive = false;
        this.cheatAttempts = 0;
        this.maxCheatAttempts = 3;
        this.quizName = '';
        this.username = localStorage.getItem('username') || 'unknown_user';
        this.isSubmitting = false;
        this.setupEventListeners();
    }

    setupEventListeners() {
        document.addEventListener('keydown', this.handleKeyDown.bind(this));
        document.addEventListener('contextmenu', (e) => this.preventAction(e, 'Right-click context menu is disabled.'));
        document.addEventListener('visibilitychange', this.handleVisibilityChange.bind(this));
        document.addEventListener('copy', (e) => this.preventAction(e, 'Copying content is disabled.'));
        document.addEventListener('paste', (e) => this.preventAction(e, 'Pasting content is disabled.'));
        document.addEventListener('cut', (e) => this.preventAction(e, 'Cutting content is disabled.'));
        document.addEventListener('mousedown', this.logMouseClick.bind(this)); // Mouse left/right
        document.addEventListener('keypress', this.logKeyPress.bind(this));   // Regular key input
    }

    startQuiz(quizName) {
        this.isQuizActive = true;
        this.cheatAttempts = 0;
        this.quizName = quizName;
        this.isSubmitting = false;
        console.log(`Anti-cheat started for quiz: ${quizName}`);
    }

    endQuiz() {
        this.isQuizActive = false;
        this.isSubmitting = true;
        console.log('Anti-cheat stopped.');
        this.disableFullscreen();
    }

    preventAction(event, reason) {
        if (!this.isQuizActive) return;
        event.preventDefault();
        this.handleCheatAttempt(reason);
    }

    handleKeyDown(event) {
        if (!this.isQuizActive) return;

        const combination = [];
        if (event.ctrlKey) combination.push('Ctrl');
        if (event.altKey) combination.push('Alt');
        if (event.metaKey) combination.push('Meta');
        if (event.shiftKey) combination.push('Shift');
        combination.push(event.key);

        const comboString = combination.join('+');
        console.log(`KeyDown: ${comboString}`);

        const forbiddenCombos = ['Ctrl+c', 'Ctrl+v', 'Ctrl+x', 'Ctrl+p', 'Ctrl+Tab', 'Ctrl+F5', 'Meta+v', 'Alt+Tab'];

        if (forbiddenCombos.includes(comboString)) {
            event.preventDefault();
            this.handleCheatAttempt(`Use of forbidden shortcut detected: ${comboString}`);
        }
    }

    handleVisibilityChange() {
        if (!this.isQuizActive || this.isSubmitting) return;

        if (document.hidden) {
            this.handleCheatAttempt('User switched tabs or minimized the window.');
        }
    }

    async handleCheatAttempt(reason) {
        if (!this.isQuizActive || this.isSubmitting) return;

        this.cheatAttempts++;

        console.warn(`Cheat attempt #${this.cheatAttempts}: ${reason}`);

        const incidentData = {
            username: this.username,
            quiz_name: this.quizName,
            incident_type: reason,
            timestamp: new Date().toISOString(),
            details: `Attempt ${this.cheatAttempts} of ${this.maxCheatAttempts}.`
        };

        try {
            await fetch('http://127.0.0.1:5000/reportCheating', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(incidentData)
            });
        } catch (error) {
            console.error('Failed to report cheating incident:', error);
        }

        if (this.cheatAttempts >= this.maxCheatAttempts) {
            this.endQuiz();
            alert('Quiz terminated due to multiple cheating attempts. Your session has been logged.');
            window.location.href = 'courses.html';
        } else {
            alert(`Warning: Cheating attempt detected. \nReason: ${reason}\nThis is attempt ${this.cheatAttempts} of ${this.maxCheatAttempts}. Further attempts will terminate the quiz.`);
        }
    }

    async enableFullscreen() {
        try {
            if (document.documentElement.requestFullscreen) {
                await document.documentElement.requestFullscreen({ navigationUI: 'hide' });
            } else if (document.documentElement.webkitRequestFullscreen) {
                await document.documentElement.webkitRequestFullscreen();
            }
        } catch (error) {
            console.warn('Fullscreen request failed.', error);
            alert('Please enable fullscreen mode to start the quiz.');
        }
    }

    disableFullscreen() {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
        }
    }

    logMouseClick(event) {
        if (!this.isQuizActive) return;

        let button = 'Unknown';
        switch (event.button) {
            case 0:
                button = 'Left Click';
                break;
            case 1:
                button = 'Middle Click';
                break;
            case 2:
                button = 'Right Click';
                break;
        }

        console.log(`Mouse ${button} at [X: ${event.clientX}, Y: ${event.clientY}] on element: ${event.target.tagName}`);
    }

    logKeyPress(event) {
        if (!this.isQuizActive) return;
        console.log(`Key pressed: '${event.key}'`);
    }
}

const antiCheat = new AntiCheat();
export default antiCheat;
