import { createRouter, createWebHistory } from 'vue-router'
import BasicLayout from '@/layouts/BasicLayout.vue'
import FishManueList from '@/views/FishManueList.vue'
import FishDetailView from '@/views/FishDetailView.vue'

const routes = [
  {
    path: '/',
    component: BasicLayout,
    children: [
      {
        path: '',
        name: 'home',
        component: () => import('@/views/Home.vue')
      },
      {
        path: '/manue/fish',
        name: 'manueFish',
        component: FishManueList
      },
      {
        path: '/manue/fish/:name',
        name: 'manueFishDetail',
        component: FishDetailView,
        props: true
      },
      {
        path: '/manue/bait',
        name: 'manueBait',
        component: () => import('@/views/BaitList.vue')
      },
      {
        path: '/manue/bait/:id',
        name: 'manueBaitDetail',
        component: () => import('@/views/BaitDetailView.vue'),
        props: true
      },
      {
        path: '/manue/lure',
        name: 'manueLure',
        component: () => import('@/views/LureList.vue')
      },
      {
        path: '/manue/lure/:id',
        name: 'manueLureDetail',
        component: () => import('@/views/LureDetailView.vue'),
        props: true
      },
      {
        path: '/manue/rod',
        name: 'manueRod',
        component: () => import('@/views/RodList.vue')
      },
      {
        path: '/manue/rod/:id',
        name: 'manueRodDetail',
        component: () => import('@/views/RodDetailView.vue'),
        props: true
      },
      {
        path: '/manue/reel',
        name: 'manueReel',
        component: () => import('@/views/ReelList.vue')
      },
      {
        path: '/manue/reel/:id',
        name: 'manueReelDetail',
        component: () => import('@/views/ReelDetailView.vue'),
        props: true
      },
      {
        path: '/manue/line',
        name: 'manueLine',
        component: () => import('@/views/LineList.vue')
      },
      {
        path: '/manue/line/:id',
        name: 'manueLineDetail',
        component: () => import('@/views/LineDetailView.vue'),
        props: true
      },
      {
        path: '/manue/hook',
        name: 'manueHook',
        component: () => import('@/views/HookList.vue')
      },
      {
        path: '/manue/hook/:id',
        name: 'manueHookDetail',
        component: () => import('@/views/HookDetailView.vue'),
        props: true
      },
      {
        path: '/manue/rig',
        name: 'manueRig',
        component: () => import('@/views/RigList.vue')
      },
      {
        path: '/manue/rig/:id',
        name: 'manueRigDetail',
        component: () => import('@/views/RigDetailView.vue'),
        props: true
      },
      {
        path: '/manue/groundbait',
        name: 'manueGroundbait',
        component: () => import('@/views/GroundbaitList.vue')
      },
      {
        path: '/manue/groundbait/:id',
        name: 'manueGroundbaitDetail',
        component: () => import('@/views/GroundbaitDetailView.vue'),
        props: true
      },
      {
        path: '/manue/food',
        name: 'manueFood',
        component: () => import('@/views/FoodList.vue')
      },
      {
        path: '/manue/food/:id',
        name: 'manueFoodDetail',
        component: () => import('@/views/FoodDetailView.vue'),
        props: true
      },
      {
        path: '/manue/accessory',
        name: 'manueAccessory',
        component: () => import('@/views/AccessoryList.vue')
      },
      {
        path: '/manue/accessory/:id',
        name: 'manueAccessoryDetail',
        component: () => import('@/views/AccessoryDetailView.vue'),
        props: true
      },
      {
        path: '/user/login',
        name: 'userLogin',
        component: () => import('@/views/user/UserLogin.vue')
      },
      {
        path: '/agent',
        name: 'agent',
        component: () => import('@/views/Agent.vue')
      },
      {
        path: '/catch/from-image',
        name: 'catchFromImage',
        component: () => import('@/views/CatchFromImage.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 