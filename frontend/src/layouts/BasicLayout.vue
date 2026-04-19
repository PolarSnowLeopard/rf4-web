<template>
    <div id="BasicLayout">
        <a-layout>
            <a-layout-header class="header">
                <GlobalHeader />
            </a-layout-header>
            <a-layout-content class="content">
                <router-view />
            </a-layout-content>
            <a-layout-footer class="footer">
                <a href="https://github.com/PolarSnowLeopard" target="_blank">
                    俄钓4助手 by 瀚海雪豹
                </a>
            </a-layout-footer>
        </a-layout>
    </div>
</template>

<script setup>
import GlobalHeader from '@/components/GlobalHeader.vue';
</script>

<style scoped>
#BasicLayout {
    height: 100vh;
    width: 100vw;
}

#BasicLayout .header {
    padding-inline: 20px;
    margin-bottom: 16px;
    color: unset;
    background: white;
}

#BasicLayout .content {
    padding: 16px;
    min-height: calc(100vh - 150px);
    margin-bottom: 70px;
    overflow-y: auto;
    background-color: #fefefe;
}

#BasicLayout .footer {
    background-color: #fefefe;
    text-align: center;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 16px;
    height: 60px;
}
</style>
