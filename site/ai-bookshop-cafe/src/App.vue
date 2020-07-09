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
          <img :src="require(`./assets/${participant.cover}`)" />
        </portal>
      </div>
    </div>
    <div id="conversations">
      <div
        class="conversation"
        v-for="conversation in conversations"
        :key="conversation.id"
      >
        <div
          class="conversationMessages"
          v-chat-scroll="{ always: false, smooth: true, notSmoothOnInit: true }"
        >
          <div class="conversationCovers">
            <portal-target
              v-for="participant in conversation.participants"
              :key="participant"
              :name="'participant-' + participant"
              class="cover"
            />
          </div>
          <div
            class="message"
            v-for="message in conversation.messages"
            :key="message.id"
          >
            <b
              >{{ participants.find(x => x.id === message.model).title }} by
              {{ participants.find(x => x.id === message.model).author }}</b
            ><br />
            {{ message.message }}<br />
          </div>
        </div>
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
      participants: []
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
  /*position: relative;*/
  position: absolute;
}

.conversation:nth-child(1) .cover:nth-child(1) {
  left: -8em;
}

.conversation:nth-child(1) .cover:nth-child(2) {
  left: -10em;
  top: 15em;
}

.conversation:nth-child(1) .cover:nth-child(3) {
  bottom: -16em;
}

.conversation:nth-child(1) .cover:nth-child(4) {
  right: -12em;
  top: -2em;
}

.conversation:nth-child(1) .cover:nth-child(5) {
  right: -14em;
  top: 22em;
}

.conversation:nth-child(2) .cover:nth-child(1) {
  top: -10em;
}

.conversation:nth-child(2) .cover:nth-child(2) {
  left: -10em;
  top: 15em;
}

.conversation:nth-child(2) .cover:nth-child(3) {
  left: -8em;
}

.conversation:nth-child(2) .cover:nth-child(4) {
  right: -14em;
  top: 22em;
}

.conversation:nth-child(2) .cover:nth-child(5) {
  right: -12em;
  top: -2em;
}

.cover img {
  transition: transform linear 2s;
  width: 6em;
}

.conversation {
  /*font-size: 15px;*/
  font-family: serif;
  position: absolute;
  width: 30em;
  height: 20em;
}

.conversationMessages {
  width: 100%;
  height: 100%;
  padding: 1em;
  overflow-y: auto;
  scroll-snap-type: y mandatory;
  display: flex;
  flex-direction: column;
  border: 0.5em solid black;
  scrollbar-color: black white;
}

.message {
  font-size: 1.2em;
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
  left: max(15%, 10em);
  top: max(10%, 10em);
}

.conversation:nth-child(2) {
  right: max(3em, min(10%, 15em));
  bottom: max(3em, 10%, 15em);
}

.message {
  margin: 0;
  margin-bottom: 1em;
}

.message:last-child {
  padding-bottom: 2em;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: black;
}
</style>
