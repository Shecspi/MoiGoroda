var tooltipTriggerList = [].slice.call(
    document.querySelectorAll(
        '[data-bs-toggle="tooltip"], [data-bs-tooltip="tooltip"]'
    )
);
var tooltipList = tooltipTriggerList.map(
    function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    }
);
