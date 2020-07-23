import Vue from 'vue'
import Router from 'vue-router'
import Home from "../components/Home";
import Login from "../components/Login";
import Register from "../components/Register";
import Course from "../components/Course";
import CourseDetails from "../components/CourseDetails";
import Cart from "../components/Cart";
import Order from "../components/Order";
import OrderSuccess from "../components/OrderSuccess";


Vue.use(Router)

export default new Router({
    mode:"history",
    routes: [
        {
            path: '/',
            name:"home",
            component:Home
        },
        {
            path: '/home',
            name:"home",
            component:Home
        },
        {
            path: '/home/login',
            name:"login",
            component:Login
        },
        {
            path: '/user/register',
            name:"register",
            component:Register
        },
        {
            path: '/python',
            name:"Course",
            component:Course
        },
        {
            path: '/detail/:id',
            name:"detail",
            component:CourseDetails
        },
        {
            path: '/cart',
            name:"cart",
            component:Cart
        },
        {
            path: '/order',
            name:"order",
            component:Order
        },
        {
            path: '/payments/result',
            name:"ordersuccess",
            component:OrderSuccess
        },
    ]
})
