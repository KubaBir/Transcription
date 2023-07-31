const spinner = document.getElementById('spinner')

const listenerLang = document.getElementById('listener_lang');
const speakerLang = document.getElementById('speaker_lang');

const recordCommandButton = document.getElementById('recordCommandButton');
const postCommandButton = document.getElementById('postCommandButton');
const commandHolder = document.getElementById('commandHolder');
recordCommandButton.addEventListener('click', recordCommand);
postCommandButton.addEventListener('click', postCommand);

const recordMsgButton = document.getElementById('recordMsgButton');
recordMsgButton.addEventListener('click', recordMsg);

const chatInput = document.getElementById('chatInput');
const chatSendButton = document.getElementById('chatSendButton');
chatSendButton.addEventListener('click', uploadMessage);

let chatBox = document.getElementById("outputfield");


let mediaRecorder = null;

let chunks = [];
let audioBlob = null;

let commandChunks = [];
let commandAudioBlob = null;

let latestPlayer = null;
let latestTranslation = null;

let webSocket = null;

var conversataion = [];

var messageEnded = false;


// fileUpload.addEventListener('change', function (e) {
//     submitButton1.style.visibility = "visible";
//     submitButton1.disabled = false;
//     playback1.style.visibility = "visible";
//     const file = e.target.files[0];
//     const url = URL.createObjectURL(file);
//     playback1.src = url;
// });

function recordCommand() {
    if (!mediaRecorder) {
        navigator.mediaDevices.getUserMedia({
            audio: true,
        })
            .then((stream) => {
                recordCommandButton.style.backgroundColor = "green";

                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();
                mediaRecorder.ondataavailable = mediaRecorderDataAvailable;
                mediaRecorder.onstop = mediaRecorderStop;
            })
            .catch((err) => {
                alert(`The following error occurred: ${err}`);
                recordMsgButton.style.backgroundColor = "red";
            });
    } else {
        mediaRecorder.stop();
    }

    function mediaRecorderDataAvailable(e) {
        commandChunks.push(e.data);
    }

    function mediaRecorderStop() {
        recordCommandButton.style.backgroundColor = "white";

        commandAudioBlob = new Blob(commandChunks, { type: 'audio/mp3' });
        const audioURL = window.URL.createObjectURL(commandAudioBlob);
        commandHolder.src = audioURL;
        mediaRecorder = null;
        commandChunks = [];
    }
}

function postCommand() {
    audioSource = commandAudioBlob;
    if (audioSource == null) return;
    spinner.style.visibility = "visible";

    const formData = new FormData();
    formData.append('audio', audioSource, filename = 'recording.wav');
    formData.append('to_language', speakerLang.value);

    fetch('/api/command/', {
        method: 'POST',
        body: formData
    })
        .then((response) => response.json())
        .then((data) => {
            console.log(data);
            if (data == 'translate') {
                latestTranslation.click();
            } else if (data == 'read') {
                latestPlayer.play();
            }
        })
        .catch((errors) => console.log(errors))
        .finally(() => {
            spinner.style.visibility = "hidden";
        })

}

function getTransctipt(audioSource) {
    const formData = new FormData();
    formData.append('audio', audioSource, 'recording.wav');
    formData.append('to_language', listenerLang.value);
    fetch('/api/transcribe/', {
        method: 'POST',
        body: formData
    })
        .then((response) => response.json())
        .then((data) => {
            let player = createMessage(data);
            playback2.style.visibility = "hidden"
            spinner.style.visibility = "hidden";
            playback1.style.visibility = 'hidden';
            submitButton1.style.visibility = 'hidden';
            fileUpload.value = "";

            return [data['original'], player];

        })
        .then(([prompt, player]) => getAudio(prompt, player))
        .catch((errors) => {
            console.log(errors);
            spinner.style.visibility = "hidden";

        })

}

function createMessage(data) {
    let d = document.createElement("div");
    d.className = 'message prompt';

    let original = document.createElement("div");
    original.textContent = data["original"];
    original.className = 'original';

    let translation = document.createElement("div");
    translation.textContent = data["translation"];
    translation.className = 'translation';

    let player = document.createElement("audio");
    player.setAttribute("controls", "");
    player.setAttribute("src", "");
    player.className = 'message_audio_player';

    let btn_translate = document.createElement("button");
    btn_translate.textContent = 'X'
    btn_translate.className = 'btn_translate';
    btn_translate.addEventListener('click', function () {
        let f = this.parentElement.firstChild;
        let s = f.nextSibling;
        if (s.textContent == "") return false;

        if (f.style.visibility == 'hidden') {
            f.style.visibility = 'visible';
            let s = f.nextSibling;
            s.style.visibility = 'hidden';
        } else {
            f.style.visibility = 'hidden';
            let s = f.nextSibling;
            s.style.visibility = 'visible';
        }
    })

    d.appendChild(original);
    d.appendChild(translation);
    d.appendChild(player);
    d.appendChild(btn_translate);
    chatBox.appendChild(d);
    chatBox.scrollTop = chatBox.scrollHeight;

    latestTranslation = btn_translate;
    latestPlayer = player;

    conversataion = [];
    const messages = chatBox.children
    for (var i = 0; i < messages.length; i++) {
        var message = messages[i];
        if (message.classList.contains('prompt')) {
            conversataion.push({ 'role': 'user', 'content': message.firstChild.innerHTML })
        } else if (message.classList.contains('assistant')) {
            conversataion.push({ 'role': 'assistant', 'content': message.firstChild.innerHTML })
        }
    }

    return player;
}

// function saveAudio() {
//     if (document.getElementById("audio_input").value == "") {
//         return false;
//     }
//     submitButton1.disabled = true;
//     spinner.style.visibility = "visible";
//     var input = document.getElementById('audio_input');
//     getTransctipt(input.files[0]);
// }

// Text --> Audio file
function getAudio(text, language, player) {
    data = {
        'prompt': text,
        'language': language
    }
    fetch(`/api/voiceover/`, {
        method: "POST",
        body: JSON.stringify(data),
        headers: {
            "Content-Type": "application/json",
        },
    })
        .then(response => response.blob())
        .then(audioBlob => {
            const audioURL = URL.createObjectURL(audioBlob);
            player.src = audioURL;
        })
        .catch((errors) => console.log(errors))

}

function getChatResponse() {
    fetch(`/api/chat/`, {
        method: "POST",
        body: JSON.stringify({ 'messages': conversataion }),
        headers: {
            "Content-Type": "application/json",
        },
    })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(errors => console.log(errors))
}

function recordMsg() {
    recordMsgButton.style.backgroundColor = "green";
    if (!webSocket || webSocket.readyState !== WebSocket.OPEN) {
        webSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/chat/'
        );
    }
    webSocket.onopen = function (e) {
        console.log("Socket opened");
    };
    webSocket.onclose = function (e) {
        console.error('Chat socket closed unexpectedly');
    };
    webSocket.onmessage = function (e) {
        if (messageEnded) return;
        const data = JSON.parse(e.data);
        chatInput.value = data.message;
        // console.log(data.message)

        if (data.done && mediaRecorder) {
            messageEnded = true;
            mediaRecorder.stop();
            console.log("Got the stop command");
            uploadMessage(getChatResponse);

            // console.log(data.response);
            // createMessage({ 'originial': data.response.content, 'translation': '' })
        }
    };

    if (!mediaRecorder) {
        messageEnded = false;
        navigator.mediaDevices.getUserMedia({
            audio: true,
        })
            .then((stream) => {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start(1000);
                mediaRecorder.ondataavailable = mediaRecorderDataAvailable;
                mediaRecorder.onstop = mediaRecorderStop;
            })
            .catch((err) => {
                alert(`The following error occurred: ${err}`);
                recordMsgButton.style.backgroundColor = "red";
            });
    } else {
        mediaRecorder.stop();
    }
    function mediaRecorderDataAvailable(e) {
        chunks.push(e.data);
        audioBlob = new Blob(chunks, { type: 'audio/wav' });

        var reader = new FileReader();
        reader.readAsDataURL(audioBlob);
        reader.onloadend = function () {
            var base64data = reader.result;
            const msg = {
                messages: conversataion,
                text: speakerLang.value,
                audioBlob: base64data
            };
            webSocket.send(JSON.stringify(msg));
        }

    }
    function mediaRecorderStop() {
        recordMsgButton.style.backgroundColor = "white";
        // playback2.style.visibility = "visible"
        // postCommandButton.style.visibility = "visible"
        // audioBlob = new Blob(chunks, { type: 'audio/wav' });
        // const audioURL = window.URL.createObjectURL(audioBlob);
        // playback2.src = audioURL;
        mediaRecorder = null;
        chunks = [];

    }
};

// Translate msg from chatInput and crate a chat message with TTS
function uploadMessage(callback) {
    const msg = chatInput.value;
    if (msg == "") return;

    // Translate and send for TTS
    data = {
        'prompt': msg,
        'to_language': listenerLang.value
    }
    fetch(`/api/translate/`, {
        method: "POST",
        body: JSON.stringify(data),
        headers: {
            "Content-Type": "application/json",
        },
    })
        .then(response => response.json())
        .then(data => {
            let player = createMessage(data);
            const language = listenerLang.value;
            const msg = data['translation'];

            return [msg, language, player];
        })
        .then(([msg, language, player]) => getAudio(msg, language, player))
        .catch((errors) => console.log(errors))
        .finally(() => {
            chatInput.value = "";
            callback();
        })
}

// Insert dummy message
function insert() {
    createMessage({ 'original': "testfkdjfgbkajsfbksja dbfkkdsjbvaksdjvbakjsdbvkjas bdkvjabskdjvbkasjdbvkjabsdvd ksjsjadvfmznvckdfvsdjfhsvmessage" });
}