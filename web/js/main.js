(function() {
    var canvas_size = 600, 
        shuttle_size = 32,
        rocket_size = 32,
        scale_factor,
        grid_size;

    var game_over = false, game_started = false;
    var shuttles = [], 
        rockets = [];

    var socket = null;
    var isopen = false;

    var server_ip  = "127.0.0.1";
    var server_port = "9000";



    // Set up the canvas for the arena
    var then = Date.now();
    var canvas = document.createElement("canvas");
    var ctx = canvas.getContext("2d");
    canvas.width = canvas_size;
    canvas.height = canvas_size;
    document.body.appendChild(canvas);


    // Pre-load Images
    var bgImage = new Image();
    bgImage.onload = function () {
        bgReady = true;
    };
    bgImage.src = "img/background.png";

    // Shuttle image
    var shuttleReady = false;
    var shuttleImage = new Image();
    shuttleImage.onload = function () {
            shuttleReady = true;
    };
    shuttleImage.src = "img/shuttle.png";

    // Rocket image
    var rocketReady = false;
    var rocketImage = new Image();
    rocketImage.onload = function () {
     rocketReady = true;
    };
    rocketImage.src = "img/rocket.png";

    window.onload = function() {

        // connect to the server
        socket = new WebSocket("ws://" + server_ip + ":" + server_port);
        socket.binaryType = "arraybuffer";

        socket.onopen = function() {
            console.log("Connected!");
            isopen = true;
        };

        socket.onmessage = function(e) {
            var game_msg;
            console.log("Text message received: " + e.data);
            game_msg = JSON.parse(e.data);
            if (game_msg['type'] === 'init') {
                // initialize the game
                console.log('grid size is ' + String(game_msg['grid_size']));
                grid_size = game_msg['grid_size'];
                scale_factor = canvas_size / grid_size;
                console.log('player names are:' + String(game_msg['player_names']));
                for (var i=0; i<game_msg['player_names'].length; i++) {
                    var shuttle = {};
                    shuttle.name = game_msg['player_names'][i];
                    shuttle.x = 0; 
                    shuttle.y = 0; 
                    shuttle.image = shuttleImage;
                    shuttle.rocket = null;
                    shuttles.push(shuttle);
                }
                game_started = true;
            } else if(game_msg['type'] === 'update') {
                // update shuttle and rocket position and adapt to fit the canvas size
                for (var i=0; i<game_msg['shuttles'].length; i++) {
                    var shuttle = game_msg['shuttles'][i];
                    shuttles[i].x = shuttle_size + shuttle.x * scale_factor - 2*shuttle_size;
                    shuttles[i].y = shuttle_size + shuttle.y * scale_factor - 2*shuttle_size;
                    if (shuttle.hasOwnProperty('rocket')) {
                        shuttle.rocket = {'x': rocket_size + shuttle.rocket.x * scale_factor - 2*rocket_size,
                                          'y': rocket_size + shuttle.rocket.y * scale_factor - 2*rocket_size};
                    }
                }
            }
        };

        socket.onclose = function(e) {
            console.log("Connection closed.");
            socket = null;
            isopen = false;
        };
    };


    var render = function () {
        // draw the bg
        ctx.drawImage(bgImage, 0, 0);
        // then draw the shuttles
        for (var i=0; i<shuttles.length; i++) {
            ctx.drawImage(shuttles[i].image, shuttles[i].x, shuttles[i].y);
            ctx.font="20px Georgia";
            ctx.fillStyle = "red";
            ctx.textAlign = "center";
            ctx.fillText(shuttles[i].name, shuttles[i].x + 10 + shuttle_size , shuttles[i].y);

            if (shuttles[i].rocket) {
                ctx.drawImage(shuttles[i].rocketImage, shuttles[i].rocket.x, shuttles[i].rocket.y);
            }
        }
        // the server will check for collisions

        // game is over
    };

    var update = function(modifier) {
        // poll server
        if (isopen) {
            socket.send("s"); // poll the server
        } 
    };

    // the main loop
    var main = function () {
        var now = Date.now();
        var delta = now - then;
        render();

        //update(delta / 1000);
        if (!game_over) {
            if (game_started) {
                update();
                render();

                then = now;
            }
            requestAnimationFrame(main);
        }
    };

    main(); // start the main loop


}());
