let socket;
if (location.protocol === "https:")
    socket = io.connect('https://' + document.domain, {secure: true});
else
    socket = io.connect('http://' + document.domain + ':' + location.port);


socket.on('json_response', function (response) {
    if (response["type"] === "start_game") {
        let opponent = response["opponent"];
        app.players[1].name = opponent["nickname"];
        app.players[1].wins = opponent["wins"];
        app.players[1].draws = opponent["draws"];
        app.players[1].loses = opponent["loses"];
        app.players[1].image = `/static/avatars/${opponent["avatar"]}`;

        app.showWaiting = false;
        app.showWin = false;
        app.showDraw = false;
        app.showLose = false;
        app.showPlayAgain = false;

        app.showPlay = true;

        let buttons = document.getElementsByClassName("choose_button");
        for (let i = 0; i < buttons.length; i++) {
            buttons[i].style.visibility = "visible";
        }
        curr_secs = 10;
        set_timer();
    } else if (response["type"] === "game_result") {
        app.showPlay = false;
        if (response["result"] === "win") {
            app.showWin = true;
            app.players[0].wins++;
            app.players[1].loses++;
        } else if (response["result"] === "lose") {
            app.showLose = true;
            app.players[0].loses++;
            app.players[1].wins++;
        } else {
            app.showDraw = true;
            app.players[0].draws++;
            app.players[1].draws++;
        }
    } else if (response["type"] === "play_again") {
        app.showPlayAgain = true;
    } else if (response["type"] === "update_rating") {
        app.players[0].rating = response["table"];
        app.players[1].rating = response["table"];
    }
    console.log(response);
})
;

function play_again() {
    socket.emit('json_message', {"type": "play_again"});
}

function new_game() {
    socket.emit('json_message', {"type": "new_game"});
    app.showWin = false;
    app.showDraw = false;
    app.showLose = false;
    app.showWaiting = true;
    app.players[1] = Object.assign({}, default_user);
}

function play_again_approve() {
    socket.emit('json_message', {"type": "play_again_approve"});
    app.showPlayAgain = false;
}
