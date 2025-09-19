import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { useMainStore } from './store'



const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(ElementPlus)


router.isReady().then(()=>{
    const store = useMainStore();
    if(store.user){
        store.initWebSocket();
    }
}) 



app.mount('#app')