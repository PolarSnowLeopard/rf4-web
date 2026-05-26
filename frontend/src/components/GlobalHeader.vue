<template>
    <div id="global-header">
        <a-row :wrap="false">
            <a-col flex="200px">
                <div class="title-bar">
                    <img class="logo" src="../assets/fisherman.svg" alt="logo" />
                    <div class="title">俄钓4 钓鱼助手</div>
                </div>
            </a-col>
            <a-col flex="auto">
                <a-menu v-model:selectedKeys="current" mode="horizontal" :items="items" @click="doMenuClick" />
            </a-col>
            <a-col flex="150px">
                <!-- 用户登录状态 -->
                <div class="user-login-status">
                    <template v-if="loginUserStore.loginUser && loginUserStore.loginUser.id">
                        <div class="user-info">
                            <span class="username">{{ loginUserStore.loginUser.username }}</span>
                            <a-button type="link" size="small" @click="handleLogout">注销</a-button>
                        </div>
                    </template>
                    <template v-else>
                        <a-button type="primary" @click="goToLogin">登录</a-button>
                    </template>
                </div>
            </a-col>
        </a-row>
    </div>
</template>

<script setup>
import { h, ref, onMounted, computed } from 'vue';
import { HomeOutlined, BookOutlined, ExperimentOutlined, CameraOutlined } from '@ant-design/icons-vue';
import { useRoute, useRouter } from 'vue-router';
import { useLoginUserStore } from '@/store/user';
import { userLogout } from '@/api/user';
import { message } from 'ant-design-vue';

const router = useRouter();
const route = useRoute();
const current = ref(['home']);
const loginUserStore = useLoginUserStore();

// 动态生成菜单项，根据登录状态决定是否显示登录菜单项
const items = computed(() => {
    const baseItems = [
        {
            key: '/',
            icon: () => h(HomeOutlined),
            label: '主页',
            title: '主页',
        },
        {
            key: '/manue/fish',
            icon: () => h(BookOutlined),
            label: '图鉴',
            title: '图鉴',
            children: [
                {
                    key: '/manue/fish',
                    label: '鱼类图鉴',
                },
                {
                    key: '/manue/bait',
                    label: '鱼饵图鉴',
                },
                {
                    key: '/manue/lure',
                    label: '拟饵图鉴',
                },
                {
                    key: '/manue/rod',
                    label: '渔竿图鉴',
                },
                {
                    key: '/manue/reel',
                    label: '渔轮图鉴',
                },
                {
                    key: '/manue/line',
                    label: '鱼线图鉴',
                },
                {
                    key: '/manue/hook',
                    label: '钓钩图鉴',
                },
            ],
        },
        {
            key: '/catch/from-image',
            icon: () => h(CameraOutlined),
            label: '渔获识别',
            title: '渔获识别',
        },
        {
            key: '/agent',
            icon: () => h(ExperimentOutlined),
            label: '智能体',
            title: '智能体',
        }
    ];
    
    // 如果用户未登录，添加登录菜单项
    if (!loginUserStore.loginUser || !loginUserStore.loginUser.id) {
        baseItems.push({
            key: '/user/login',
            label: '登录',
            title: '登录',
        });
    }
    
    return baseItems;
});

// 路由跳转事件
const doMenuClick = ({ key }) => {
    router.push(key);
};

// 跳转到登录页
const goToLogin = () => {
    router.push('/user/login');
};

// 处理注销
const handleLogout = () => {
    // 清除本地存储的token
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    
    // 重置用户状态
    loginUserStore.clearUser();
    
    message.success('注销成功');
    
    // 重定向到首页
    router.push('/');
};

// 组件挂载时，根据当前路由初始化选中状态
onMounted(() => {
    initSelectedMenu();
    // 获取用户信息（如果token存在但没有用户信息）
    if (!loginUserStore.loginUser || !loginUserStore.loginUser.id) {
        loginUserStore.fetchLoginUser();
    }
});

// 初始化选中菜单
const initSelectedMenu = () => {
    const currentPath = route.path;
    current.value = [currentPath];
};

// 监听路由变化，更新菜单选中状态
router.afterEach((to, from) => {
    current.value = [to.path];
});
</script>

<style scoped>
.title-bar {
    display: flex;
    align-items: center;
}

.title {
    color: black;
    font-size: 18px;
    margin-left: 16px;
}

.logo {
    height: 48px;
}

.user-login-status {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    height: 100%;
    padding-right: 16px;
}

.user-info {
    display: flex;
    align-items: center;
}

.username {
    margin-right: 8px;
    font-weight: 500;
}
</style>
