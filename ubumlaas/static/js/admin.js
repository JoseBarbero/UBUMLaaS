import Chart from "chart.js";
import flatpickr from "flatpickr";
import feather from "feather-icons";
import "jsvectormap"
import "jsvectormap/dist/maps/world.js"

Chart.defaults.global.defaultFontColor = window.theme["gray-600"];
Chart.defaults.global.defaultFontFamily = "'Inter', 'Helvetica Neue', 'Helvetica', 'Arial', sans-serif";
window.Chart = Chart;

document.addEventListener("DOMContentLoaded", () => {
    feather.replace();
});

window.feather = feather;

window.flatpickr = flatpickr;

const theme = {
    "primary": "#3B7DDD",
    "secondary": "#6c757d",
    "success": "#1cbb8c",
    "info": "#17a2b8",
    "warning": "#fcb92c",
    "danger": "#dc3545",
    "white": "#fff",
    "gray-100": "#f8f9fa",
    "gray-200": "#e9ecef",
    "gray-300": "#dee2e6",
    "gray-400": "#ced4da",
    "gray-500": "#adb5bd",
    "gray-600": "#6c757d",
    "gray-700": "#495057",
    "gray-800": "#343a40",
    "gray-900": "#212529",
    "black": "#000"
};

// Add theme to the window object
window.theme = theme;