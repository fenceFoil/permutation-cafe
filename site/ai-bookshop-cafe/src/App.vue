<template>
  <div id="app">
    <img alt="Vue logo" src="./assets/logo.png" />
    <p v-for="message in messages" :key="message.id">
      Message {{ message.id }}: {{ message.message }}
    </p>
    <HelloWorld msg="Welcome to Your Vue.js App" />
  </div>
</template>

<script>
import HelloWorld from "./components/HelloWorld.vue";
import ReconnectingWebSocket from "reconnectingwebsocket";

export default {
  name: "App",
  components: {
    HelloWorld
  },
  data: function() {
    return {
      messages: []
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
