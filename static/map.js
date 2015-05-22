angular.module('mapApp', []).config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[{');
    $interpolateProvider.endSymbol('}]}');
}).controller('MapCtrl', function ($scope) {
    $scope.map = null;
    $scope.label = 1;

    $scope.markers = [];
    $scope.email = $scope.conditions = $scope.starting = $scope.ending = null;
    $scope.date = new Date();

    $scope.addEvent = function addEvent(sq){
        $scope.markers.push(new MarkerWithLabel({
            position: new google.maps.LatLng(sq.latLng.A, sq.latLng.F),
            url: '/',
            animation: google.maps.Animation.DROP,
            map: $scope.map,
            labelContent: $scope.label++,
            labelAnchor: new google.maps.Point(22, 0),
            labelClass: 'labels'
        }));
        $scope.$apply();
    };

    $scope.removeMarker = function removeMarker(marker){
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

        if(window.events){
            $scope.addViewEvents(events);
        }
    };

    $scope.addViewEvents = function addViewEvents(events){
        for (var i = events.length - 1; i >= 0; i--) {
            var e = events[i];
            $scope.markers.push(new MarkerWithLabel({
                position: new google.maps.LatLng(e.latitude, e.longitude),
                url: '/',
                animation: google.maps.Animation.DROP,
                map: $scope.map,
                labelContent: e.event_type,
                labelAnchor: new google.maps.Point(22, 0),
                labelClass: 'labels'
            }));
        };
    };

    $scope.getValidationMessages = function getValidationMessages(){
        var messages = [];
        if($scope.markers.length == 0){
            messages.push("add markers");
        } else {
            for (var i = $scope.markers.length - 1; i >= 0; i--) {
                if(!$scope.markers[i].type){
                    messages.push("select a type for each marker");
                }
            };
        }

        // if(!$scope.email){
        //     messages.push("include your email address");
        // }

        if(messages.length){
            return "Please " + messages.join(" and ") + " before submitting.";
        }
        return null;
    };

    $scope.getMarkersForSubmit = function getMarkersForSubmit(){
        var markers = [];
        for (var i = $scope.markers.length - 1; i >= 0; i--) {
            var marker = $scope.markers[i];
            markers.push({
                k: marker.position.k,
                d: marker.position.D,
                type: marker.type,
                comment: marker.comment,
                people_involved: marker.people_involved
            });
        };
        return markers;
    };

    $scope.submit = function submit(){
        var payload = {
            email: "asdf", // $scope.email,
            conditions: $scope.conditions,
            starting: $scope.starting,
            ending: $scope.ending,
            date: $scope.date.toUTCString(),
            events: $scope.getMarkersForSubmit()
        };

        $.ajax({
            type: "POST",
            url: "/save",
            processData: false,
            contentType: 'application/json',
            data: JSON.stringify(payload),
            success: function(data) {
                if(data && data.success){
                    for (var i = $scope.markers.length - 1; i >= 0; i--) {
                        $scope.markers[i].setMap(null);
                    };
                    $scope.markers = [];
                    $scope.label = 1;
                    $scope.showMessage("Saved!", "bg-success", true);
                } else {
                    message = (data && data.message) ? data.message : "";
                    $scope.showMessage("Error: " + message, "bg-danger");
                }
            }
        });
    };

    $scope.submitClass = function submitClass(){
        return ($scope.markers.length == 0) ? "" : "btn-primary";
    };

    $scope.showMessage = function showMessage(msg, cls, hide){
        $scope.message = msg;
        $scope.messageClass = cls;
        $scope.$apply();
        var msgSurround = $(".msgSurround").slideDown();

        if(hide){
            setTimeout(function(){
                msgSurround.slideUp();
            }, 3000)
        }
    };

    window.$scope = $scope;

    google.maps.event.addDomListener(window, 'load', $scope.initMap);
});





