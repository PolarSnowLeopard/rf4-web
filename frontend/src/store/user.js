import { defineStore } from "pinia";
import { ref } from "vue";
import { getCurrentUser } from "@/api/user";

export const useLoginUserStore = defineStore("loginUser", () => {
    const loginUser = ref({
        username: "未登录",
    });

    async function fetchLoginUser() {
        try {
            const res = await getCurrentUser();
            console.log("获取用户信息响应:", res.data);
            
            // 根据实际响应，直接使用返回的用户对象
            if (res.data && res.data.id) {
                // 后端直接返回了用户对象
                loginUser.value = res.data;
                console.log("用户状态已更新:", loginUser.value);
            } else if (res.data.code === 200 && res.data.data) {
                // 保留旧格式的兼容处理
                loginUser.value = res.data.data;
            } else {
                console.error("无法识别的用户信息格式:", res.data);
            }
        } catch (error) {
            console.error("获取用户信息失败:", error);
        }
    }

    function setLoginUser(newLoginUser) {
        loginUser.value = newLoginUser;
        console.log("手动设置用户状态:", loginUser.value);
    }

    // 新增：清除用户信息的方法
    function clearUser() {
        loginUser.value = {
            username: "未登录"
        };
    }

    return { loginUser, setLoginUser, fetchLoginUser, clearUser };
});
