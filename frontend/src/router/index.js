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