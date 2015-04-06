var map;

function addEvent(sq){
    var marker = new google.maps.Marker({
        position: new google.maps.LatLng(sq.latLng.k, sq.latLng.D),
        url: '/',
        animation: google.maps.Animation.DROP
    });
    marker.setMap(map);
}

$(document).ready(function(){
    google.maps.event.addDomListener(window, 'load', initialize);

    function initialize() {
        var latlng = new google.maps.LatLng(37.782047, -122.414782);

        var mapOptions = {
            disableDefaultUI: true,
            disableDoubleClickZoom: true,
            center: latlng,
            scrollWheel: false,
            zoom: 16,
            draggable: false,
            scrollwheel: false
        };

        map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);
        google.maps.event.addListener(map, 'click', addEvent);
    };
});
