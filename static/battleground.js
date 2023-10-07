function make_move(move) {
    socket.emit('json_message', {"type": "move", "move": move.id});
    let buttons = document.getElementsByClassName("choose_button");
    for (let i = 0; i < buttons.length; i++) {
        if (buttons[i].id !== move.id)
            buttons[i].style.visibility = "hidden";
    }
}

function getColorByPercentage(percentage) {
    if (percentage < 0) {
        percentage = 0;
    } else if (percentage > 100) {
        percentage = 100;
    }

    let green = Math.min(255, Math.floor(255 * (percentage / 50)));
    let red = Math.min(255, Math.floor(255 * ((100 - percentage) / 50)));
    let blue = 0;

    return `rgb(${red}, ${green}, ${blue})`;
}

let curr_secs = 0;

function set_timer() {
    curr_secs -= .025;
    let perc = curr_secs / 10 * 100;
    document.getElementById("progress-bar-front").style.width = `${perc}%`;
    document.getElementById("progress-bar-front").style.background = getColorByPercentage(perc);
    if (curr_secs > 0) {
        setTimeout(function () {
            set_timer()
        }, 25)
    } else {
        document.getElementById("progress-bar-front").style.width = `0`;
    }
}