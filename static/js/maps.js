// set map options
var myLatLng = {lat: 51.5074, lng: 0.1278};
var mapOptions = {
    center: myLatLng,
    zoom: 7,
    mapTypeId: google.maps.MapTypeId.ROADMAP
};

var map = new google.maps.Map(document.getElementById('googleMap'), mapOptions);

// create autocomplete objects for all inputs
var options = {
    types: ['address']
}

function initializeAutocomplete() {
    var fromInput = document.getElementById('from');
    var toInput = document.getElementById('to');

    var fromAutocomplete = new google.maps.places.Autocomplete(fromInput, options);
    var toAutocomplete = new google.maps.places.Autocomplete(toInput, options);
}

document.addEventListener('DOMContentLoaded', function() {
    initializeAutocomplete();
});