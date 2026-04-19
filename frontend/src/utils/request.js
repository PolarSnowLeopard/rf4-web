import axios from "axios";

const request = axios.create({
  baseURL: "http://fdueblab.cn:8888",
  timeout: 10000,
  withCredentials: true,
});

// 获取 JWT token 的函数
const getToken = () => {
  return localStorage.getItem('access_token');
};

// 保存 JWT token 的函数
export const setToken = (token) => {
  if (token) {
    localStorage.setItem('access_token', token);
  }
};

// 清除 JWT token 的函数
export const removeToken = () => {
  localStorage.removeItem('access_token');
};

// 刷新 token 的函数
export const refreshToken = async () => {
  const refresh = localStorage.getItem('refresh_token');
  if (refresh) {
    try {
      const response = await axios.post('/api/user/token_refresh', {
        refresh: refresh
      });
      
      if (response.data.access) {
        setToken(response.data.access);
        return response.data.access;
      }
    } catch (error) {
      console.error('刷新token失败:', error);
      // 刷新失败，清除token，用户需要重新登录
      removeToken();
      localStorage.removeItem('refresh_token');
      window.location.href = '/user/login';
    }
  }
  return null;
};

// Add a request interceptor
request.interceptors.request.use(
  async function (config) {
    // 在请求发送前自动添加 Authorization 头
    const token = getToken();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  function (error) {
    return Promise.reject(error);
  }
);

// Add a response interceptor
request.interceptors.response.use(
  function (response) {
    // 处理成功响应
    console.log(response);
    const { data } = response;
    console.log(data);
    return response;
  },
  async function (error) {
    // 处理错误响应
    const originalRequest = error.config;
    
    // 如果错误是401（未授权），并且没有尝试过刷新token
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // 尝试刷新token
      const newToken = await refreshToken();
      if (newToken) {
        // 更新请求头并重试
        originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
        return axios(originalRequest);
      } else {
        // 如果刷新失败，重定向到登录页面
        if (!window.location.pathname.includes('/user/login')) {
          window.location.href = `/user/login?redirect=${window.location.href}`;
        }
      }
    }
    
    return Promise.reject(error);
  }
);

export default request;
