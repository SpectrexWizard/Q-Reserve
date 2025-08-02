/**
 * Theme Toggle Functionality for Q-Reserve
 * 
 * Handles light/dark mode switching and persistence
 */

class ThemeManager {
    constructor() {
        this.init();
    }

    init() {
        // Apply saved theme on page load
        this.applySavedTheme();
        
        // Listen for system theme changes
        this.watchSystemTheme();
        
        // Initialize theme toggle buttons
        this.initializeToggles();
    }

    applySavedTheme() {
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // Determine theme to apply
        let theme;
        if (savedTheme) {
            theme = savedTheme;
        } else {
            theme = systemPrefersDark ? 'dark' : 'light';
        }
        
        this.setTheme(theme);
    }

    setTheme(theme) {
        const html = document.documentElement;
        
        if (theme === 'dark') {
            html.classList.add('dark');
        } else {
            html.classList.remove('dark');
        }
        
        // Update meta theme-color for mobile browsers
        this.updateMetaThemeColor(theme);
        
        // Dispatch custom event for other components
        document.dispatchEvent(new CustomEvent('themeChanged', { 
            detail: { theme } 
        }));
    }

    updateMetaThemeColor(theme) {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        
        // Set appropriate theme color
        const color = theme === 'dark' ? '#1f2937' : '#ffffff';
        metaThemeColor.content = color;
    }

    toggleTheme() {
        const currentTheme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        this.setTheme(newTheme);
        localStorage.setItem('theme', newTheme);
        
        return newTheme;
    }

    watchSystemTheme() {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        
        mediaQuery.addEventListener('change', (e) => {
            // Only apply system theme if user hasn't manually set a preference
            if (!localStorage.getItem('theme')) {
                this.setTheme(e.matches ? 'dark' : 'light');
            }
        });
    }

    initializeToggles() {
        // Find all theme toggle buttons
        const toggleButtons = document.querySelectorAll('[data-theme-toggle]');
        
        toggleButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.toggleTheme();
            });
        });
    }

    getCurrentTheme() {
        return document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    }

    resetToSystemTheme() {
        localStorage.removeItem('theme');
        this.applySavedTheme();
    }
}

// Initialize theme manager
const themeManager = new ThemeManager();

// Export for use in other scripts
window.QReserve = window.QReserve || {};
window.QReserve.ThemeManager = themeManager;

// Utility functions for theme detection
window.QReserve.theme = {
    isDark: () => themeManager.getCurrentTheme() === 'dark',
    isLight: () => themeManager.getCurrentTheme() === 'light',
    toggle: () => themeManager.toggleTheme(),
    set: (theme) => {
        themeManager.setTheme(theme);
        localStorage.setItem('theme', theme);
    },
    reset: () => themeManager.resetToSystemTheme()
};

// Add smooth transition class after page load to prevent flash
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        document.body.classList.add('transition-colors', 'duration-200');
    }, 100);
});