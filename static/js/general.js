document.addEventListener('DOMContentLoaded', function() {
    const userTypeRadios = document.querySelectorAll('input[name="user-type"]');
    const driverOnlyFields = document.querySelectorAll('.driver-only');

    userTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'driver') {
                driverOnlyFields.forEach(field => field.style.display = 'block');
            } else {
                driverOnlyFields.forEach(field => field.style.display = 'none');
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const dateInput = document.getElementById('date');
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    const yyyy = tomorrow.getFullYear();
    const mm = String(tomorrow.getMonth() + 1).padStart(2, '0'); // Months are zero-based
    const dd = String(tomorrow.getDate()).padStart(2, '0');
    const minDate = `${yyyy}-${mm}-${dd}`;
    dateInput.setAttribute('min', minDate);
});