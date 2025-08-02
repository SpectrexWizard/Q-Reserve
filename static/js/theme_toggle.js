/**
 * Theme toggle functionality for Q-Reserve
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get theme from localStorage or default to 'light'
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    // Apply theme to document
    document.documentElement.classList.toggle('dark', currentTheme === 'dark');
    
    // Theme toggle functionality
    const themeToggle = document.querySelector('[data-theme-toggle]');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const isDark = document.documentElement.classList.contains('dark');
            const newTheme = isDark ? 'light' : 'dark';
            
            // Update localStorage
            localStorage.setItem('theme', newTheme);
            
            // Update document class
            document.documentElement.classList.toggle('dark', newTheme === 'dark');
            
            // Update toggle button icon
            updateThemeIcon(newTheme);
        });
    }
    
    // Initialize theme icon
    updateThemeIcon(currentTheme);
});

function updateThemeIcon(theme) {
    const sunIcon = document.querySelector('[data-sun-icon]');
    const moonIcon = document.querySelector('[data-moon-icon]');
    
    if (sunIcon && moonIcon) {
        if (theme === 'dark') {
            sunIcon.style.display = 'block';
            moonIcon.style.display = 'none';
        } else {
            sunIcon.style.display = 'none';
            moonIcon.style.display = 'block';
        }
    }
}

// Export for use in other modules
window.QReserveTheme = {
    toggle: function() {
        const isDark = document.documentElement.classList.contains('dark');
        const newTheme = isDark ? 'light' : 'dark';
        localStorage.setItem('theme', newTheme);
        document.documentElement.classList.toggle('dark', newTheme === 'dark');
        updateThemeIcon(newTheme);
    },
    
    getCurrent: function() {
        return localStorage.getItem('theme') || 'light';
    },
    
    set: function(theme) {
        localStorage.setItem('theme', theme);
        document.documentElement.classList.toggle('dark', theme === 'dark');
        updateThemeIcon(theme);
    }
};