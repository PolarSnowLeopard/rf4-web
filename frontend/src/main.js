// import { createApp } from 'vue'
// import './style.css'
// import App from './App.vue'

// createApp(App).mount('#app')

import { createApp } from 'vue';
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue';
import App from './App.vue';
import 'ant-design-vue/dist/reset.css';
import router from './router';
import './style.css';

const app = createApp(App);
const pinia = createPinia();

app.use(Antd);
app.use(router);
app.use(pinia);
app.mount('#app');