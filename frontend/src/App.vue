<template>
  <router-view></router-view>
</template>

<script setup>
import { onMounted } from 'vue';
import { useLoginUserStore } from "@/store/user";

const loginUserStore = useLoginUserStore();

onMounted(async () => {
  // 检查本地存储中是否有token
  if (localStorage.getItem('access_token')) {
    try {
      await loginUserStore.fetchLoginUser();
      console.log("App启动时加载用户信息:", loginUserStore.loginUser);
    } catch (error) {
      console.error("App启动时加载用户信息失败:", error);
    }
  }
});
</script>

<style scoped>
</style>
