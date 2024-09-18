var options = {
    types: ['address']
}

// create autocomplete objects for origin and destination inputs
function initializeAutocomplete() {
    var fromInput = document.getElementById('from');
    var toInput = document.getElementById('to');

    var fromAutocomplete = new google.maps.places.Autocomplete(fromInput, options);
    var toAutocomplete = new google.maps.places.Autocomplete(toInput, options);
}

function calculateTravelTime(from, to, callback) {
    var service = new google.maps.DistanceMatrixService(); // initialize the distance service to calculate travel time
    service.getDistanceMatrix({
        origins: [from],
        destinations: [to],
        travelMode: google.maps.TravelMode.DRIVING,
    }, function(response, status) {
        if (status === google.maps.DistanceMatrixStatus.OK) {
            var travelTime = response.rows[0].elements[0].duration.text;
            callback(travelTime);
        } else {
            console.error('Error calculating travel time:', status);
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // initialize autocomplete
    initializeAutocomplete();

    // calculate travel time for each ride
    var rides = document.querySelectorAll('.card-title');

    rides.forEach(function(ride) {
        var from = ride.getAttribute('data-from');
        var to = ride.getAttribute('data-to');
        var travelTimeElement = ride.closest('.card-body').querySelector('.travel-time');
        
        calculateTravelTime(from, to, function(travelTime) {
            travelTimeElement.textContent = travelTime;
        });
    });
});

