let socket;
if (location.protocol === "https:")
    socket = io.connect('https://' + document.domain, {secure: true});
else
    socket = io.connect('http://' + document.domain + ':' + location.port);

let wins = 0, draws = 0, loses = 0, nickname, opponent_nickname;

socket.on('json_response', function (response) {
    if (response["type"] === "start_game") {
        opponent_nickname = response["opponent"]["nickname"];
        document.getElementById("player_2_name").innerText = opponent_nickname;
        document.getElementById("p2_wins").innerText = response["opponent"]["wins"];
        document.getElementById("p2_draws").innerText = response["opponent"]["draws"];
        document.getElementById("p2_loses").innerText = response["opponent"]["loses"];
        document.getElementById("op_avatar").setAttribute("src", "/static/avatars/" + response["opponent"]["avatar"]);
        document.getElementById("waiting_block").style.display = "none";
        document.getElementById("win_block").style.display = "none";
        document.getElementById("lose_block").style.display = "none";
        document.getElementById("draw_block").style.display = "none";
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
            document.getElementById("win_block").style.display = "block";
            wins++;

        } else if (response["result"] === "lose") {
            document.getElementById("lose_block").style.display = "block";
            loses++;
        } else {
            document.getElementById("draw_block").style.display = "block";
            draws++;
        }
        document.getElementById("p1_wins").innerText = wins;
        document.getElementById("p1_draws").innerText = draws;
        document.getElementById("p1_loses").innerText = loses;

        document.getElementById("p2_wins").innerText = response["opponent"]["wins"];
        document.getElementById("p2_draws").innerText = response["opponent"]["draws"];
        document.getElementById("p2_loses").innerText = response["opponent"]["loses"];

    } else if (response["type"] === "play_again") {
        document.getElementById("play_again_block").style.display = "flex";
    } else if (response["type"] === "update_rating") {
        document.getElementById("p1_rating").innerHTML = "";
        document.getElementById("p2_rating").innerHTML = "";
        for (let i = 0; i < response["table"].length; i++) {
            let s = document.createElement("div");
            s.innerText = `${i + 1}. ${response["table"][i][0]} ${response["table"][i][1]}`;
            let s1 = s.cloneNode(true);
            if (response["table"][i][0] === nickname)
                s.className = "class_red_rating"
            else if (response["table"][i][0] === opponent_nickname)
                s1.className = "class_red_rating"
            document.getElementById("p1_rating").appendChild(s);
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
    document.getElementById("win_block").style.display = "none";
    document.getElementById("lose_block").style.display = "none";
    document.getElementById("draw_block").style.display = "none";
    document.getElementById("waiting_block").style.display = "block";
    document.getElementById("player_2_name").innerText = "...";
    document.getElementById("op_avatar").setAttribute("src", "/static/avatars/question.png");
    document.getElementById("p2_wins").innerText = "-";
    document.getElementById("p2_draws").innerText = "-";
    document.getElementById("p2_loses").innerText = "-";
    document.getElementById("p2_rating").innerHTML = "";
}

function play_again_approve() {
    socket.emit('json_message', {"type": "play_again_approve"});
    document.getElementById("play_again_block").style.display = "none";
}
