angular.module('mapApp', ['ui.bootstrap']).config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('{[{');
    $interpolateProvider.endSymbol('}]}');
}).controller('MapCtrl', ['$scope', function ($scope) {
    // map & markers
    $scope.map = null;
    $scope.label = 1;
    $scope.markers = [];

    // used by both view and create
    $scope.eventTypes = [{
        "label": "Incidents",
        "values": [
            {key: "A", value: "A - alcohol use"},
            {key: "D", value: "D - drug use, sales, paraphenalia"},
            {key: "E", value: "E - fighting, bullying, yelling, public disturbance"},
            {key: "H", value: "H - harassment, cat-calling, sexual solicitations"},
            {key: "L", value: "L - loitering, individual blocking sidewalk, please include # of people"},
            {key: "P", value: "P - feces, urine, vomit"},
            {key: "V", value: "V - violence, weapons, threat of violence"},
            {key: "T", value: "T - traffic violations or unsafe driving"},
            {key: "X", value: "X - police presence or activity"},
            {key: "O", value: "O - other, please add comment"}
        ]
    }, {
        label: "Assets",
        values: [
            {key: "AA", value: "A - Assisting behaviors, helping, caring, interventions"},
            {key: "AB", value: "B - Beautification, cleaning, decorating, art"},
            {key: "AC", value: "C - Community connections, positive gatherings"},
            {key: "AN", value: "N - Nature, greenery, trees, potted plants, flowers"},
            {key: "AO", value: "O - Organizations, social services, desired businesses"},
            {key: "AR", value: "R - Recreation, kids playing, people exercising"},
            {key: "AS", value: "AS - Positive social interactions, friendliness, signs of respect"},
            {key: "AOO", value: "OO - Other"}
        ]
    }];

    // used for view
    $scope.format = 'shortDate';
    $scope.startDate = new Date();
    $scope.endDate = new Date();
    $scope.selectedEventTypes = {};

    // used for create
    $scope.email = $scope.conditions = $scope.starting = $scope.ending = $scope.association = null;
    $scope.viewOnly = window.viewOnly;
    $scope.date = new Date();

    // used for dropdowns
    $scope.open = function($event, type) {
        $event.preventDefault();
        $event.stopPropagation();

        $scope[type + 'Opened'] = true;
    };

    $scope.setAllEventValues = function(){
        $scope.allEventValues = [];
        for (var i = 0; i < $scope.eventTypes.length; i++) {
            var values = $scope.eventTypes[i].values;
            for (var j = 0; j < values.length; j++) {
                var option = $scope.eventTypes[i].values[j];
                $scope.allEventValues.push(option);
            };
        };
    };

    // Map
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

    $scope.clearMarkers = function(){
        if($scope.markers && $scope.markers.length){
            for (var i = $scope.markers.length - 1; i >= 0; i--) {
                $scope.markers[i].setMap(null);
                $scope.markers[i] = null;
            };
            $scope.markers = [];
        }
    }

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
        $scope.postMapInit();
    };

    $scope.postMapInit = function(){
        if(!$scope.viewOnly){
            google.maps.event.addListener($scope.map, 'click', $scope.addEvent);
        } else {
            $scope.applyFilters();
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

    // Edit
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
                k: marker.position.A,
                d: marker.position.F,
                type: marker.type,
                comment: marker.comment,
                people_involved: marker.people_involved
            });
        };
        return markers;
    };

    $scope.submit = function submit($event){
        $event.preventDefault();
        $event.stopPropagation();

        var payload = {
            email: "asdf", // $scope.email,
            conditions: $scope.conditions,
            starting: $scope.starting,
            ending: $scope.ending,
            date: $scope.date.toUTCString(),
            events: $scope.getMarkersForSubmit(),
            association: $scope.association
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


    // View events
    $scope.currentPage = 1;

    $scope.pageChanged = function() {
        $scope.applyFilters();
    };

  $scope.applyFilters = function($event){
    if($event){
        $event.preventDefault();
        $event.stopPropagation();
    }

    // ensure start is at beginning of day, end at end of day
    $scope.startDate.setHours(0);
    $scope.startDate.setMinutes(0);
    $scope.startDate.setSeconds(0);
    $scope.endDate.setHours(23);
    $scope.endDate.setMinutes(59);
    $scope.endDate.setSeconds(59);

    var filters = {
        start: $scope.startDate.toUTCString(),
        end: $scope.endDate.toUTCString(),
        types: Object.keys($scope.selectedEventTypes),
        page: $scope.currentPage
    };

    $.getJSON("/view-json", filters, function(data){
        if(data){
            $scope.reports = data.reports;
            $scope.total = data.total;
            $scope.clearMarkers();
            if(data.events){
                $scope.addViewEvents(data.events);
            }
            $scope.$apply();
        }
    });
  }

  $scope.setAllEventValues();
}]);





