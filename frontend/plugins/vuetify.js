import Vue from 'vue'
import VueMasonry from 'vue-masonry-css'
import '@fortawesome/fontawesome-free/css/all.css' // Ensure you are using css-loader
import Vuetify from 'vuetify/lib'
import colors from 'vuetify/lib/util/colors'
import minifyTheme from 'minify-css-string'

Vue.use(Vuetify)
Vue.use(VueMasonry)

export default new Vuetify({
  icons: {
    iconfont: 'fa',
  },
  theme: {
    themes: {
      options: { minifyTheme },
    },
  },
})

