import request, { setToken } from "@/utils/request";

// TODO all

const api = {
  userRegister: '/api/user/register',
  userLogin: '/api/user/login',
  userLogout: '/api/user/logout',
  getCurrentUser: '/api/user/info',
  refreshUserToken: '/api/user/token_refresh',
  searchUsers: '/api/user/search',
  deleteUser: '/api/user/delete',
}

/**
 * 用户注册
 * @param params
 */
export const userRegister = async (params) => {
  try {
    const response = await request.request({
      url: api.userRegister,
      method: "POST",
      data: params,
    });
    
    // 注册成功后，保存JWT令牌
    if (response.data.access) {
      setToken(response.data.access);
      // 存储刷新令牌
      localStorage.setItem('refresh_token', response.data.refresh);
    }
    
    return response;
  } catch (error) {
    console.error("注册请求失败:", error);
    throw error;
  }
};

/**
 * 用户登录
 * @param params
 */
export const userLogin = async (params) => {
  try {
    const response = await request.request({
      url: api.userLogin,
      method: "POST",
      data: {
        username: params.username,
        password: params.password
      },
    });
    
    // 保存JWT令牌
    if (response.data.access) {
      setToken(response.data.access);
      // 存储刷新令牌
      localStorage.setItem('refresh_token', response.data.refresh);
    }
    
    return response;
  } catch (error) {
    console.error("登录请求失败:", error);
    throw error;
  }
};

/**
 * 用户注销
 */
export const userLogout = async () => {
  // 清除本地存储的token
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  
  // 不再尝试调用后端接口，因为不存在
  return { success: true };
};

/**
 * 获取当前用户信息
 */
export const getCurrentUser = async () => {
  return request.request({
    url: api.getCurrentUser,
    method: "GET",
    // token已经在请求拦截器中自动添加到请求头
  });
};

/**
 * 刷新Token
 */
export const refreshUserToken = async () => {
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) {
    throw new Error('No refresh token available');
  }
  
  return request.request({
    url: api.refreshUserToken,
    method: "POST",
    data: {
      refresh: refreshToken
    }
  });
};

/**
 * 获取用户列表
 * @param username
 */
export const searchUsers = async (username) => {
  return request.request({
    url: api.searchUsers,
    method: "GET",
    params: {
      username,
    },
  });
};

/**
 * 删除用户
 * @param id
 */
export const deleteUser = async (id) => {
  return request.request({
    url: api.deleteUser,
    method: "POST",
    data: id,
    headers: {
      "Content-Type": "application/json",
    },
  });
};
