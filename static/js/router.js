(function(window, $){
    'use strict';

    String.prototype.capitalize = function() {
        return this.replace(/(?:^|\s)\S/g, function(a) { return a.toUpperCase(); });
    };

    var Router = window.SuperRouter = {},
        prevHash = '',
        routes = {
            '#requests': '#requests',
            '#sendrequests': '#sendrequests',
            '#deliveries': '#deliveries',
            '#pickups': '#pickups',
        },
        routeActions = {
            '#sendrequests': function(){
                $('.your-requests-table > tbody').empty();
                $.ajax({
                    type: "GET",
                    url: "/request",
                    data: {
                        hash: "sendrequests",
                    },
                    dataType: "text",
                    success: function(data) {
                        $(".your-requests-table").dataTable().fnDestroy();
                        $('.your-requests-table > tbody').html(data);
                        $().populateNearest('.your-requests-table');
                        $('.your-requests-table').dataTable( {
                            "columnDefs": [
                                { "width": "12%", "targets": 0 },
                                { "width": "40%", "targets": 1 },
                                { "width": "20%", "targets": 3 },
                            ],
                            "order": [[ 3, "desc" ]]
                        });
                        //$(".your-requests-table").DataTable({ "bDestroy": true });

                    },
                    error: function(data) {
                        console.log('Error');
                        console.log(data);
                    }
                });
            },
            '#deliveries': function(){
                $('.deliveries-table > tbody').empty();
                $.ajax({
                    type: "GET",
                    url: "/request",
                    data: {
                        hash: "deliveries",
                    },
                    dataType: "text",
                    success: function(data) {
                        $(".deliveries-table").dataTable().fnDestroy();
                        $('.deliveries-table > tbody').html(data);
                        $().populateNearest('.deliveries-table');
                        $('.deliveries-table').dataTable( {
                            "columnDefs": [
                                { "width": "12%", "targets": 0 },
                                { "width": "37%", "targets": 1 },
                                { "width": "15%", "targets": 2 },
                                { "width": "13%", "targets": 3 },
                                { "width": "16%", "targets": 4 },
                            ],
                            "order": [[ 4, "asc" ]]
                        });

                    },
                    error: function(data) {
                        console.log('Error');
                        console.log(data);
                    }
                });
            },
            '#requests': function(){
                $('.open-requests-table > tbody').empty();
                $.ajax({
                    type: "GET",
                    url: "/request",
                    data: {
                        hash: "requests",
                    },
                    dataType: "text",
                    success: function(data) {
                        $(".open-requests-table").dataTable().fnDestroy();
                        $('.open-requests-table > tbody').html(data);
                        $().populateNearest('.open-requests-table');
                        $('.open-requests-table').dataTable( {
                            "columnDefs": [
                                { "width": "12%", "targets": 0 },
                                { "width": "40%", "targets": 1 },
                                { "width": "17%", "targets": 3 },
                                { "width": "11%", "targets": 4 },
                            ],
                            "order": [[ 3, "asc" ]]
                        });
                    },
                    error: function(data) {
                        console.log('Error');
                        console.log(data);
                    }
                });
            },
            '#pickups': function(){
                $('.pickups-table > tbody').empty();
                $.ajax({
                    type: "GET",
                    url: "/request",
                    data: {
                        hash: "pickups",
                    },
                    dataType: "text",
                    success: function(data) {
                        $(".pickups-table").dataTable().fnDestroy();
                        $('.pickups-table > tbody').html(data);
                        $().populateNearest('.pickups-table');
                        $('.pickups-table').dataTable( {
                            "columnDefs": [
                                { "width": "15%", "targets": 0 },
                                { "width": "35%", "targets": 1 },
                                { "width": "20%", "targets": 3 },
                            ],
                            "order": [[ 3, "desc" ]]
                        });

                    },
                    error: function(data) {
                        console.log('Error');
                        console.log(data);
                    }
                });
            }
        };

    Router.setHashTarget = function (hash, target) {
        routes[hash] = target;
    };

    Router.onChange = function (targetSelector, callback) {
        routeActions[targetSelector] = callback;
        console.log(targetSelector);
    };


    var change = Router.change = function () {
        var hash = location.hash;
        var targetSelector = routes[hash];

        // The router has targetSelector defined.
        if (['#', '#/'].indexOf(hash) >= 0) {
            window.location = "/";
        }

        else if (targetSelector) {
            console.log(hash);
            prevHash = hash; // record history.

            hideAllSections();
            displaySelectedNav(hash);

            // show the targetSelector.
            $(targetSelector).css("display", "none");

            // set all the forms in the targetSelector to visible.
            $(targetSelector).find("form").each(function () {
                var targetForm = $(this);
                targetForm.removeClass("display-none");
                targetForm.css("display", "block"); //instead of fading in each form just fad in parent
            });

            // deselect the current menu item.
            $(".selected-nav-item").removeClass("selected-nav-item");

            // select new menu item.
            var start_pos = hash.indexOf('/') + 1;
            var end_pos = hash.indexOf('/', start_pos);
            var navItem = hash.substring(start_pos, end_pos);
            navItem = navItem.replace(/-/g, ' ').capitalize();
            $('span[title="' + navItem + '"').children().addClass("selected-nav-item");

            $('#contentModal').modal('hide');
            $(targetSelector).fadeIn("slow");
        }

        var targetAction = routeActions[targetSelector];
        // Execute defined route action.
        if (targetAction && typeof targetAction === 'function') {
            targetAction();
        }
    };

    // Private helper functions
    // ------------------------------------------------------------
    function hideAllSections() {
        $("section").each(function(){
            $(this).css("display","none");
        });
    }

    function displaySelectedNav (hashURL){
        $('.navbar-nav > li > a').removeClass('nav-active');
        $('a[href="'+hashURL+'"]').addClass('nav-active');
        
    }

    // Initialize Router
    (function () {
        $(document).ready(change);
        $(window).on('hashchange', change);
    })();

}(window, jQuery));