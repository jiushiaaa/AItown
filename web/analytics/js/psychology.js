// 消费心理分析页面脚本
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
  document.getElementById('refreshMotiveBtn').addEventListener('click', function() {
    const activeTimeRange = document.querySelector('.filter-option.active').getAttribute('data-value');
    loadData(activeTimeRange);
  });
  
  document.getElementById('refreshDecisionBtn').addEventListener('click', function() {
    const activeTimeRange = document.querySelector('.filter-option.active').getAttribute('data-value');
    loadData(activeTimeRange);
  });
  
  document.getElementById('refreshEmotionBtn').addEventListener('click', function() {
    const activeTimeRange = document.querySelector('.filter-option.active').getAttribute('data-value');
    loadData(activeTimeRange);
  });
  
  document.getElementById('refreshNeedsBtn').addEventListener('click', function() {
    const activeTimeRange = document.querySelector('.filter-option.active').getAttribute('data-value');
    loadData(activeTimeRange);
  });
  
  document.getElementById('refreshValueBtn').addEventListener('click', function() {
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
  renderEmptyConsumptionMotiveChart();
  renderEmptyDecisionFactorChart();
  renderEmptyEmotionAnalysisChart();
  renderEmptyEmotionalNeedsChart();
  renderEmptyValueAnalysisChart();
  
  // 清空指标显示
  clearMetrics();
}

// 清空指标显示
function clearMetrics() {
  document.getElementById('qualitySatisfaction').textContent = '--';
  document.getElementById('priceSatisfaction').textContent = '--';
  document.getElementById('brandLoyalty').textContent = '--';
  document.getElementById('recommendIntention').textContent = '--';
  
  document.getElementById('qualitySatisfactionTrend').textContent = '--';
  document.getElementById('priceSatisfactionTrend').textContent = '--';
  document.getElementById('brandLoyaltyTrend').textContent = '--';
  document.getElementById('recommendIntentionTrend').textContent = '--';
}

// 渲染空白消费动机分析图表
function renderEmptyConsumptionMotiveChart() {
  const chartDom = document.getElementById('consumptionMotiveChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['男性消费者', '女性消费者', '平均值']
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
        name: '男性消费者',
        type: 'bar',
        data: []
      },
      {
        name: '女性消费者',
        type: 'bar',
        data: []
      },
      {
        name: '平均值',
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

// 渲染空白购买决策因素图表
function renderEmptyDecisionFactorChart() {
  const chartDom = document.getElementById('decisionFactorChart');
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
        name: '决策因素',
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

// 渲染空白消费情绪分析图表
function renderEmptyEmotionAnalysisChart() {
  const chartDom = document.getElementById('emotionAnalysisChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      bottom: '2%',
      left: 'center',
      data: []
    },
    series: [
      {
        name: '消费情绪',
        type: 'pie',
        radius: '65%',
        center: ['50%', '45%'],
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

// 渲染空白情感需求满足度图表
function renderEmptyEmotionalNeedsChart() {
  const chartDom = document.getElementById('emotionalNeedsChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['满足度', '重要性']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: []
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '满足度',
        type: 'bar',
        barWidth: '30%',
        data: []
      },
      {
        name: '重要性',
        type: 'line',
        smooth: true,
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

// 渲染空白消费价值观分析图表
function renderEmptyValueAnalysisChart() {
  const chartDom = document.getElementById('valueAnalysisChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'item'
    },
    radar: {
      indicator: [
        { name: '健康至上', max: 100 },
        { name: '品质优先', max: 100 },
        { name: '注重体验', max: 100 },
        { name: '价值导向', max: 100 },
        { name: '社会责任', max: 100 },
        { name: '文化传承', max: 100 },
        { name: '情感价值', max: 100 },
        { name: '个性表达', max: 100 }
      ],
      radius: 130
    },
    series: [
      {
        name: '消费价值观',
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
    const data = await fetchPsychologyData(timeRange);
    
    // 更新消费心理概览指标
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

// 从API获取消费心理分析数据
async function fetchPsychologyData(timeRange) {
  try {
    // 发送API请求获取数据
    const response = await http.get('/api/psychology-analysis', { timeRange });
    return response.data;
  } catch (error) {
    console.error('API请求失败:', error);
    // 返回模拟数据
    return generateMockData(timeRange);
  }
}

// 更新消费心理概览指标
function updateMetrics(metrics) {
  // 更新品质满意度
  document.getElementById('qualitySatisfaction').textContent = metrics.qualitySatisfaction;
  document.getElementById('qualitySatisfactionTrend').textContent = metrics.qualitySatisfactionTrend;
  updateTrendStyle('qualitySatisfactionTrend', metrics.qualitySatisfactionTrend);
  
  // 更新价格满意度
  document.getElementById('priceSatisfaction').textContent = metrics.priceSatisfaction;
  document.getElementById('priceSatisfactionTrend').textContent = metrics.priceSatisfactionTrend;
  updateTrendStyle('priceSatisfactionTrend', metrics.priceSatisfactionTrend);
  
  // 更新品牌忠诚度
  document.getElementById('brandLoyalty').textContent = metrics.brandLoyalty;
  document.getElementById('brandLoyaltyTrend').textContent = metrics.brandLoyaltyTrend;
  updateTrendStyle('brandLoyaltyTrend', metrics.brandLoyaltyTrend);
  
  // 更新推荐意愿度
  document.getElementById('recommendIntention').textContent = metrics.recommendIntention;
  document.getElementById('recommendIntentionTrend').textContent = Math.abs(metrics.recommendIntentionTrend);
  updateTrendStyle('recommendIntentionTrend', metrics.recommendIntentionTrend);
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
  // 消费动机分析
  renderConsumptionMotiveChart(chartsData.consumptionMotive);
  
  // 购买决策因素
  renderDecisionFactorChart(chartsData.decisionFactor);
  
  // 消费情绪分析
  renderEmotionAnalysisChart(chartsData.emotionAnalysis);
  
  // 情感需求满足度
  renderEmotionalNeedsChart(chartsData.emotionalNeeds);
  
  // 消费价值观分析
  renderValueAnalysisChart(chartsData.valueAnalysis);
}

// 渲染消费动机分析图表
function renderConsumptionMotiveChart(motiveData) {
  const chartDom = document.getElementById('consumptionMotiveChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['男性消费者', '女性消费者', '平均值']
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
      data: motiveData.categories
    },
    series: [
      {
        name: '男性消费者',
        type: 'bar',
        data: motiveData.male,
        itemStyle: {
          color: '#5470c6'
        }
      },
      {
        name: '女性消费者',
        type: 'bar',
        data: motiveData.female,
        itemStyle: {
          color: '#ee6666'
        }
      },
      {
        name: '平均值',
        type: 'bar',
        data: motiveData.average,
        itemStyle: {
          color: '#91cc75'
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

// 渲染购买决策因素图表
function renderDecisionFactorChart(factorData) {
  const chartDom = document.getElementById('decisionFactorChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}% ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center',
      data: factorData.map(item => item.name)
    },
    series: [
      {
        name: '决策因素',
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
        data: factorData
      }
    ]
  };
  
  myChart.setOption(option);
  
  // 窗口大小变化时自动调整图表大小
  window.addEventListener('resize', function() {
    myChart.resize();
  });
}

// 渲染消费情绪分析图表
function renderEmotionAnalysisChart(emotionData) {
  const chartDom = document.getElementById('emotionAnalysisChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}% ({d}%)'
    },
    legend: {
      bottom: '2%',
      left: 'center',
      data: emotionData.map(item => item.name)
    },
    series: [
      {
        name: '消费情绪',
        type: 'pie',
        radius: '65%',
        center: ['50%', '45%'],
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        data: emotionData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          formatter: '{b}: {c}%'
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

// 渲染情感需求满足度图表
function renderEmotionalNeedsChart(needsData) {
  const chartDom = document.getElementById('emotionalNeedsChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['满足度', '重要性']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: needsData.categories
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '满足度',
        type: 'bar',
        barWidth: '30%',
        data: needsData.satisfaction,
        itemStyle: {
          color: '#5470c6'
        }
      },
      {
        name: '重要性',
        type: 'line',
        smooth: true,
        data: needsData.importance,
        symbolSize: 8,
        itemStyle: {
          color: '#ee6666'
        },
        lineStyle: {
          width: 3
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

// 渲染消费价值观分析图表
function renderValueAnalysisChart(valueData) {
  const chartDom = document.getElementById('valueAnalysisChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'item'
    },
    radar: {
      indicator: valueData.indicators,
      radius: 130
    },
    series: [
      {
        name: '消费价值观',
        type: 'radar',
        data: [
          {
            value: valueData.values,
            name: '消费者价值观特征',
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
  
  // 更新消费心理概览指标
  updateMetrics(mockData.metrics);
  
  // 更新图表
  updateCharts(mockData.charts);
}

// 生成模拟数据
function generateMockData(timeRange) {
  // 消费心理概览指标模拟数据
  const metrics = {
    qualitySatisfaction: (Math.random() * 10 + 85).toFixed(1),
    qualitySatisfactionTrend: (Math.random() * 8).toFixed(1),
    priceSatisfaction: (Math.random() * 15 + 75).toFixed(1),
    priceSatisfactionTrend: (Math.random() * 5).toFixed(1),
    brandLoyalty: (Math.random() * 10 + 80).toFixed(1),
    brandLoyaltyTrend: (Math.random() * 6).toFixed(1),
    recommendIntention: (Math.random() * 10 + 75).toFixed(1),
    recommendIntentionTrend: -((Math.random() * 3).toFixed(1))
  };
  
  // 消费动机分析数据
  const consumptionMotiveData = {
    categories: ['健康养生需求', '品质追求需求', '社交礼仪需求', '收藏投资需求', '情感寄托需求', '身份象征需求'],
    male: [
      Math.floor(Math.random() * 10) + 75,
      Math.floor(Math.random() * 15) + 80,
      Math.floor(Math.random() * 20) + 60,
      Math.floor(Math.random() * 15) + 70,
      Math.floor(Math.random() * 20) + 40,
      Math.floor(Math.random() * 20) + 65
    ],
    female: [
      Math.floor(Math.random() * 15) + 80,
      Math.floor(Math.random() * 10) + 75,
      Math.floor(Math.random() * 15) + 70,
      Math.floor(Math.random() * 20) + 55,
      Math.floor(Math.random() * 15) + 65,
      Math.floor(Math.random() * 15) + 60
    ],
    average: [
      Math.floor(Math.random() * 8) + 78,
      Math.floor(Math.random() * 8) + 78,
      Math.floor(Math.random() * 10) + 65,
      Math.floor(Math.random() * 10) + 65,
      Math.floor(Math.random() * 10) + 55,
      Math.floor(Math.random() * 10) + 65
    ]
  };
  
  // 购买决策因素数据
  const decisionFactorData = [
    { value: Math.floor(Math.random() * 10) + 30, name: '品质' },
    { value: Math.floor(Math.random() * 8) + 20, name: '价格' },
    { value: Math.floor(Math.random() * 5) + 15, name: '品牌' },
    { value: Math.floor(Math.random() * 5) + 10, name: '口感' },
    { value: Math.floor(Math.random() * 5) + 5, name: '包装' },
    { value: Math.floor(Math.random() * 3) + 5, name: '健康功效' },
    { value: Math.floor(Math.random() * 3) + 3, name: '其他' }
  ];
  
  // 消费情绪分析数据
  const emotionAnalysisData = [
    { value: Math.floor(Math.random() * 10) + 40, name: '满足感' },
    { value: Math.floor(Math.random() * 10) + 20, name: '愉悦感' },
    { value: Math.floor(Math.random() * 5) + 15, name: '成就感' },
    { value: Math.floor(Math.random() * 5) + 10, name: '安心感' },
    { value: Math.floor(Math.random() * 5) + 5, name: '其他' }
  ];
  
  // 情感需求满足度数据
  const emotionalNeedsData = {
    categories: ['社交需求', '自我实现', '尊重需求', '审美需求', '归属感', '安全感'],
    satisfaction: [
      Math.floor(Math.random() * 15) + 70,
      Math.floor(Math.random() * 15) + 65,
      Math.floor(Math.random() * 15) + 75,
      Math.floor(Math.random() * 15) + 80,
      Math.floor(Math.random() * 15) + 60,
      Math.floor(Math.random() * 15) + 75
    ],
    importance: [
      Math.floor(Math.random() * 10) + 75,
      Math.floor(Math.random() * 10) + 70,
      Math.floor(Math.random() * 10) + 80,
      Math.floor(Math.random() * 10) + 85,
      Math.floor(Math.random() * 10) + 65,
      Math.floor(Math.random() * 10) + 80
    ]
  };
  
  // 消费价值观分析数据
  const valueAnalysisData = {
    indicators: [
      { name: '健康至上', max: 100 },
      { name: '品质优先', max: 100 },
      { name: '注重体验', max: 100 },
      { name: '价值导向', max: 100 },
      { name: '社会责任', max: 100 },
      { name: '文化传承', max: 100 },
      { name: '情感价值', max: 100 },
      { name: '个性表达', max: 100 }
    ],
    values: [
      Math.floor(Math.random() * 15) + 75,
      Math.floor(Math.random() * 10) + 85,
      Math.floor(Math.random() * 15) + 70,
      Math.floor(Math.random() * 15) + 75,
      Math.floor(Math.random() * 20) + 60,
      Math.floor(Math.random() * 15) + 75,
      Math.floor(Math.random() * 15) + 70,
      Math.floor(Math.random() * 15) + 65
    ]
  };
  
  return {
    metrics: metrics,
    charts: {
      consumptionMotive: consumptionMotiveData,
      decisionFactor: decisionFactorData,
      emotionAnalysis: emotionAnalysisData,
      emotionalNeeds: emotionalNeedsData,
      valueAnalysis: valueAnalysisData
    }
  };
} 