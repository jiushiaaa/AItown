// 消费者分析页面脚本
document.addEventListener('DOMContentLoaded', function() {
  // 初始化页面
  initPage();
});

// 初始化页面
function initPage() {
  // 初始化时间筛选器
  initTimeFilter(function(timeRange) {
    // 加载对应时间范围的数据
    loadData(timeRange);
  });
  
  // 初始化按钮事件
  document.getElementById('refreshPortraitBtn').addEventListener('click', function() {
    const activeTimeRange = document.querySelector('.filter-option.active').getAttribute('data-value');
    loadData(activeTimeRange);
  });
  
  document.getElementById('refreshAgeBtn').addEventListener('click', function() {
    const activeTimeRange = document.querySelector('.filter-option.active').getAttribute('data-value');
    loadData(activeTimeRange);
  });
  
  document.getElementById('refreshOccupationBtn').addEventListener('click', function() {
    const activeTimeRange = document.querySelector('.filter-option.active').getAttribute('data-value');
    loadData(activeTimeRange);
  });
  
  document.getElementById('refreshFrequencyBtn').addEventListener('click', function() {
    const activeTimeRange = document.querySelector('.filter-option.active').getAttribute('data-value');
    loadData(activeTimeRange);
  });
  
  document.getElementById('refreshLoyaltyBtn').addEventListener('click', function() {
    const activeTimeRange = document.querySelector('.filter-option.active').getAttribute('data-value');
    loadData(activeTimeRange);
  });
  
  document.getElementById('testDataBtn').addEventListener('click', function() {
    loadMockData();
  });
  
  // 初始化空白图表
  initEmptyCharts();
}

// 初始化空白图表
function initEmptyCharts() {
  // 初始化所有图表为空状态
  renderEmptyConsumerPortraitChart();
  renderEmptyAgeDistributionChart();
  renderEmptyOccupationChart();
  renderEmptyPurchaseFrequencyChart();
  renderEmptyLoyaltyChart();
  
  // 清空指标显示
  clearMetrics();
}

// 清空指标显示
function clearMetrics() {
  document.getElementById('newConsumers').textContent = '--';
  document.getElementById('activeConsumers').textContent = '--';
  document.getElementById('avgOrderValue').textContent = '--';
  document.getElementById('repurchaseRate').textContent = '--';
  
  document.getElementById('newConsumersTrend').textContent = '--';
  document.getElementById('activeConsumersTrend').textContent = '--';
  document.getElementById('avgOrderValueTrend').textContent = '--';
  document.getElementById('repurchaseRateTrend').textContent = '--';
}

// 渲染空白消费者画像图表
function renderEmptyConsumerPortraitChart() {
  const chartDom = document.getElementById('consumerPortraitChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['当前值', '行业平均']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      boundaryGap: [0, 0.01],
      max: 100
    },
    yAxis: {
      type: 'category',
      data: []
    },
    series: [
      {
        name: '当前值',
        type: 'bar',
        data: []
      },
      {
        name: '行业平均',
        type: 'bar',
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

// 渲染空白年龄分布图表
function renderEmptyAgeDistributionChart() {
  const chartDom = document.getElementById('ageDistributionChart');
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
        name: '年龄分布',
        type: 'pie',
        radius: ['50%', '70%'],
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

// 渲染空白职业分布图表
function renderEmptyOccupationChart() {
  const chartDom = document.getElementById('occupationChart');
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
        name: '职业分布',
        type: 'pie',
        radius: '55%',
        center: ['40%', '50%'],
        roseType: 'radius',
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

// 渲染空白消费频率分析图表
function renderEmptyPurchaseFrequencyChart() {
  const chartDom = document.getElementById('purchaseFrequencyChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        crossStyle: {
          color: '#999'
        }
      }
    },
    legend: {
      data: ['消费者数量', '消费金额', '消费占比']
    },
    xAxis: [
      {
        type: 'category',
        data: [],
        axisPointer: {
          type: 'shadow'
        }
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: '人数',
        min: 0,
        axisLabel: {
          formatter: '{value} 人'
        }
      },
      {
        type: 'value',
        name: '金额/占比',
        min: 0,
        max: 100,
        axisLabel: {
          formatter: '{value} %'
        }
      }
    ],
    series: [
      {
        name: '消费者数量',
        type: 'bar',
        data: []
      },
      {
        name: '消费金额',
        type: 'bar',
        data: []
      },
      {
        name: '消费占比',
        type: 'line',
        yAxisIndex: 1,
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

// 渲染空白消费者忠诚度分析图表
function renderEmptyLoyaltyChart() {
  const chartDom = document.getElementById('loyaltyChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      top: '5%',
      left: 'center'
    },
    series: [
      {
        name: '忠诚度分布',
        type: 'funnel',
        left: '10%',
        top: 60,
        bottom: 60,
        width: '80%',
        min: 0,
        max: 100,
        minSize: '0%',
        maxSize: '100%',
        sort: 'descending',
        gap: 2,
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
    const data = await fetchConsumerData(timeRange);
    
    // 更新消费者概览指标
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

// 从API获取消费者分析数据
async function fetchConsumerData(timeRange) {
  try {
    // 发送API请求获取数据
    const response = await http.get('/api/consumer-analysis', { timeRange });
    return response.data;
  } catch (error) {
    console.error('API请求失败:', error);
    // 返回模拟数据
    return generateMockData(timeRange);
  }
}

// 更新消费者概览指标
function updateMetrics(metrics) {
  // 更新新增消费者
  document.getElementById('newConsumers').textContent = formatNumber(metrics.newConsumers);
  document.getElementById('newConsumersTrend').textContent = metrics.newConsumersTrend;
  updateTrendStyle('newConsumersTrend', metrics.newConsumersTrend);
  
  // 更新活跃消费者
  document.getElementById('activeConsumers').textContent = formatNumber(metrics.activeConsumers);
  document.getElementById('activeConsumersTrend').textContent = metrics.activeConsumersTrend;
  updateTrendStyle('activeConsumersTrend', metrics.activeConsumersTrend);
  
  // 更新平均客单价
  document.getElementById('avgOrderValue').textContent = metrics.avgOrderValue;
  document.getElementById('avgOrderValueTrend').textContent = metrics.avgOrderValueTrend;
  updateTrendStyle('avgOrderValueTrend', metrics.avgOrderValueTrend);
  
  // 更新复购率
  document.getElementById('repurchaseRate').textContent = metrics.repurchaseRate;
  document.getElementById('repurchaseRateTrend').textContent = Math.abs(metrics.repurchaseRateTrend);
  updateTrendStyle('repurchaseRateTrend', metrics.repurchaseRateTrend);
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
  // 消费者画像
  renderConsumerPortraitChart(chartsData.consumerPortrait);
  
  // 年龄分布
  renderAgeDistributionChart(chartsData.ageDistribution);
  
  // 职业分布
  renderOccupationChart(chartsData.occupation);
  
  // 消费频率分析
  renderPurchaseFrequencyChart(chartsData.purchaseFrequency);
  
  // 消费者忠诚度分析
  renderLoyaltyChart(chartsData.loyalty);
}

// 渲染消费者画像图表
function renderConsumerPortraitChart(portraitData) {
  const chartDom = document.getElementById('consumerPortraitChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['当前值', '行业平均']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      boundaryGap: [0, 0.01],
      max: 100
    },
    yAxis: {
      type: 'category',
      data: portraitData.labels
    },
    series: [
      {
        name: '当前值',
        type: 'bar',
        data: portraitData.values,
        itemStyle: {
          color: '#1890ff'
        }
      },
      {
        name: '行业平均',
        type: 'bar',
        data: portraitData.averages,
        itemStyle: {
          color: '#bfbfbf'
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

// 渲染年龄分布图表
function renderAgeDistributionChart(ageData) {
  const chartDom = document.getElementById('ageDistributionChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}人 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      data: ageData.map(item => item.name)
    },
    series: [
      {
        name: '年龄分布',
        type: 'pie',
        radius: ['50%', '70%'],
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
        data: ageData
      }
    ]
  };
  
  myChart.setOption(option);
  
  // 窗口大小变化时自动调整图表大小
  window.addEventListener('resize', function() {
    myChart.resize();
  });
}

// 渲染职业分布图表
function renderOccupationChart(occupationData) {
  const chartDom = document.getElementById('occupationChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}人 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      data: occupationData.map(item => item.name)
    },
    series: [
      {
        name: '职业分布',
        type: 'pie',
        radius: '55%',
        center: ['40%', '50%'],
        roseType: 'radius',
        itemStyle: {
          borderRadius: 5,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true
          }
        },
        data: occupationData
      }
    ]
  };
  
  myChart.setOption(option);
  
  // 窗口大小变化时自动调整图表大小
  window.addEventListener('resize', function() {
    myChart.resize();
  });
}

// 渲染消费频率分析图表
function renderPurchaseFrequencyChart(frequencyData) {
  const chartDom = document.getElementById('purchaseFrequencyChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        crossStyle: {
          color: '#999'
        }
      }
    },
    legend: {
      data: ['消费者数量', '消费金额', '消费占比']
    },
    xAxis: [
      {
        type: 'category',
        data: frequencyData.categories,
        axisPointer: {
          type: 'shadow'
        }
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: '人数',
        min: 0,
        axisLabel: {
          formatter: '{value} 人'
        }
      },
      {
        type: 'value',
        name: '金额/占比',
        min: 0,
        max: 100,
        axisLabel: {
          formatter: '{value} %'
        }
      }
    ],
    series: [
      {
        name: '消费者数量',
        type: 'bar',
        data: frequencyData.consumerCounts,
        itemStyle: {
          color: '#5470c6'
        }
      },
      {
        name: '消费金额',
        type: 'bar',
        data: frequencyData.purchaseAmounts,
        itemStyle: {
          color: '#91cc75'
        }
      },
      {
        name: '消费占比',
        type: 'line',
        yAxisIndex: 1,
        data: frequencyData.percentages,
        itemStyle: {
          color: '#ee6666'
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

// 渲染消费者忠诚度分析图表
function renderLoyaltyChart(loyaltyData) {
  const chartDom = document.getElementById('loyaltyChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      top: '5%',
      left: 'center'
    },
    series: [
      {
        name: '忠诚度分布',
        type: 'funnel',
        left: '10%',
        top: 60,
        bottom: 60,
        width: '80%',
        min: 0,
        max: 100,
        minSize: '0%',
        maxSize: '100%',
        sort: 'descending',
        gap: 2,
        label: {
          show: true,
          position: 'inside'
        },
        labelLine: {
          length: 10,
          lineStyle: {
            width: 1,
            type: 'solid'
          }
        },
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 1
        },
        emphasis: {
          label: {
            fontSize: 16
          }
        },
        data: loyaltyData
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
  
  // 更新消费者概览指标
  updateMetrics(mockData.metrics);
  
  // 更新图表
  updateCharts(mockData.charts);
}

// 生成模拟数据
function generateMockData(timeRange) {
  // 消费者概览指标模拟数据
  const metrics = {
    newConsumers: Math.floor(Math.random() * 1000) + 500,
    newConsumersTrend: (Math.random() * 15).toFixed(1),
    activeConsumers: Math.floor(Math.random() * 5000) + 2000,
    activeConsumersTrend: (Math.random() * 10).toFixed(1),
    avgOrderValue: (Math.random() * 300 + 200).toFixed(0),
    avgOrderValueTrend: (Math.random() * 8).toFixed(1),
    repurchaseRate: (Math.random() * 20 + 30).toFixed(1),
    repurchaseRateTrend: -((Math.random() * 5).toFixed(1))
  };
  
  // 消费者画像数据
  const consumerPortrait = {
    labels: ['品质关注度', '健康意识', '价格敏感度', '对产品认知', '购买力', '品牌忠诚度'],
    values: [
      Math.floor(Math.random() * 15) + 85,
      Math.floor(Math.random() * 15) + 80,
      Math.floor(Math.random() * 20) + 50,
      Math.floor(Math.random() * 20) + 70,
      Math.floor(Math.random() * 15) + 75,
      Math.floor(Math.random() * 25) + 60
    ],
    averages: [
      Math.floor(Math.random() * 15) + 65,
      Math.floor(Math.random() * 15) + 60,
      Math.floor(Math.random() * 15) + 70,
      Math.floor(Math.random() * 15) + 55,
      Math.floor(Math.random() * 15) + 60,
      Math.floor(Math.random() * 15) + 50
    ]
  };
  
  // 年龄分布数据
  const ageDistribution = [
    { value: Math.floor(Math.random() * 200) + 100, name: '18-24岁' },
    { value: Math.floor(Math.random() * 400) + 300, name: '25-34岁' },
    { value: Math.floor(Math.random() * 600) + 500, name: '35-44岁' },
    { value: Math.floor(Math.random() * 400) + 400, name: '45-54岁' },
    { value: Math.floor(Math.random() * 300) + 200, name: '55岁以上' }
  ];
  
  // 职业分布数据
  const occupation = [
    { value: Math.floor(Math.random() * 300) + 500, name: '企业高管' },
    { value: Math.floor(Math.random() * 300) + 400, name: '公务员' },
    { value: Math.floor(Math.random() * 300) + 300, name: '专业人士' },
    { value: Math.floor(Math.random() * 200) + 200, name: '自由职业' },
    { value: Math.floor(Math.random() * 200) + 200, name: '教师' },
    { value: Math.floor(Math.random() * 150) + 100, name: '学生' },
    { value: Math.floor(Math.random() * 150) + 150, name: '其他' }
  ];
  
  // 消费频率分析数据
  const purchaseFrequency = {
    categories: ['首次消费', '偶尔消费', '定期消费', '高频消费', '极高频消费'],
    consumerCounts: [
      Math.floor(Math.random() * 500) + 1000,
      Math.floor(Math.random() * 500) + 800,
      Math.floor(Math.random() * 300) + 600,
      Math.floor(Math.random() * 200) + 300,
      Math.floor(Math.random() * 100) + 100
    ],
    purchaseAmounts: [
      Math.floor(Math.random() * 10) + 5,
      Math.floor(Math.random() * 10) + 15,
      Math.floor(Math.random() * 10) + 25,
      Math.floor(Math.random() * 15) + 35,
      Math.floor(Math.random() * 20) + 50
    ],
    percentages: [
      Math.floor(Math.random() * 10) + 10,
      Math.floor(Math.random() * 10) + 20,
      Math.floor(Math.random() * 10) + 30,
      Math.floor(Math.random() * 10) + 50,
      Math.floor(Math.random() * 10) + 80
    ]
  };
  
  // 消费者忠诚度分析数据
  const loyalty = [
    { value: Math.floor(Math.random() * 500) + 2000, name: '普通顾客' },
    { value: Math.floor(Math.random() * 300) + 1000, name: '忠实顾客' },
    { value: Math.floor(Math.random() * 200) + 500, name: '铜牌会员' },
    { value: Math.floor(Math.random() * 150) + 300, name: '银牌会员' },
    { value: Math.floor(Math.random() * 100) + 100, name: '金牌会员' }
  ];
  
  return {
    metrics: metrics,
    charts: {
      consumerPortrait: consumerPortrait,
      ageDistribution: ageDistribution,
      occupation: occupation,
      purchaseFrequency: purchaseFrequency,
      loyalty: loyalty
    }
  };
}

// 格式化数字，添加千位分隔符
function formatNumber(num) {
  return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
} 