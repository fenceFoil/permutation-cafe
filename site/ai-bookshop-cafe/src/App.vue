<template>
  <div id="app">
    <img alt="Vue logo" src="./assets/logo.png" />
    <p v-for="message in messages" :key="message.id">
      <b>{{ friendlyNames[message.model] }}</b><br> {{ message.message }}<br>
    </p>
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
      messages: [],
      friendlyNames: {
        "dialog-permutationCity-774M-2-300": "Permutation City by Greg Egan",
        "dialog-lankhmar-all-774M-1000":
          "Fafherd and the Grey Mouser by Fritz Lieber"
      }
    };
  },
  mounted() {
    var ws = new ReconnectingWebSocket("ws://localhost:5678/");
    ws.timeoutInterval = 2000;
    let that = this;
    ws.onmessage = function(event) {
      console.log(event.data);
      that.messages = JSON.parse(event.data);
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
