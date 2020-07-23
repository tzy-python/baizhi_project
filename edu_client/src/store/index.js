import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
    state: {
        //购物车数据
        cart_length: ''
    },
    mutations: {
        // 检测购物车提交的动作
        add_cart(state,data){
            state.cart_length = data
        }
    }
})
