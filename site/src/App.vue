<template>
  <div id="app">
    <p>HELLO ALL</p>
    <img alt="Vue logo" src="./assets/logo.png" />
    <div v-for="conversation in conversations" :key="conversation.id" style="border:2px solid black;">
      <p v-for="message in conversation.messages" :key="message.id">
        <b>{{ friendlyNames[message.model] }}</b><br />
        {{ message.message }}<br />
      </p>
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
      friendlyNames: {
        "dialog-permutationCity-774M-2-300": "Permutation City by Greg Egan",
        "dialog-lankhmar-all-774M-1000":
          "Fafherd and the Grey Mouser by Fritz Lieber",
        "dialog-hitchhikerAll-774M-700":
          "The Hitchhiker's Guide to the Galaxy by Douglas Adams",
        "dialog-marsSeries-774M-600":
          "A Princess of Mars by Edgar Rice Burroughs",
        "dialog-50shades-774M-1200":
          "50 Shades of Gray by E. L. James"
      }
    };
  },
  mounted() {
    var ws = new ReconnectingWebSocket("ws://localhost:5678/");
    ws.timeoutInterval = 2000;
    let that = this;
    ws.onmessage = function(event) {
      console.log(event.data);
      that.conversations = JSON.parse(event.data);
    };
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
}
</style>
