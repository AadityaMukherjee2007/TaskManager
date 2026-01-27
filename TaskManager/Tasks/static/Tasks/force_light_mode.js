// This file disables system dark mode preference for the app by always forcing light theme.
(function() {
  // Remove any existing data-theme attribute
  document.documentElement.removeAttribute('data-theme');
  // Always set data-theme to light
  document.documentElement.setAttribute('data-theme', 'light');
  // Remove any class that might enable dark mode
  document.documentElement.classList.remove('dark');
  // Remove prefers-color-scheme: dark media queries by overriding them
  var style = document.createElement('style');
  style.innerHTML = `
    @media (prefers-color-scheme: dark) {
      html, body {
        color-scheme: light !important;
        background: #f9fafb !important;
        color: #111827 !important;
      }
      * {
        background: inherit !important;
        color: inherit !important;
      }
    }
  `;
  document.head.appendChild(style);
})();
