<template>
  <div id="app" @mousemove="mouseMove" style="width:100vw;height:100vh">
    <form>
      <textarea id="incoming"></textarea>
      <button type="submit">submit</button>
    </form>
    <pre id="outgoing"></pre>

    <button @click="speak('hello worldo')">This is a button. Click to Speek</button>
    <button @click="speechToText()">This is a button. Click to Record</button>
    <button id="musicButton" @click="startMusic">This is a button. Click to Music</button>

    <p>Spoken Text: {{interimRecognizedSpeech}} - {{ recognizedSpeech }}</p>
    <p>Mouse Position: {{ JSON.stringify([mouseX, mouseY]) }}</p>
    <div
      v-for="conversation in conversations"
      :key="conversation.id"
      style="border:2px solid black;"
    >
      <p v-for="message in conversation.messages" :key="message.id">
        <b>{{ friendlyNames[message.model] }}</b>
        <br />
        {{ message.message }}
        <br />
      </p>
    </div>
    <!--<HelloWorld msg="Welcome to Your Vue.js App" />-->
  </div>
</template>

<script>
//import HelloWorld from "./components/HelloWorld.vue";
import ReconnectingWebSocket from "reconnectingwebsocket";
import SimplePeer from "simple-peer";
import { Howl, Howler } from "howler";
let backgroundAudio;

export default {
  name: "App",
  components: {
    //HelloWorld
  },
  data: function() {
    return {
      mouseX: 0,
      mouseY: 0,
      handPoseModel: null,
      poseNetModel: null,
      recognizedSpeech: "",
      interimRecognizedSpeech: "",
      conversations: [],
      friendlyNames: {
        "dialog-permutationCity-774M-2-300": "Permutation City by Greg Egan",
        "dialog-lankhmar-all-774M-1000":
          "Fafherd and the Grey Mouser by Fritz Lieber",
        "dialog-hitchhikerAll-774M-700":
          "The Hitchhiker's Guide to the Galaxy by Douglas Adams",
        "dialog-marsSeries-774M-600":
          "A Princess of Mars by Edgar Rice Burroughs",
        "dialog-50shades-774M-1200": "50 Shades of Gray by E. L. James"
      }
    };
  },
  methods: {
    startMusic: () => {
      backgroundAudio = new Howl({
        src: ["audio/99632__tomlija__small-cafe-ambience.wav"],
        autoplay: true,
        loop: true,
        volume: 0.5,
        preload: true,
        html5: true,
        onend: function() {
          console.log("Finished!");
        }
      });
    },
    mouseMove(event) {
      // if (backgroundAudio){
      //   console.log(event.clientX,event.clientY)
      this.mouseX = event.clientX;
      this.mouseY = event.clientY;
      // this.mousePosition = [event.clientX, event.clientY];
      //   // backgroundAudio.pos(event.clientX,event.clientY,0);
      //   backgroundAudio.stereo(event.clientX - 750);
      // }
    },
    speak: text => {
      //----------------- TEXT TO VOICE -----------------------
      if ("speechSynthesis" in window) {
        var synthesis = window.speechSynthesis;

        var voice = synthesis.getVoices().filter(function(voice) {
          return voice.lang === "en";
        })[0];

        // Regex to match all English language tags e.g en, en-US, en-GB
        var langRegex = /^en(-[a-z]{2})?$/i;

        // Get the available voices and filter the list to only have English speakers
        var voices = synthesis
          .getVoices()
          .filter(voice => langRegex.test(voice.lang));

        // Log the properties of the voices in the list
        voices.forEach(function(v) {
          console.log({
            name: v.name,
            lang: v.lang,
            uri: v.voiceURI,
            local: v.localService,
            default: v.default
          });
        });

        var utterance = new SpeechSynthesisUtterance(text);

        // Set utterance properties
        utterance.voice = voice;
        utterance.pitch = 1.5;
        utterance.rate = 1.25;
        utterance.volume = 0.8;

        console.log(utterance);

        // Speak the utterance
        synthesis.speak(utterance);
      } else {
        console.log("Text-to-speech not supported.");
      }

      //----------------------------------------
    },
    onSpeechRecognized (event) {
      this.interimRecognizedSpeech = event.results[0][0].transcript
      if (this.interimRecognizedSpeech === "delete" || this.interimRecognizedSpeech === "clear"){
        this.recognizedSpeech = "";
        this.speechToText();
      }else if (this.interimRecognizedSpeech === "submit" || this.interimRecognizedSpeech === "send"){
        // Submit the form and let GPT2 respond
        this.recognizedSpeech = "";
      }
      if (event.results[0].isFinal){
        this.speechToText();
        this.recognizedSpeech = event.results[0][0].transcript
      }
    },
    speechToText: function() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      const recognition = new SpeechRecognition();
      const that = this;
      // recognition.onresult = function(event){
      //   console.log(event);
      //   console.log(event.results[0][0].transcript)
      //   recognizedSpeech = event.results[0][0].transcript
      // }//onSpeechRecognized //console.log;
      recognition.onresult = this.onSpeechRecognized
      recognition.continuous = true;
      recognition.interimResults = true; // false === Only output the recognized speech once fully recognized
      recognition.maxAlternatives = 1;
      // recognition.addEventListener("result", onSpeechRecognized);
      recognition.start();





      
    },
  },
  mounted() {

    var ws = new ReconnectingWebSocket("ws://localhost:3001/conversation");
    ws.timeoutInterval = 2000;
    let that = this;
    ws.onmessage = function(event) {
      // console.log(event.data);
      // <p v-for="message in conversation.messages" :key="message.id">
      //   <b>{{ friendlyNames[message.model] }}</b>
      //   <br />
      //   {{ message.message }}
      //   <br />
      // </p>
      const rawResult = JSON.parse(event.data);

      // console.log(rawResult)
      // const allMessages = rawResult.update[0].messages;
      // let unseenMessages = [];
      // if (this.messagesSeen === null){
      //   this.messagesSeen = {};
      // }else{
      //   allMessages.filter(m => !(m in this.messagesSeen));
      //   allMessages.map(m => this.messagesSeen[m.id] = m);
      // }
      // console.log("New messages", this.unseenMessages)

      
    };

    //   const p = new SimplePeer({
    //       initiator: true,
    //       trickle: false
    //     })

    //     console.log("INITIATOR", p.initiator)

    //     p.on('error', err => console.log('error', err))

    //     p.on('signal', data => {
    //       console.log('SIGNAL', JSON.stringify(data))
    //       document.querySelector('#outgoing').textContent = JSON.stringify(data)
    //     })

    //     document.querySelector('form').addEventListener('submit', ev => {
    //       ev.preventDefault()
    //       p.signal(JSON.parse(document.querySelector('#incoming').value))
    //     })

    //     p.on('connect', () => {
    //       console.log('CONNECT')
    //       p.send('whatever' + Math.random())
    //     })

    //     p.on('data', data => {
    //       console.log('data: ' + data)
    //     })
  }
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
  width: 100%;
  height: 100%;
}
</style>
