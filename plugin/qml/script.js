"use strict";
/*global print, Service, Qt, appWindow*/


function MockHTTPRequest() {
    return Qt.createQmlObject("import Service 1.0; MockHTTPRequest {}",
        appWindow, "MockHTTPRequest");
}

function onLoad() {
    var xhr = new MockHTTPRequest();
    xhr.requested.connect(function(reply) {
        print(reply);
    });

    xhr.request("POST", "/endpoint", { "data": "value" });

    print("request() was made");
}