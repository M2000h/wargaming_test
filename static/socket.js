let socket;
if (location.protocol === "https:")
    socket = io.connect('https://' + document.domain, {secure: true});
else
    socket = io.connect('http://' + document.domain + ':' + location.port);


socket.on('json_response', function (response) {
    if (response["type"] === "start_game") {
        let opponent = response["opponent"];
        app.p2_name = opponent["nickname"];
        app.p2_wins = opponent["wins"];
        app.p2_draws = opponent["draws"];
        app.p2_loses = opponent["loses"];
        app.p2_image = `/static/avatars/${opponent["avatar"]}`;

        app.showWaiting = false;
        app.showWin = false;
        app.showDraw = false;
        app.showLose = false;

        app.showPlayAgain = false;

        document.getElementById("play_block").style.display = "block";
        let buttons = document.getElementsByClassName("choose_button");
        for (let i = 0; i < buttons.length; i++) {
            buttons[i].style.visibility = "visible";
        }
        curr_secs = 10;
        set_timer();
    } else if (response["type"] === "game_result") {
        document.getElementById("play_block").style.display = "none";
        if (response["result"] === "win") {
            app.showWin = true;
            app.p1_wins++;
            app.p2_loses++;
        } else if (response["result"] === "lose") {
            app.showLose = true;
            app.p1_loses++;
            app.p2_wins++;
        } else {
            app.showDraw = true;
            app.p1_draws++;
            app.p2_draws++;
        }
    } else if (response["type"] === "play_again") {
        app.showPlayAgain = true;
    } else if (response["type"] === "update_rating") {
        document.getElementById("p1_rating").innerHTML = "";
        document.getElementById("p2_rating").innerHTML = "";
        for (let i = 0; i < response["table"].length; i++) {
            let s = document.createElement("div");
            s.innerText = `${i + 1}. ${response["table"][i][0]} ${response["table"][i][1]}`;
            let s1 = s.cloneNode(true);
            if (response["table"][i][0] === app.p1_name)
                s.className = "class_red_rating"
            else if (response["table"][i][0] === app.p2_name)
                s1.className = "class_red_rating"
            document.getElementById("p1_rating").appendChild(s);
            if (app.p1_name !== "...")
                document.getElementById("p2_rating").appendChild(s1);
        }
    }
    console.log(response);
});

function play_again() {
    socket.emit('json_message', {"type": "play_again"});
}

function new_game() {
    socket.emit('json_message', {"type": "new_game"});
    app.showWin = false;
    app.showDraw = false;
    app.showLose = false;
    app.showWaiting = true;
    app.p2_name = "...";
    app.p2_image = "/static/avatars/question.png";
    app.p2_wins = "-";
    app.p2_draws = "-";
    app.p2_loses = "-";
    document.getElementById("p2_rating").innerHTML = "";
}

function play_again_approve() {
    socket.emit('json_message', {"type": "play_again_approve"});
    app.showPlayAgain = false;
}
