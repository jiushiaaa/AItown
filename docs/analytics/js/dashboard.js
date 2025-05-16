// 数据概览页面脚本
document.addEventListener('DOMContentLoaded', function() {
  console.log('页面加载完成，检查ECharts和地图数据');
  
  // 验证ECharts和地图是否正确加载
  if (typeof echarts !== 'undefined') {
    console.log('ECharts已加载');
    
    // 检查中国地图数据是否已经注册
    if (echarts.getMap('china')) {
      console.log('中国地图数据已加载');
    } else {
      console.warn('中国地图数据未加载');
    }
  } else {
    console.error('ECharts未加载');
  }
  
  // 初始化页面
  initPage();
});

// 初始化页面
function initPage() {
  // 检查是否有模拟数据
  if (typeof DataService !== 'undefined' && DataService.hasSimulationData()) {
    console.log('检测到模拟数据，加载真实数据');
    loadSimulationData();
  } else {
    console.log('未检测到模拟数据，加载空白页面');
    // 初始化空白图表
    initEmptyCharts();
  }

  // 监听数据更新事件
  window.addEventListener('local_data_updated', function() {
    console.log('数据更新事件接收到，刷新页面数据');
    loadSimulationData();
  });

  // 初始化时间筛选器
  initTimeFilter(function(timeRange) {
    // 加载对应时间范围的数据
    loadData(timeRange);
  });
  
  // 初始化按钮事件
  document.getElementById('refreshTrendBtn').addEventListener('click', function() {
    const activeTimeRange = document.querySelector('.filter-option.active').getAttribute('data-value');
    loadData(activeTimeRange);
  });
  
  document.getElementById('refreshMapBtn').addEventListener('click', function() {
    const activeTimeRange = document.querySelector('.filter-option.active').getAttribute('data-value');
    loadData(activeTimeRange);
  });
  
  document.getElementById('refreshTypeBtn').addEventListener('click', function() {
    const activeTimeRange = document.querySelector('.filter-option.active').getAttribute('data-value');
    loadData(activeTimeRange);
  });
  
  document.getElementById('refreshPsychologyBtn').addEventListener('click', function() {
    const activeTimeRange = document.querySelector('.filter-option.active').getAttribute('data-value');
    loadData(activeTimeRange);
  });
  
  document.getElementById('testDataBtn').addEventListener('click', function() {
    console.log('点击了测试数据按钮');
    testMapData();
    loadMockData();
  });
}

// 初始化空白图表
function initEmptyCharts() {
  // 初始化所有图表为空状态
  renderEmptyRegionMapChart();
  renderEmptyTrendChart();
  renderEmptyConsumerTypeChart();
  renderEmptyPsychologyChart();
}

// 渲染空白区域地图
function renderEmptyRegionMapChart() {
  console.log('渲染空白区域地图');
  // 使用map-utils.js中的函数渲染空地图
  renderChinaMap('regionMapChart', [], {
    title: {
      text: '区域销售分布',
      left: 'center',
    },
    seriesName: '区域销售',
    tooltipFormatter: function(params) {
      // 确保数值正确格式化，避免NaN显示
      const value = isNaN(params.value) ? 0 : params.value;
      return `${params.name}<br/>销售额: ${value}万元`;
    },
    showLabel: false
  }).then(chart => {
    console.log('空白区域地图渲染完成');
  }).catch(error => {
    console.error('空白区域地图渲染失败:', error);
  });
}

// 将函数暴露到全局作用域，以便于地图加载失败时重新调用
window.renderEmptyRegionMapChart = renderEmptyRegionMapChart;

// 渲染空白销售趋势图
function renderEmptyTrendChart() {
  const chartDom = document.getElementById('trendChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['销售额', '订单量', '客流量']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: []
    },
    yAxis: [
      {
        type: 'value',
        name: '金额 (万元)',
        position: 'left'
      },
      {
        type: 'value',
        name: '数量',
        position: 'right'
      }
    ],
    series: [
      {
        name: '销售额',
        type: 'line',
        smooth: true,
        data: [],
        yAxisIndex: 0
      },
      {
        name: '订单量',
        type: 'line',
        smooth: true,
        data: [],
        yAxisIndex: 1
      },
      {
        name: '客流量',
        type: 'line',
        smooth: true,
        data: [],
        yAxisIndex: 1
      }
    ]
  };
  
  myChart.setOption(option);
  
  // 窗口大小变化时自动调整图表大小
  window.addEventListener('resize', function() {
    myChart.resize();
  });
}

// 渲染空白消费者类型分布图
function renderEmptyConsumerTypeChart() {
  const chartDom = document.getElementById('consumerTypeChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      data: []
    },
    series: [
      {
        name: '消费者类型',
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['40%', '50%'],
        data: []
      }
    ]
  };
  
  myChart.setOption(option);
  
  // 窗口大小变化时自动调整图表大小
  window.addEventListener('resize', function() {
    myChart.resize();
  });
}

// 渲染空白消费心理分析图
function renderEmptyPsychologyChart() {
  const chartDom = document.getElementById('psychologyChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'item'
    },
    radar: {
      indicator: []
    },
    series: [
      {
        name: '消费心理分析',
        type: 'radar',
        data: []
      }
    ]
  };
  
  myChart.setOption(option);
  
  // 窗口大小变化时自动调整图表大小
  window.addEventListener('resize', function() {
    myChart.resize();
  });
}

// 加载指定时间范围的数据
async function loadData(timeRange) {
  try {
    // 显示加载状态
    showLoading();
    
    // 获取数据
    const data = await fetchDashboardData(timeRange);
    
    // 更新核心指标
    updateMetrics(data.metrics);
    
    // 更新图表
    updateCharts(data.charts);
    
    // 隐藏加载状态
    hideLoading();
  } catch (error) {
    console.error('加载数据失败:', error);
    // 加载失败时使用模拟数据
    loadMockData();
  }
}

// 显示加载状态
function showLoading() {
  // 可以添加加载动画效果
  document.querySelectorAll('.chart-content').forEach(chart => {
    chart.classList.add('loading');
  });
}

// 隐藏加载状态
function hideLoading() {
  document.querySelectorAll('.chart-content').forEach(chart => {
    chart.classList.remove('loading');
  });
}

// 从API获取仪表盘数据
async function fetchDashboardData(timeRange) {
  try {
    // 发送API请求获取数据
    const response = await http.get('/api/dashboard', { timeRange });
    return response.data;
  } catch (error) {
    console.error('API请求失败:', error);
    // 返回模拟数据
    return generateMockData(timeRange);
  }
}

// 更新核心指标
function updateMetrics(metrics) {
  // 更新访问量
  document.getElementById('visitCount').textContent = formatNumber(metrics.visitCount);
  document.getElementById('visitTrend').textContent = metrics.visitTrend;
  updateTrendStyle('visitTrend', metrics.visitTrend);
  
  // 更新客流量
  document.getElementById('customerCount').textContent = formatNumber(metrics.customerCount);
  document.getElementById('customerTrend').textContent = metrics.customerTrend;
  updateTrendStyle('customerTrend', metrics.customerTrend);
  
  // 更新订单数
  document.getElementById('orderCount').textContent = formatNumber(metrics.orderCount);
  document.getElementById('orderTrend').textContent = metrics.orderTrend;
  updateTrendStyle('orderTrend', metrics.orderTrend);
  
  // 更新消费者数
  document.getElementById('consumerCount').textContent = formatNumber(metrics.consumerCount);
  document.getElementById('consumerTrend').textContent = Math.abs(metrics.consumerTrend);
  updateTrendStyle('consumerTrend', metrics.consumerTrend);
  
  // 更新成交率
  document.getElementById('conversionRate').textContent = metrics.conversionRate;
  document.getElementById('conversionTrend').textContent = metrics.conversionTrend;
  updateTrendStyle('conversionTrend', metrics.conversionTrend);
  
  // 更新平均停留时间
  document.getElementById('stayTime').textContent = metrics.stayTime;
  document.getElementById('stayTimeTrend').textContent = metrics.stayTimeTrend;
  updateTrendStyle('stayTimeTrend', metrics.stayTimeTrend);
}

// 更新趋势样式
function updateTrendStyle(elementId, trendValue) {
  const element = document.getElementById(elementId).parentNode;
  const arrowElement = element.querySelector('.trend-arrow');
  
  if (trendValue >= 0) {
    element.classList.remove('negative');
    element.classList.add('positive');
    arrowElement.textContent = '↑';
  } else {
    element.classList.remove('positive');
    element.classList.add('negative');
    arrowElement.textContent = '↓';
  }
}

// 更新图表
function updateCharts(chartsData) {
  // 1. 区域销售分布图
  renderRegionMapChart(chartsData.regionMap);
  
  // 2. 销售趋势图
  renderTrendChart(chartsData.salesTrend);
  
  // 3. 消费者类型分布
  renderConsumerTypeChart(chartsData.consumerTypes);
  
  // 4. 消费心理分析
  renderPsychologyChart(chartsData.psychology);
}

// 渲染区域地图
function renderRegionMapChart(mapData) {
  console.log('渲染地图数据', mapData);
  
  // 确保数据格式正确并验证每个数据项
  if (mapData && Array.isArray(mapData)) {
    // 创建一个省份名称映射表，解决名称不匹配问题
    const provinceNameMap = {
      '北京': '北京市',
      '天津': '天津市',
      '上海': '上海市',
      '重庆': '重庆市',
      '内蒙古': '内蒙古自治区',
      '新疆': '新疆维吾尔自治区',
      '西藏': '西藏自治区',
      '广西': '广西壮族自治区',
      '宁夏': '宁夏回族自治区',
      '香港': '香港特别行政区',
      '澳门': '澳门特别行政区',
      '黑龙江': '黑龙江省',
      '吉林': '吉林省',
      '辽宁': '辽宁省',
      '河北': '河北省',
      '河南': '河南省',
      '山东': '山东省',
      '山西': '山西省',
      '江苏': '江苏省',
      '安徽': '安徽省',
      '浙江': '浙江省',
      '福建': '福建省',
      '江西': '江西省',
      '湖南': '湖南省',
      '湖北': '湖北省',
      '广东': '广东省',
      '云南': '云南省',
      '贵州': '贵州省',
      '四川': '四川省',
      '陕西': '陕西省',
      '甘肃': '甘肃省',
      '青海': '青海省',
      '海南': '海南省',
      '台湾': '台湾省'
    };
    
    // 创建一个反向映射表，用于在工具提示中查找数据
    const reverseProvinceNameMap = {};
    Object.keys(provinceNameMap).forEach(shortName => {
      reverseProvinceNameMap[provinceNameMap[shortName]] = shortName;
    });
    
    // 处理数据，确保省份名称匹配
    const processedMapData = mapData.map(item => {
      // 检查是否需要映射省份名称
      const displayName = provinceNameMap[item.name] || item.name;
      
      console.log(`省份数据: ${item.name} -> ${displayName}, 值: ${item.value}`);
      
      // 确保值是有效的数字
      if (typeof item.value !== 'number' || isNaN(item.value)) {
        console.warn(`警告: ${item.name}的值不是有效数字，正在修复`);
        item.value = parseInt(item.value) || 0;
      }
      
      return {
        name: displayName, // 使用完整省份名称
        value: item.value,
        originalName: item.name // 保存原始名称，方便调试
      };
    });
  
  // 使用map-utils.js中的函数渲染地图
    renderChinaMap('regionMapChart', processedMapData, {
    title: {
      text: '区域销售分布',
      left: 'center',
    },
    seriesName: '区域销售',
    tooltipFormatter: function(params) {
      console.log('区域地图tooltip参数:', params);
      
      // 调试输出完整参数
      console.log('完整参数结构:', JSON.stringify(params));
      
        // 根据地图显示的省份名称找出对应的原始数据名称
        const shortName = reverseProvinceNameMap[params.name] || params.name;
        
        // 找到对应的原始数据项
        const originalDataItem = mapData.find(item => item.name === shortName);
        
        // 如果找到了原始数据，使用它的value，否则使用0
      let value = 0;
        if (originalDataItem && typeof originalDataItem.value === 'number') {
          value = originalDataItem.value;
          console.log(`找到原始数据: ${shortName}, 值: ${value}`);
        } else if (params.data && typeof params.data.value === 'number') {
          value = params.data.value;
          console.log(`使用params.data.value: ${value}`);
        } else if (typeof params.value === 'number') {
          value = params.value;
          console.log(`使用params.value: ${value}`);
      } else {
          console.log(`未找到${params.name}(${shortName})的有效数据，使用默认值0`);
      }
      
      return `${params.name}<br/>销售额: ${value}万元`;
    },
    showLabel: false,
    visualMap: {
      type: 'piecewise',
      pieces: [
        {min: 100, label: '100万以上'},
        {min: 50, max: 100, label: '50-100万'},
        {min: 20, max: 50, label: '20-50万'},
        {min: 10, max: 20, label: '10-20万'},
        {min: 5, max: 10, label: '5-10万'},
        {max: 5, label: '5万以下'}
      ],
      inRange: {
        color: ['#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695']
      }
    }
  }).then(chart => {
    console.log('区域地图渲染完成');
  }).catch(error => {
    console.error('区域地图渲染失败:', error);
  });
  } else {
    console.error('地图数据格式不正确', mapData);
    mapData = []; // 防止错误
    
    // 使用空数据渲染地图
    renderChinaMap('regionMapChart', [], {
      title: {
        text: '区域销售分布',
        left: 'center',
      },
      seriesName: '区域销售',
      tooltipFormatter: function(params) {
        return `${params.name}<br/>销售额: 0万元`;
      },
      showLabel: false
    }).catch(error => {
      console.error('空数据地图渲染失败:', error);
    });
  }
}

// 渲染销售趋势图
function renderTrendChart(trendData) {
  const chartDom = document.getElementById('trendChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['销售额', '订单量', '客流量']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: trendData.dates
    },
    yAxis: [
      {
        type: 'value',
        name: '金额 (万元)',
        position: 'left'
      },
      {
        type: 'value',
        name: '数量',
        position: 'right'
      }
    ],
    series: [
      {
        name: '销售额',
        type: 'line',
        smooth: true,
        emphasis: {
          focus: 'series'
        },
        data: trendData.sales,
        yAxisIndex: 0,
        itemStyle: {
          color: '#1890ff'
        }
      },
      {
        name: '订单量',
        type: 'line',
        smooth: true,
        emphasis: {
          focus: 'series'
        },
        data: trendData.orders,
        yAxisIndex: 1,
        itemStyle: {
          color: '#13c2c2'
        }
      },
      {
        name: '客流量',
        type: 'line',
        smooth: true,
        emphasis: {
          focus: 'series'
        },
        data: trendData.customers,
        yAxisIndex: 1,
        itemStyle: {
          color: '#722ed1'
        }
      }
    ]
  };
  
  myChart.setOption(option);
  
  // 窗口大小变化时自动调整图表大小
  window.addEventListener('resize', function() {
    myChart.resize();
  });
}

// 渲染消费者类型分布图
function renderConsumerTypeChart(typeData) {
  const chartDom = document.getElementById('consumerTypeChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      data: typeData.map(item => item.name)
    },
    series: [
      {
        name: '消费者类型',
        type: 'pie',
        radius: ['45%', '70%'],
        center: ['40%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 5,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '14',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: typeData
      }
    ]
  };
  
  myChart.setOption(option);
  
  // 窗口大小变化时自动调整图表大小
  window.addEventListener('resize', function() {
    myChart.resize();
  });
}

// 渲染消费心理分析图
function renderPsychologyChart(psychologyData) {
  const chartDom = document.getElementById('psychologyChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'item'
    },
    radar: {
      indicator: psychologyData.indicators
    },
    series: [
      {
        name: '消费心理分析',
        type: 'radar',
        data: [
          {
            value: psychologyData.values,
            name: '消费者心理特征',
            areaStyle: {
              color: 'rgba(24, 144, 255, 0.3)'
            },
            lineStyle: {
              color: '#1890ff'
            },
            itemStyle: {
              color: '#1890ff'
            }
          }
        ]
      }
    ]
  };
  
  myChart.setOption(option);
  
  // 窗口大小变化时自动调整图表大小
  window.addEventListener('resize', function() {
    myChart.resize();
  });
}

// 加载模拟数据
function loadMockData() {
  // 生成模拟数据
  const mockData = generateMockData('7days');
  
  // 更新核心指标
  updateMetrics(mockData.metrics);
  
  // 更新图表
  updateCharts(mockData.charts);
}

// 生成模拟数据
function generateMockData(timeRange) {
  // 核心指标模拟数据
  const metrics = {
    visitCount: Math.floor(Math.random() * 10000) + 5000,
    visitTrend: (Math.random() * 20).toFixed(1),
    customerCount: Math.floor(Math.random() * 5000) + 2000,
    customerTrend: (Math.random() * 15).toFixed(1),
    orderCount: Math.floor(Math.random() * 2000) + 1000,
    orderTrend: (Math.random() * 10).toFixed(1),
    consumerCount: Math.floor(Math.random() * 3000) + 1500,
    consumerTrend: -((Math.random() * 5).toFixed(1)),
    conversionRate: (Math.random() * 30 + 20).toFixed(1),
    conversionTrend: (Math.random() * 8).toFixed(1),
    stayTime: (Math.random() * 20 + 15).toFixed(1),
    stayTimeTrend: (Math.random() * 12).toFixed(1)
  };
  
  // 生成日期数组
  const dates = [];
  const today = new Date();
  let days;
  
  switch(timeRange) {
    case 'today':
      days = 24; // 24小时
      for (let i = 0; i < days; i++) {
        dates.push(`${i}:00`);
      }
      break;
    case 'yesterday':
      days = 24; // 24小时
      for (let i = 0; i < days; i++) {
        dates.push(`${i}:00`);
      }
      break;
    case '7days':
      days = 7;
      for (let i = days - 1; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        dates.push(`${date.getMonth() + 1}/${date.getDate()}`);
      }
      break;
    case '30days':
      days = 30;
      for (let i = days - 1; i >= 0; i -= 2) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        dates.push(`${date.getMonth() + 1}/${date.getDate()}`);
      }
      break;
    case '90days':
      days = 90;
      for (let i = days - 1; i >= 0; i -= 6) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        dates.push(`${date.getMonth() + 1}/${date.getDate()}`);
      }
      break;
    default:
      days = 7;
      for (let i = days - 1; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        dates.push(`${date.getMonth() + 1}/${date.getDate()}`);
      }
  }
  
  // 生成销售趋势数据
  const sales = [];
  const orders = [];
  const customers = [];
  
  for (let i = 0; i < dates.length; i++) {
    sales.push((Math.random() * 100 + 50).toFixed(1));
    orders.push(Math.floor(Math.random() * 300) + 100);
    customers.push(Math.floor(Math.random() * 500) + 200);
  }
  
  // 生成区域销售数据
  const provinces = [
    '北京', '天津', '上海', '重庆', '河北', '山西', '辽宁', '吉林', '黑龙江',
    '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南',
    '广东', '广西', '海南', '四川', '贵州', '云南', '西藏', '陕西', '甘肃',
    '青海', '宁夏', '新疆'
  ];
  
  const regionMap = provinces.map(province => {
    return {
      name: province,
      value: Math.floor(Math.random() * 100) + 1
    };
  });
  
  // 特殊调整，设置一些热门省份销售额更高
  const hotProvinces = ['浙江', '福建', '江苏', '北京', '广东', '上海'];
  regionMap.forEach(item => {
    if (hotProvinces.includes(item.name)) {
      item.value = Math.floor(Math.random() * 100) + 50;
    }
  });
  
  // 生成消费者类型分布数据
  const consumerTypes = [
    { value: Math.floor(Math.random() * 300) + 500, name: '品质追求型' },
    { value: Math.floor(Math.random() * 300) + 300, name: '健康养生型' },
    { value: Math.floor(Math.random() * 200) + 200, name: '礼品馈赠型' },
    { value: Math.floor(Math.random() * 150) + 150, name: '收藏投资型' },
    { value: Math.floor(Math.random() * 100) + 100, name: '其他类型' }
  ];
  
  // 生成消费心理分析数据
  const psychology = {
    indicators: [
      { name: '品质追求', max: 100 },
      { name: '健康意识', max: 100 },
      { name: '价格敏感', max: 100 },
      { name: '品牌偏好', max: 100 },
      { name: '情感共鸣', max: 100 },
      { name: '投资价值', max: 100 }
    ],
    values: [
      Math.floor(Math.random() * 20) + 80,
      Math.floor(Math.random() * 20) + 70,
      Math.floor(Math.random() * 30) + 40,
      Math.floor(Math.random() * 20) + 60,
      Math.floor(Math.random() * 25) + 65,
      Math.floor(Math.random() * 30) + 50
    ]
  };
  
  return {
    metrics: metrics,
    charts: {
      regionMap: regionMap,
      salesTrend: {
        dates: dates,
        sales: sales,
        orders: orders,
        customers: customers
      },
      consumerTypes: consumerTypes,
      psychology: psychology
    }
  };
}

// 格式化数字，添加千位分隔符
function formatNumber(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// 加载区域销售地图数据
function loadRegionMapData() {
  // 这里可以换成从服务器加载数据的代码
  // 返回模拟数据，使用正确的省份全名
  return [
    { name: '北京市', value: 200 },
    { name: '天津市', value: 150 },
    { name: '河北省', value: 120 },
    { name: '山西省', value: 80 },
    { name: '内蒙古自治区', value: 60 },
    { name: '辽宁省', value: 110 },
    { name: '吉林省', value: 70 },
    { name: '黑龙江省', value: 65 },
    { name: '上海市', value: 210 },
    { name: '江苏省', value: 180 },
    { name: '浙江省', value: 190 },
    { name: '安徽省', value: 95 },
    { name: '福建省', value: 125 },
    { name: '江西省', value: 85 },
    { name: '山东省', value: 170 },
    { name: '河南省', value: 140 },
    { name: '湖北省', value: 130 },
    { name: '湖南省', value: 120 },
    { name: '广东省', value: 220 },
    { name: '广西壮族自治区', value: 90 },
    { name: '海南省', value: 75 },
    { name: '重庆市', value: 115 },
    { name: '四川省', value: 135 },
    { name: '贵州省', value: 70 },
    { name: '云南省', value: 80 },
    { name: '西藏自治区', value: 45 },
    { name: '陕西省', value: 95 },
    { name: '甘肃省', value: 55 },
    { name: '青海省', value: 40 },
    { name: '宁夏回族自治区', value: 35 },
    { name: '新疆维吾尔自治区', value: 65 }
  ];
}

// 测试地图数据
function testMapData() {
  console.log('测试地图数据加载');
  try {
    // 检查中国地图是否已载入
    if (echarts.getMap('china')) {
      console.log('中国地图数据已正确载入');
    } else {
      console.warn('中国地图数据未载入，尝试手动注册');
      // 如果地图未载入，尝试多种路径加载地图数据并注册
      const possiblePaths = [
        '../Assets/map.json',
        './Assets/map.json',
        '/Assets/map.json',
        '/web/Assets/map.json'
      ];
      
      let loadPromises = possiblePaths.map(path => 
        fetch(path, {
          cache: 'force-cache',
          timeout: 10000
        })
        .then(response => {
          if (!response.ok) {
            throw new Error(`从 ${path} 加载失败，状态码：${response.status}`);
          }
          return response.json();
        })
        .then(geoJson => {
          console.log(`从 ${path} 手动加载地图数据成功，正在注册`);
          echarts.registerMap('china', geoJson);
          
          // 获取地图中的省份名称，用于调试
          if (geoJson && geoJson.features) {
            const provinceNames = geoJson.features.map(feature => 
              feature.properties && feature.properties.name
            ).filter(Boolean);
            console.log('地图包含的省份名称:', provinceNames.join(', '));
          }
          
          console.log('手动注册地图数据成功');
          return true;
        })
        .catch(error => {
          console.warn(`路径 ${path} 加载失败:`, error);
          return false;
        })
      );
      
      // 使用Promise.any等待任意一个成功
      Promise.any(loadPromises).catch(error => {
        console.error('所有地图数据加载尝试都失败:', error);
        // 如果所有加载都失败，尝试创建一个空地图结构
        try {
          console.log('尝试使用空地图数据初始化');
          const emptyMapData = {"type":"FeatureCollection","features":[]};
          echarts.registerMap('china', emptyMapData);
          console.log('使用空地图数据初始化成功');
        } catch (e) {
          console.error('空地图数据初始化失败:', e);
        }
        });
    }
    
    // 使用标准省份全名的测试数据
    const testData = [
      { name: '北京市', value: 200 },
      { name: '天津市', value: 150 },
      { name: '河北省', value: 120 },
      { name: '山西省', value: 80 },
      { name: '内蒙古自治区', value: 60 },
      { name: '辽宁省', value: 110 },
      { name: '吉林省', value: 70 },
      { name: '黑龙江省', value: 65 },
      { name: '上海市', value: 210 },
      { name: '江苏省', value: 180 },
      { name: '浙江省', value: 190 },
      { name: '安徽省', value: 95 },
      { name: '福建省', value: 125 },
      { name: '江西省', value: 85 },
      { name: '山东省', value: 170 },
      { name: '河南省', value: 140 },
      { name: '湖北省', value: 130 },
      { name: '湖南省', value: 120 },
      { name: '广东省', value: 220 },
      { name: '广西壮族自治区', value: 90 },
      { name: '海南省', value: 75 },
      { name: '重庆市', value: 115 },
      { name: '四川省', value: 135 },
      { name: '贵州省', value: 70 },
      { name: '云南省', value: 80 },
      { name: '西藏自治区', value: 45 },
      { name: '陕西省', value: 95 },
      { name: '甘肃省', value: 55 },
      { name: '青海省', value: 40 },
      { name: '宁夏回族自治区', value: 35 },
      { name: '新疆维吾尔自治区', value: 65 }
    ];
    
    console.log('使用硬编码的测试数据:', testData);
    // 直接渲染硬编码的测试数据
    renderRegionMapChart(testData);
  } catch (error) {
    console.error('测试地图数据时出错:', error);
    // 出错时也尝试渲染测试数据
    try {
      const testData = [
        { name: '北京市', value: 200 },
        { name: '上海市', value: 210 },
        { name: '广东省', value: 220 }
      ];
      console.log('尝试使用简化测试数据渲染');
      renderRegionMapChart(testData);
    } catch (e) {
      console.error('使用简化测试数据渲染失败:', e);
    }
  }
}

// 从模拟数据中加载真实数据
function loadSimulationData() {
  console.log('从模拟数据加载仪表盘数据');
  showLoading();
  
  try {
    // 获取模拟结果数据
    const simulationResult = DataService.getSimulationResult();
    
    if (simulationResult && simulationResult.length > 0) {
      const data = simulationResult[0];
      console.log('获取到模拟数据:', data);
      
      // 提取并更新核心指标
      if (data.metrics) {
        updateMetrics(data.metrics);
      } else {
        // 没有指标数据，生成模拟指标
        const mockMetrics = generateDefaultMetrics();
        updateMetrics(mockMetrics);
      }
      
      // 提取并更新图表数据
      if (data.charts) {
        updateCharts(data.charts);
      } else {
        // 没有图表数据，生成模拟图表
        const mockCharts = generateDefaultCharts();
        updateCharts(mockCharts);
      }
    } else {
      console.log('模拟结果为空，加载默认数据');
      loadMockData();
    }
  } catch (error) {
    console.error('加载模拟数据出错:', error);
    loadMockData();
  } finally {
    hideLoading();
  }
}

// 生成默认指标数据
function generateDefaultMetrics() {
  return {
    visitCount: 12500,
    visitTrend: 15.6,
    customerCount: 8760,
    customerTrend: 12.3,
    orderCount: 3254,
    orderTrend: 8.7,
    consumerCount: 2180,
    consumerTrend: -3.2,
    conversionRate: 28.5,
    conversionTrend: 4.5,
    stayTime: 8.3,
    stayTimeTrend: 6.1
  };
}

// 生成默认图表数据
function generateDefaultCharts() {
  return {
    mapData: generateRandomMapData(),
    trendData: generateRandomTrendData(),
    typeData: generateRandomTypeData(),
    psychologyData: generateRandomPsychologyData()
  };
} 