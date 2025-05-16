// API配置
const API_CONFIG = {
  BASE_URL: 'http://localhost:5000',
  TIMEOUT: 10000,
  HEADERS: {
    'Content-Type': 'application/json'
  }
};

// 页面加载检查用户是否已登录
document.addEventListener('DOMContentLoaded', function() {
  // 检查用户是否已登录，未登录则重定向到登录页面
  if (localStorage.getItem('isLoggedIn') !== 'true' && sessionStorage.getItem('isLoggedIn') !== 'true') {
    window.location.href = '../login.html';
  }
  
  // 初始化修改密码模态框
  initPasswordModal();
  
  // 初始化移动端菜单切换
  initMobileMenu();
});

// 退出登录功能
function logout() {
  // 清除所有登录状态
  localStorage.removeItem('isLoggedIn');
  sessionStorage.removeItem('isLoggedIn');
  // 重定向到登录页面
  window.location.href = '../login.html';
}

// 初始化修改密码模态框
function initPasswordModal() {
  const modal = document.getElementById('passwordModal');
  const openModalBtn = document.getElementById('changePasswordBtn');
  const closeBtn = document.querySelector('.close');
  const cancelBtn = document.querySelector('.cancel-btn');
  const form = document.getElementById('changePasswordForm');
  const currentPasswordInput = document.getElementById('currentPassword');
  const newPasswordInput = document.getElementById('newPassword');
  const confirmPasswordInput = document.getElementById('confirmPassword');
  const errorMessage = document.getElementById('passwordError');
  
  if (!modal || !openModalBtn) return;
  
  // 打开模态框
  openModalBtn.addEventListener('click', function() {
    modal.classList.add('show');
    // 清空表单
    form.reset();
    errorMessage.textContent = '';
  });
  
  // 关闭模态框的多种方式
  function closeModal() {
    modal.classList.remove('show');
  }
  
  closeBtn.addEventListener('click', closeModal);
  cancelBtn.addEventListener('click', closeModal);
  
  // 点击模态框外部关闭
  window.addEventListener('click', function(event) {
    if (event.target === modal) {
      closeModal();
    }
  });
  
  // 提交修改密码表单
  form.addEventListener('submit', function(event) {
    event.preventDefault();
    
    const currentPassword = currentPasswordInput.value;
    const newPassword = newPasswordInput.value;
    const confirmPassword = confirmPasswordInput.value;
    
    // 验证当前密码
    const savedPassword = localStorage.getItem('userPassword') || 'admin';
    if (currentPassword !== savedPassword) {
      errorMessage.textContent = '当前密码不正确！';
      return;
    }
    
    // 验证新密码长度
    if (newPassword.length < 6) {
      errorMessage.textContent = '新密码长度至少为6个字符！';
      return;
    }
    
    // 验证两次密码输入是否一致
    if (newPassword !== confirmPassword) {
      errorMessage.textContent = '两次输入的密码不一致！';
      return;
    }
    
    // 保存新密码
    if (localStorage.getItem('isLoggedIn') === 'true') {
      localStorage.setItem('userPassword', newPassword);
    } else {
      sessionStorage.setItem('userPassword', newPassword);
    }
    
    // 显示成功消息并关闭模态框
    alert('密码修改成功！下次登录请使用新密码。');
    closeModal();
  });
}

// 初始化移动端菜单切换
function initMobileMenu() {
  const menuToggle = document.querySelector('.header-menu-toggle');
  if (!menuToggle) return;
  
  menuToggle.addEventListener('click', function() {
    document.querySelector('.sidebar').classList.toggle('active');
    document.querySelector('.main-content').classList.toggle('sidebar-active');
  });
}

// HTTP请求工具
const http = {
  // GET请求
  async get(url, params = {}) {
    try {
      // 构建查询参数
      const queryParams = Object.keys(params)
        .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
        .join('&');
      
      const fullUrl = `${API_CONFIG.BASE_URL}${url}${queryParams ? '?' + queryParams : ''}`;
      
      const response = await fetch(fullUrl, {
        method: 'GET',
        headers: API_CONFIG.HEADERS,
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('GET请求错误:', error);
      // 返回模拟数据用于开发测试
      return getMockData(url);
    }
  },
  
  // POST请求
  async post(url, data = {}) {
    try {
      const response = await fetch(`${API_CONFIG.BASE_URL}${url}`, {
        method: 'POST',
        headers: API_CONFIG.HEADERS,
        body: JSON.stringify(data),
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('POST请求错误:', error);
      // 返回模拟数据用于开发测试
      return { success: true, message: '模拟请求成功' };
    }
  }
};

// 创建时间范围选项切换功能
function initTimeFilter(callback) {
  const timeOptions = document.querySelectorAll('.filter-option');
  
  timeOptions.forEach(option => {
    option.addEventListener('click', function() {
      // 移除所有active类
      timeOptions.forEach(opt => opt.classList.remove('active'));
      // 添加当前选中active类
      this.classList.add('active');
      
      // 调用回调函数并传递时间范围值
      if (typeof callback === 'function') {
        callback(this.getAttribute('data-value'));
      }
    });
  });
}

// 根据不同API路径返回模拟数据
function getMockData(url) {
  console.log('使用模拟数据:', url);
  
  // 默认返回空对象
  return {};
} 