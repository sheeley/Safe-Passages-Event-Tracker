angular.module('mapApp', []).config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[{');
    $interpolateProvider.endSymbol('}]}');
}).controller('MapCtrl', function ($scope) {
    $scope.map = null;
    $scope.markers = [];
    $scope.label = 1;

    $scope.addEvent = function addEvent(sq){
        $scope.markers.push(new MarkerWithLabel({
            position: new google.maps.LatLng(sq.latLng.k, sq.latLng.D),
            url: '/',
            animation: google.maps.Animation.DROP,
            map: $scope.map,
            labelContent: $scope.label++,
            labelAnchor: new google.maps.Point(22, 0),
            labelClass: 'labels'
        }));
        $scope.$apply();
    };

    $scope.remove = function removeMarker(marker){
        var index = $scope.markers.indexOf(marker);
        if(!marker || index == -1 || !confirm("Remove this marker?")){
            return;
        }
        marker.setMap(null);
        $scope.markers.splice(index, 1);
        $scope.renumberMarkers();
    };

    $scope.renumberMarkers = function renumberMarkers(){
        $scope.label = 1;
        for (var i = 0; i < $scope.markers.length; i++) {
            var marker = $scope.markers[i];
            marker.labelContent = $scope.label++;
            marker.label.setContent();
        };
    }

    $scope.initMap = function initMap(){
        var mapOptions = {
            disableDefaultUI: true,
            disableDoubleClickZoom: true,
            center: new google.maps.LatLng(37.783997, -122.412722),
            scrollWheel: false,
            zoom: 16,
            draggable: true,
            scrollwheel: false
        };

        $scope.map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);
        google.maps.event.addListener($scope.map, 'click', $scope.addEvent);
    };

    google.maps.event.addDomListener(window, 'load', $scope.initMap);
});





