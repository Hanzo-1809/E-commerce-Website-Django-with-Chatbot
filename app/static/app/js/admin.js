document.addEventListener('DOMContentLoaded', function () {
    // Toggle sidebar
    document.getElementById('sidebarCollapse').addEventListener('click', function () {
        document.getElementById('sidebar').classList.toggle('active');
    });

    // Tooltips initialization
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Datatable initialization if exists
    if ($.fn.DataTable !== undefined) {
        $('.datatable').DataTable({
            "pageLength": 10,
            "ordering": true,
            "responsive": true
        });
    }
});