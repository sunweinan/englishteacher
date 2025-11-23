import { createApp } from 'vue';
import ElementPlus from 'element-plus';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import 'element-plus/dist/index.css';
import 'vant/lib/index.css';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(ElementPlus);
app.use(router);
app.mount('#app');
