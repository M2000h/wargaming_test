const avatars_list = ["1.gif", "2.svg", "3.svg", "4.svg", "5.svg", "6.svg", "7.svg", "8.svg", "9.svg", "10.svg"];
let curr_avatar = 0;

function filter_nickname(input_element) {
    input_element.value = input_element.value.replace(/[^a-zA-Zа-яА-Я0-9]/g, '');
}

function submit_nickname(input_element) {
    if (event.key === 'Enter') {
        if (input_element.value.length === 0) {
            alert("input your name!");
            return;
        }
        socket.emit('json_message',
            {
                "type": "new_user",
                "nickname": input_element.value,
                "avatar": avatars_list[curr_avatar],
            });
        app.showNicknameInput = false;
        app.showBattleground = true;
        app.p1_name = input_element.value;
        app.p1_image = "/static/avatars/" + avatars_list[curr_avatar];
    }
}

function next_avatar() {
    curr_avatar++;
    curr_avatar %= avatars_list.length;
    app.p1_image = "/static/avatars/" + avatars_list[curr_avatar];
}

function prev_avatar() {
    curr_avatar--;
    curr_avatar += avatars_list.length;
    curr_avatar %= avatars_list.length;
    app.p1_image = "/static/avatars/" + avatars_list[curr_avatar];
}