import Vue from "vue";
import App from "./App.vue";
import PortalVue from "portal-vue";
import VueChatScroll from "vue-chat-scroll";

Vue.config.productionTip = false;
Vue.use(PortalVue);
Vue.use(VueChatScroll);

new Vue({
  render: h => h(App)
}).$mount("#app");
