<template>
    <div class="login-container">
        <div class="login-card">
            <h1 class="login-title">用户登录</h1>
            
            <div class="login-logo">
                <img src="@/assets/fisherman.svg" alt="logo" />
            </div>
            
            <a-form 
                :model="form" 
                @finish="handleSubmit"
                layout="vertical"
                class="login-form"
            >
                <a-form-item name="userAccount" label="账号" :rules="[{ required: true, message: '请输入账号' }]">
                    <a-input 
                        v-model:value="form.userAccount" 
                        placeholder="请输入账号"
                        size="large"
                    >
                        <template #prefix>
                            <UserOutlined />
                        </template>
                    </a-input>
                </a-form-item>
                
                <a-form-item name="userPassword" label="密码" :rules="[
                    { required: true, message: '请输入密码' },
                    { min: 8, message: '密码不少于 8 位' },
                ]">
                    <a-input-password 
                        v-model:value="form.userPassword" 
                        placeholder="请输入密码"
                        size="large"
                    >
                        <template #prefix>
                            <LockOutlined />
                        </template>
                    </a-input-password>
                </a-form-item>
                
                <a-form-item>
                    <a-button 
                        type="primary" 
                        html-type="submit" 
                        size="large"
                        block
                        :loading="loading"
                    >
                        登录
                    </a-button>
                </a-form-item>
                
                <div class="login-links">
                    <a>忘记密码?</a>
                    <a>注册账号</a>
                </div>
            </a-form>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useLoginUserStore } from '@/store/user';
import { userLogin } from '@/api/user';
import { message } from 'ant-design-vue';
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue';

const router = useRouter();
const loginUserStore = useLoginUserStore();
const loading = ref(false);

// 表单字段名称
const form = ref({
    userAccount: '',
    userPassword: '',
});

/**
 * 提交表单
 */
const handleSubmit = async () => {
    loading.value = true;
    
    const params = {
        username: form.value.userAccount,
        password: form.value.userPassword
    };

    try {
        // 调用登录接口 - token的存取已经在user.js中封装
        const res = await userLogin(params);
        
        // 登录成功
        if (res.data.access && res.data.refresh) {
            console.log("登录成功，令牌已保存");
            
            // 登录成功后额外请求用户信息
            try {
                console.log("开始获取用户信息");
                await loginUserStore.fetchLoginUser();
                console.log("用户信息获取成功", loginUserStore.loginUser);
                
                message.success("登录成功");
                router.push({
                    path: "/",
                    replace: true,
                });
            } catch (infoError) {
                console.error("获取用户信息失败:", infoError);
                message.warning("登录成功，但获取用户信息失败");
                router.push({
                    path: "/",
                    replace: true,
                });
            }
        } 
        // 兼容旧的返回格式
        else if (res.data.code === 0 && res.data.data) {
            await loginUserStore.fetchLoginUser();
            message.success("登录成功");
            router.push({
                path: "/",
                replace: true,
            });
        } else {
            // 登录失败但有返回消息
            message.error("登录失败：" + (res.data.detail || ""));
        }
    } catch (error) {
        console.error("登录请求失败:", error);
        // 显示错误消息，优先使用后端返回的错误信息
        const errorMsg = error.response?.data?.detail || 
                         error.response?.data?.message || 
                         "登录失败，请检查账号密码";
        message.error(errorMsg);
    } finally {
        loading.value = false;
    }
};
</script>

<style scoped>
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 85vh;
    background-color: #f0f2f5;
    background-image: url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiPjxkZWZzPjxwYXR0ZXJuIGlkPSJwYXR0ZXJuXzAiIHBhdHRlcm5Vbml0cz0idXNlclNwYWNlT25Vc2UiIHdpZHRoPSIxMCIgaGVpZ2h0PSIxMCIgcGF0dGVyblRyYW5zZm9ybT0icm90YXRlKDQ1KSI+PHJlY3QgeD0iMCIgeT0iMCIgd2lkdGg9IjYiIGhlaWdodD0iNiIgZmlsbD0iI2VlZWVlZSI+PC9yZWN0PjwvcGF0dGVybj48L2RlZnM+PHJlY3QgeD0iMCIgeT0iMCIgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNwYXR0ZXJuXzApIj48L3JlY3Q+PC9zdmc+');
}

.login-card {
    width: 360px;
    padding: 40px 30px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    animation: fadeIn 0.5s ease-out;
}

.login-title {
    text-align: center;
    color: #1890ff;
    margin-bottom: 30px;
    font-size: 24px;
    font-weight: 600;
}

.login-logo {
    text-align: center;
    margin-bottom: 24px;
}

.login-logo img {
    width: 64px;
    height: 64px;
}

.login-form {
    margin-top: 20px;
}

.login-links {
    display: flex;
    justify-content: space-between;
    margin-top: 12px;
    font-size: 14px;
}

.login-links a {
    color: #1890ff;
    transition: color 0.3s;
}

.login-links a:hover {
    color: #40a9ff;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* 响应式调整 */
@media (max-width: 576px) {
    .login-card {
        width: 90%;
        padding: 30px 20px;
    }
}
</style>