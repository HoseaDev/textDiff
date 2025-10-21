import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { useThemeStore } from './stores/theme'

// 导入主题样式
import './assets/styles/theme.scss'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

app.mount('#app')

// 初始化主题
const themeStore = useThemeStore()
themeStore.initTheme()
