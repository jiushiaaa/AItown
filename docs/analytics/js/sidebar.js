// 侧边栏管理脚本

// 立即执行函数，确保在页面解析时就执行
(function() {
  // 确保营销策略菜单项始终可见
  ensureSidebarConsistency();
  
  // 页面加载完成后再执行一次，以防万一
  document.addEventListener('DOMContentLoaded', function() {
    ensureSidebarConsistency();
  });
  
  // 也在窗口加载完成后执行一次
  window.addEventListener('load', function() {
    ensureSidebarConsistency();
  });
})();

// 确保侧边栏的一致性
function ensureSidebarConsistency() {
  // 1. 确保营销策略菜单项存在
  const sidebarMenu = document.querySelector('.sidebar-menu');
  if (!sidebarMenu) return;
  
  // 检查是否已经存在营销策略菜单项
  const existingMarketingItem = document.querySelector('.sidebar-menu li a[href*="marketing"]');
  
  // 如果不存在，则创建
  if (!existingMarketingItem) {
    const marketingItem = document.createElement('li');
    marketingItem.className = 'sidebar-item';
    marketingItem.innerHTML = `
      <a href="./marketing.html" class="sidebar-link">
        <i class="icon-placeholder icon-idea"></i>
        营销策略
      </a>
    `;
    sidebarMenu.appendChild(marketingItem);
  }
  
  // 2. 根据当前页面URL设置active状态
  const currentUrl = window.location.href;
  const allMenuItems = document.querySelectorAll('.sidebar-menu li a');
  
  allMenuItems.forEach(link => {
    const href = link.getAttribute('href');
    // 移除所有active类
    link.classList.remove('active');
    
    // 如果是当前页面，添加active类
    if (currentUrl.includes(href)) {
      link.classList.add('active');
    }
  });
  
  // 3. 确保所有菜单项都有正确的图标
  ensureMenuIcons();
  
  // 4. 强制显示所有图标
  forceShowIcons();
}

// 确保所有菜单项有正确的图标
function ensureMenuIcons() {
  // 图标映射表 - 确保每个菜单项都有独特的图标
  const iconMap = {
    '仿真模拟系统': 'icon-simulation', // 🏭
    '模型配置': 'icon-settings', // ⚙️
    '数据概览': 'icon-dashboard', // 📊
    '消费者分析': 'icon-user', // 👤
    '地域分析': 'icon-location', // 🗺️
    '消费心理分析': 'icon-opportunity', // 🔍
    '营销策略': 'icon-idea' // 💡
  };
  
  // 为所有菜单项设置正确的图标
  const menuItems = document.querySelectorAll('.sidebar-menu li a');
  menuItems.forEach(item => {
    const text = item.textContent.trim();
    const iconClass = iconMap[text];
    
    if (iconClass) {
      // 查找现有图标元素
      const iconElement = item.querySelector('i');
      if (iconElement) {
        // 更新图标类
        iconElement.className = `icon-placeholder ${iconClass}`;
        // 确保图标可见
        iconElement.style.display = 'inline-block';
        iconElement.style.visibility = 'visible';
        iconElement.style.opacity = '1';
      } else {
        // 创建图标元素
        const icon = document.createElement('i');
        icon.className = `icon-placeholder ${iconClass}`;
        icon.style.display = 'inline-block';
        icon.style.visibility = 'visible';
        icon.style.opacity = '1';
        item.insertBefore(icon, item.firstChild);
      }
    }
  });
}

// 强制显示所有图标
function forceShowIcons() {
  // 选择所有图标元素
  const allIcons = document.querySelectorAll('.icon-placeholder');
  
  // 为每个图标添加内联样式，确保可见
  allIcons.forEach(icon => {
    icon.style.display = 'inline-block';
    icon.style.visibility = 'visible';
    icon.style.opacity = '1';
    
    // 使用计时器确保在页面渲染后仍然可见
    setTimeout(() => {
      icon.style.display = 'inline-block';
      icon.style.visibility = 'visible';
      icon.style.opacity = '1';
    }, 100);
  });
} 