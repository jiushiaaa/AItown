// 公共函数

// 初始化时间筛选器
function initTimeFilter(callback) {
  const filterOptions = document.querySelectorAll('.filter-option');
  
  filterOptions.forEach(option => {
    option.addEventListener('click', function() {
      // 移除其他选项的激活状态
      filterOptions.forEach(opt => opt.classList.remove('active'));
      
      // 激活当前选项
      this.classList.add('active');
      
      // 获取选择的时间范围
      const timeRange = this.getAttribute('data-value');
      
      // 执行回调
      if (typeof callback === 'function') {
        callback(timeRange);
      }
    });
  });
}

// HTTP请求工具
const http = {
  // GET请求
  get: async function(url, params = {}) {
    try {
      // 构建URL参数
      const queryString = Object.keys(params)
        .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
        .join('&');
      
      const fullUrl = queryString ? `${url}?${queryString}` : url;
      
      // 发送请求
      const response = await fetch(fullUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      // 检查响应状态
      if (!response.ok) {
        throw new Error(`HTTP错误: ${response.status}`);
      }
      
      // 解析响应
      const data = await response.json();
      return { data };
    } catch (error) {
      console.error('GET请求失败:', error);
      throw error;
    }
  },
  
  // POST请求
  post: async function(url, data = {}) {
    try {
      // 发送请求
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(data)
      });
      
      // 检查响应状态
      if (!response.ok) {
        throw new Error(`HTTP错误: ${response.status}`);
      }
      
      // 解析响应
      const responseData = await response.json();
      return { data: responseData };
    } catch (error) {
      console.error('POST请求失败:', error);
      throw error;
    }
  }
};

// 登出函数
function logout() {
  // 清除会话信息
  sessionStorage.removeItem('authToken');
  localStorage.removeItem('auth');
  
  // 跳转到登录页
  window.location.href = '../login.html';
}

// 初始化修改密码模态框
document.addEventListener('DOMContentLoaded', function() {
  // 获取模态框元素
  const passwordModal = document.getElementById('passwordModal');
  const passwordForm = document.getElementById('changePasswordForm');
  const changePasswordBtn = document.getElementById('changePasswordBtn');
  const closeBtn = passwordModal.querySelector('.close');
  const cancelBtn = passwordModal.querySelector('.cancel-btn');
  const errorMessage = document.getElementById('passwordError');
  
  // 打开模态框
  changePasswordBtn.addEventListener('click', function() {
    passwordModal.style.display = 'block';
  });
  
  // 关闭模态框
  function closeModal() {
    passwordModal.style.display = 'none';
    passwordForm.reset();
    errorMessage.textContent = '';
  }
  
  closeBtn.addEventListener('click', closeModal);
  cancelBtn.addEventListener('click', closeModal);
  
  // 点击模态框外部关闭
  window.addEventListener('click', function(event) {
    if (event.target == passwordModal) {
      closeModal();
    }
  });
  
  // 表单提交
  passwordForm.addEventListener('submit', function(event) {
    event.preventDefault();
    
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    
    // 验证
    if (newPassword !== confirmPassword) {
      errorMessage.textContent = '新密码和确认密码不一致';
      return;
    }
    
    // 发送修改密码请求
    http.post('/api/change-password', {
      currentPassword,
      newPassword
    }).then(response => {
      alert('密码修改成功！');
      closeModal();
    }).catch(error => {
      errorMessage.textContent = '密码修改失败，请检查当前密码是否正确';
    });
  });
}); 