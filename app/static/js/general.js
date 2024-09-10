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