<template>
  <div id="app">
    <div id="sign">
      Permutation Cafe
    </div>
    <div id="covers">
      <div
        v-for="participant in participants"
        :key="participant.id"
        class="coverWrapper"
      >
        <portal :to="'participant-' + participant.id">
          <div class="cover">
            <img :src="require(`./assets/${participant.cover}`)" />
          </div>
        </portal>
      </div>
    </div>
    <div id="conversations">
      <div
        class="conversation"
        v-for="conversation in conversations"
        :key="conversation.id"
      >
        <div class="conversationMessages">
          <div
            class="message"
            v-for="message in conversation.messages"
            :key="message.id"
          >
            <b>{{ friendlyNames[message.model] }}</b
            ><br />
            {{ message.message }}<br />
          </div>
        </div>
        <portal-target
          v-for="participant in conversation.participants"
          :key="participant"
          :name="'participant-' + participant"
        />
      </div>
    </div>
    <!--<HelloWorld msg="Welcome to Your Vue.js App" />-->
  </div>
</template>

<script>
//import HelloWorld from "./components/HelloWorld.vue";
import ReconnectingWebSocket from "reconnectingwebsocket";

export default {
  name: "App",
  components: {
    //HelloWorld
  },
  data: function() {
    return {
      conversations: [],
      participants: [],
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
  mounted() {
    var ws = new ReconnectingWebSocket("ws://localhost:5678/");
    ws.timeoutInterval = 2000;
    let that = this;
    ws.onmessage = function(event) {
      console.log(event.data);
      let packet = JSON.parse(event.data);
      if ("update" in packet) {
        that.conversations = packet.update;
      }
      if ("participantsMetadata" in packet) {
        that.participants = packet.participantsMetadata;
      }
    };
  } /*,
  methods: function() {
    return {
      findConversationOf(participantID) {
        this.conversations
      }
    }
  }*/
};
</script>

<style>
@import url("https://fonts.googleapis.com/css2?family=Courier+Prime:ital@1&display=swap");

#sign {
  font-family: "Courier Prime", monospace;
  font-size: 3rem;

  color: #00000044;

  position: absolute;
  margin-left: 4rem;
  margin-top: 0.6rem;
}

.coverWrapper {
}

.cover {
  transition: transform linear 2s;
}

.cover img {
  position: absolute;
  width: 6em;
}

.conversation {
  font-size: 12px;
  font-family: serif;
  position: absolute;
}

.conversationMessages {
  width: 30em;
  height: 20em;
  padding: 1em;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  border: 0.5em solid black;
  scrollbar-color: black white;
}

.message {
  margin: 1em;
}

.conversationMessages > :first-child {
  margin-top: auto !important;
}

/*.conversation::after {
  content: ".";
  color: transparent;
  position: absolute;
  top: 0;
  margin:0.5em;
  left: 0;
  width: 100%;
  height: 20%;
  background-image: linear-gradient(
    to top,
    rgba(255, 255, 255, 0),
    rgba(255, 255, 255, 1)
  );
}*/

.conversation:nth-child(1) {
  left: 15%;
  top: 10%;
}

.conversation:nth-child(2) {
  right: 10%;
  bottom: 10%;
}

.message {
  margin: 0;
  margin-bottom: 1em;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: black;
}
</style>
