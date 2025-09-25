import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import { useMainStore } from './store'
import { themeManager } from './store/theme/themeManager'



const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(ElementPlus)



// 初始化主题（白天/黑夜）
themeManager.initTheme();

router.isReady().then(()=>{
    const store = useMainStore();
    if(store.user){
        store.initWebSocket();
    }
}) 



app.mount('#app')