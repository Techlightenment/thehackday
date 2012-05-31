
$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};
    updater.start();
});

var updater = {
    socket: null,

    start: function() {
        var url = "ws://" + location.host + "/smallgraph?hashtag=jubilee";
        if ("WebSocket" in window) {
        updater.socket = new WebSocket(url);
        } else {
            updater.socket = new MozWebSocket(url);
        }
        updater.socket.onmessage = function(event) {
            console.log(JSON.parse(event.data));
        }
    },

};
