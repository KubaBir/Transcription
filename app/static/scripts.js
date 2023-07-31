const spinner = document.getElementById('spinner')
const fileUpload = document.getElementById('audio_input');
const playback1 = document.getElementById('playback1');
const submitButton1 = document.getElementById('submitButton1');
const listenerLang = document.getElementById('listener_lang');
const speakerLang = document.getElementById('speaker_lang');
submitButton1.addEventListener('click', saveAudio);

const startButton = document.getElementById('start');
const postCommandButton = document.getElementById('submitButton3');
const recordedAudioContainer = document.getElementById('recordedAudioContainer');
const playback2 = document.getElementById('playback2');
const chatInput = document.getElementById('chatInput');
const chatSendButton = document.getElementById('chatSendButton');

chatSendButton.addEventListener('click', uploadMessage);

let chunks = [];
let mediaRecorder = null;
let audioBlob = null;

let latestPlayer = null;
let latestTranslation = null;

let webSocket = null;

startButton.addEventListener('click', record);
postCommandButton.addEventListener('click', postCommand);

fileUpload.addEventListener('change', function (e) {
    submitButton1.style.visibility = "visible";
    submitButton1.disabled = false;
    playback1.style.visibility = "visible";
    const file = e.target.files[0];
    const url = URL.createObjectURL(file);
    playback1.src = url;
});

function postCommand(audioSource) {
    audioSource = audioBlob;
    const formData = new FormData();
    formData.append('audio', audioSource, filename = 'recording.wav');
    formData.append('to_language', listenerLang.value);

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
    d.className = 'message';

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
    let container = document.getElementById("outputfield");
    container.appendChild(d);
    container.scrollTop = container.scrollHeight;

    latestTranslation = btn_translate;
    latestPlayer = player;

    return player;
}

function saveAudio() {
    if (document.getElementById("audio_input").value == "") {
        return false;
    }
    submitButton1.disabled = true;
    spinner.style.visibility = "visible";
    var input = document.getElementById('audio_input');
    getTransctipt(input.files[0]);
}

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

function record() {
    startButton.style.backgroundColor = "green";
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
        const data = JSON.parse(e.data);
        chatInput.value = data;
        console.log(data.message)
    };

    if (!mediaRecorder) {
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
                startButton.style.backgroundColor = "red";
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
                text: speakerLang.value,
                audioBlob: base64data
            };
            webSocket.send(JSON.stringify(msg));
        }

    }
    function mediaRecorderStop() {
        startButton.style.backgroundColor = "white";
        playback2.style.visibility = "visible"
        postCommandButton.style.visibility = "visible"
        audioBlob = new Blob(chunks, { type: 'audio/wav' });

        const audioURL = window.URL.createObjectURL(audioBlob);
        playback2.src = audioURL;
        mediaRecorder = null;
        chunks = [];

    }
};

function uploadMessage() {
    const msg = chatInput.value;
    if (msg == "") return;

    console.log(msg);
    console.log(listenerLang.value);

    // Translate
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
            console.log(data);
            let player = createMessage(data);
            const language = listenerLang.value;
            const msg = data['translation'];

            return [msg, language, player];
        })
        .then(([msg, language, player]) => getAudio(msg, language, player))
        .finally(() => {
            chatInput.value = "";
        })
        .catch((errors) => console.log(errors))
}

// Insert dummy message
function insert() {
    createMessage({ 'original': "testfkdjfgbkajsfbksja dbfkkdsjbvaksdjvbakjsdbvkjas bdkvjabskdjvbkasjdbvkjabsdvd ksjsjadvfmznvckdfvsdjfhsvmessage" });
}