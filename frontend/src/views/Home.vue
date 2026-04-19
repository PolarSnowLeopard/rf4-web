<template>
  <div class="home-container">
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="title">俄罗斯钓鱼4助手</h1>
        <p class="subtitle">游戏数据查询与攻略工具</p>
        
        <a-button type="primary" size="large" @click="goToFishManue">
          进入鱼类图鉴
        </a-button>
      </div>
      
      <div class="content-section">
        <div class="info-grid">
          <div class="info-block tool-intro">
            <h2>关于本工具</h2>
            <p>
              本工具为《俄罗斯钓鱼4》玩家提供实用数据查询功能。目前包含完整鱼类图鉴，
              提供游戏中所有鱼种的详细数据，包括稀有重量、超稀有重量和其他关键信息。
              工具界面简洁直观，数据持续更新，帮助玩家快速查询所需信息，提升游戏体验。
            </p>
          </div>
          
          <div class="info-block development-plan">
            <h2>开发计划</h2>
            <div class="plans">
              <div class="plan-item">
                <div class="plan-icon">📍</div>
                <div class="plan-text">
                  <h3>钓点位置查询</h3>
                  <p>热门钓点位置</p>
                </div>
              </div>
              
              <div class="plan-item">
                <div class="plan-icon">🎣</div>
                <div class="plan-text">
                  <h3>装备配置指南</h3>
                  <p>装备推荐</p>
                </div>
              </div>
              
              <div class="plan-item">
                <div class="plan-icon">🥫</div>
                <div class="plan-text">
                  <h3>窝料配方技巧</h3>
                  <p>窝料配方</p>
                </div>
              </div>
              
              <div class="plan-item">
                <div class="plan-icon">📊</div>
                <div class="plan-text">
                  <h3>数据统计分析</h3>
                  <p>数据分析</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const goToFishManue = () => {
  router.push('/manue/fish');
};
</script>

<style scoped>
.home-container {
  min-height: 85vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 30px;
  background-color: #f5f8fa;
}

.hero-section {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.hero-content {
  text-align: center;
  margin-bottom: 30px;
}

.title {
  font-size: 2.5rem;
  margin-bottom: 12px;
  color: #245f7b;
}

.subtitle {
  font-size: 1.2rem;
  margin-bottom: 25px;
  color: #5a6c7d;
}

.content-section {
  background-color: #fff;
  padding: 35px;
  border-radius: 8px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 30px;
}

.info-block h2 {
  color: #245f7b;
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 1.5rem;
  padding-bottom: 10px;
  border-bottom: 1px solid #eef2f6;
}

.info-block p {
  line-height: 1.6;
  color: #444;
  font-size: 1rem;
}

.tool-intro p {
  max-width: 100%;
}

.plans {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
}

.plan-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  background-color: #f9fbfd;
  padding: 20px 15px;
  border-radius: 8px;
  border-top: 3px solid #48b0f7;
}

.plan-icon {
  font-size: 2rem;
  margin-bottom: 12px;
  color: #48b0f7;
}

.plan-text h3 {
  font-size: 1rem;
  margin: 0 0 8px 0;
  color: #245f7b;
}

.plan-text p {
  margin: 0;
  font-size: 0.85rem;
  color: #5a6c7d;
}

/* 平板设备 */
@media (max-width: 900px) {
  .plans {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 手机设备 */
@media (max-width: 600px) {
  .home-container {
    padding: 20px;
  }
  
  .title {
    font-size: 2rem;
  }
  
  .subtitle {
    font-size: 1.1rem;
  }
  
  .content-section {
    padding: 25px 20px;
  }
  
  .plans {
    grid-template-columns: 1fr;
  }
}
</style>
