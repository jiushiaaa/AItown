// 地域分析页面脚本
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
  document.getElementById('refreshMapBtn').addEventListener('click', function() {
    const activeTimeRange = document.querySelector('.filter-option.active').getAttribute('data-value');
    loadData(activeTimeRange);
  });
  
  document.getElementById('refreshCityRankBtn').addEventListener('click', function() {
    const activeTimeRange = document.querySelector('.filter-option.active').getAttribute('data-value');
    loadData(activeTimeRange);
  });
  
  document.getElementById('refreshRegionTrendBtn').addEventListener('click', function() {
    const activeTimeRange = document.querySelector('.filter-option.active').getAttribute('data-value');
    loadData(activeTimeRange);
  });
  
  document.getElementById('refreshRegionCompareBtn').addEventListener('click', function() {
    const activeTimeRange = document.querySelector('.filter-option.active').getAttribute('data-value');
    loadData(activeTimeRange);
  });
  
  document.getElementById('refreshCityFeatureBtn').addEventListener('click', function() {
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
  renderEmptyRegionMapChart();
  renderEmptyCityRankChart();
  renderEmptyRegionTrendChart();
  renderEmptyRegionCompareChart();
  renderEmptyCityFeatureChart();
  
  // 清空指标显示
  clearMetrics();
}

// 清空指标显示
function clearMetrics() {
  document.getElementById('provinceCount').textContent = '--';
  document.getElementById('cityCount').textContent = '--';
  document.getElementById('avgRegionRate').textContent = '--';
  document.getElementById('regionGrowth').textContent = '--';
  
  document.getElementById('provinceTrend').textContent = '--';
  document.getElementById('cityTrend').textContent = '--';
  document.getElementById('avgRegionTrend').textContent = '--';
  document.getElementById('regionGrowthTrend').textContent = '--';
}

// 渲染空白地域销售分布地图
function renderEmptyRegionMapChart() {
  console.log('渲染空白地域销售分布地图');
  // 使用map-utils.js中的函数渲染空地图
  renderChinaMap('regionMapChart', [], {
    title: {
      text: '地域销售分布',
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
    console.log('空白地域销售分布地图渲染完成');
  }).catch(error => {
    console.error('空白地域销售分布地图渲染失败:', error);
  });
}

// 将函数暴露到全局作用域，以便于地图加载失败时重新调用
window.renderEmptyRegionMapChart = renderEmptyRegionMapChart;

// 渲染空白城市销售排名图表
function renderEmptyCityRankChart() {
  const chartDom = document.getElementById('cityRankChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}万元'
      }
    },
    yAxis: {
      type: 'category',
      data: [],
      axisTick: {
        alignWithLabel: true
      }
    },
    series: [
      {
        name: '销售额',
        type: 'bar',
        barWidth: '60%',
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

// 渲染空白地域销售趋势图表
function renderEmptyRegionTrendChart() {
  const chartDom = document.getElementById('regionTrendChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: []
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
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}万元'
      }
    },
    series: []
  };
  
  myChart.setOption(option);
  
  // 窗口大小变化时自动调整图表大小
  window.addEventListener('resize', function() {
    myChart.resize();
  });
}

// 渲染空白区域消费力对比图表
function renderEmptyRegionCompareChart() {
  // 使用map-utils.js中的函数渲染空热力地图
  renderHeatMap('regionCompareChart', [], {
    title: {
      text: '区域消费力指数',
      left: 'center'
    },
    showLabel: false // 不显示省份名称
  }).then(chart => {
    console.log('空白区域消费力对比图渲染完成');
  }).catch(error => {
    console.error('空白区域消费力对比图渲染失败:', error);
  });
}

// 渲染空白城市消费特征分析图表
function renderEmptyCityFeatureChart() {
  // 使用map-utils.js中的函数渲染空地图和飞线
  const pointsData = [];
  const linesData = [];
  
  renderMapWithPointsAndLines('cityFeatureChart', pointsData, linesData, {
    title: {
      text: '城市消费特征分析',
      left: 'center'
    },
    showLabel: false // 不显示省份名称
  }).then(chart => {
    console.log('空白城市消费特征分析图表渲染完成');
  }).catch(error => {
    console.error('空白城市消费特征分析图表渲染失败:', error);
  });
}

// 加载指定时间范围的数据
async function loadData(timeRange) {
  try {
    // 显示加载状态
    showLoading();
    
    // 获取数据
    const data = await fetchRegionData(timeRange);
    
    // 更新地域销售概览指标
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

// 从API获取地域分析数据
async function fetchRegionData(timeRange) {
  try {
    // 发送API请求获取数据
    const response = await http.get('/api/region-analysis', { timeRange });
    return response.data;
  } catch (error) {
    console.error('API请求失败:', error);
    // 返回模拟数据
    return generateMockData(timeRange);
  }
}

// 更新地域销售概览指标
function updateMetrics(metrics) {
  // 更新覆盖省份
  document.getElementById('provinceCount').textContent = metrics.provinceCount;
  document.getElementById('provinceTrend').textContent = metrics.provinceTrend;
  updateTrendStyle('provinceTrend', metrics.provinceTrend);
  
  // 更新覆盖城市
  document.getElementById('cityCount').textContent = metrics.cityCount;
  document.getElementById('cityTrend').textContent = metrics.cityTrend;
  updateTrendStyle('cityTrend', metrics.cityTrend);
  
  // 更新平均区域转化率
  document.getElementById('avgRegionRate').textContent = metrics.avgRegionRate;
  document.getElementById('avgRegionTrend').textContent = metrics.avgRegionTrend;
  updateTrendStyle('avgRegionTrend', metrics.avgRegionTrend);
  
  // 更新区域增长率
  document.getElementById('regionGrowth').textContent = metrics.regionGrowth;
  document.getElementById('regionGrowthTrend').textContent = Math.abs(metrics.regionGrowthTrend);
  updateTrendStyle('regionGrowthTrend', metrics.regionGrowthTrend);
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
  // 地域销售分布地图
  renderRegionMapChart(chartsData.regionMap);
  
  // 城市销售排名
  renderCityRankChart(chartsData.cityRank);
  
  // 地域销售趋势
  renderRegionTrendChart(chartsData.regionTrend);
  
  // 区域消费力对比
  renderRegionCompareChart(chartsData.regionCompare);
  
  // 城市消费特征分析
  renderCityFeatureChart(chartsData.cityFeature);
}

// 渲染地域销售分布地图
function renderRegionMapChart(mapData) {
  console.log('渲染地域销售分布数据', mapData);
  
  // 创建省份名称映射表，解决名称不匹配问题
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
  
  // 创建反向映射，用于工具提示中查找数据
  const reverseProvinceNameMap = {};
  Object.keys(provinceNameMap).forEach(shortName => {
    reverseProvinceNameMap[provinceNameMap[shortName]] = shortName;
  });
  
  // 处理数据，确保省份名称匹配
  const processedMapData = Array.isArray(mapData) ? mapData.map(item => {
    if (!item) return null;
    
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
  }) : [];
  
  // 使用map-utils.js中的函数渲染地图
  renderChinaMap('regionMapChart', processedMapData, {
    title: {
      text: '地域销售分布',
      left: 'center',
    },
    seriesName: '区域销售',
    tooltipFormatter: function(params) {
      console.log('地域销售分布tooltip参数:', params);
      
      // 根据地图显示的省份名称找出对应的原始数据名称
      const shortName = reverseProvinceNameMap[params.name] || params.name;
      
      // 找到对应的原始数据项
      const originalDataItem = mapData.find(item => item && item.name === shortName);
      
      // 强制获取正确的销售额值
      let value = 0;
      try {
        if (originalDataItem && typeof originalDataItem.value === 'number') {
          // 首选从原始数据中获取
          value = originalDataItem.value;
          console.log(`找到原始数据: ${shortName}, 值: ${value}`);
        } else if (params.data && typeof params.data.value === 'number') {
          // 其次从data对象中获取
          value = params.data.value;
          console.log(`从params.data.value获取值: ${value}`);
        } else if (typeof params.value === 'number') {
          // 再次从value属性获取
          value = params.value;
          console.log(`从params.value获取值: ${value}`);
        } else if (Array.isArray(params.value) && params.value.length > 0) {
          // 处理数组情况
          value = params.value[params.value.length - 1];
          console.log(`从params.value数组获取值: ${value}`);
        } else {
          console.log(`未找到${params.name}(${shortName})的有效数据，使用默认值0`);
        }
      } catch (e) {
        console.error('获取值时出错:', e);
      }
      
      // 确保是数字类型
      value = isNaN(Number(value)) ? 0 : Number(value);
      
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
    console.log('地域销售分布地图渲染完成');
  }).catch(error => {
    console.error('地域销售分布地图渲染失败:', error);
  });
}

// 渲染城市销售排名图表
function renderCityRankChart(rankData) {
  const chartDom = document.getElementById('cityRankChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}万元'
      }
    },
    yAxis: {
      type: 'category',
      data: rankData.cities,
      axisTick: {
        alignWithLabel: true
      }
    },
    series: [
      {
        name: '销售额',
        type: 'bar',
        barWidth: '60%',
        data: rankData.values,
        itemStyle: {
          color: function(params) {
            // 给不同排名的城市设置不同的颜色
            const colorList = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc'];
            return colorList[params.dataIndex % colorList.length];
          }
        },
        label: {
          show: true,
          position: 'right',
          formatter: '{c}万元'
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

// 渲染地域销售趋势图表
function renderRegionTrendChart(trendData) {
  const chartDom = document.getElementById('regionTrendChart');
  const myChart = echarts.init(chartDom);
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: trendData.regions
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
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}万元'
      }
    },
    series: trendData.regions.map((region, index) => {
      return {
        name: region,
        type: 'line',
        stack: '总量',
        areaStyle: {},
        emphasis: {
          focus: 'series'
        },
        data: trendData.values[index]
      };
    })
  };
  
  myChart.setOption(option);
  
  // 窗口大小变化时自动调整图表大小
  window.addEventListener('resize', function() {
    myChart.resize();
  });
}

// 渲染区域消费力对比图表
function renderRegionCompareChart(compareData) {
  // 将数据转换为热力图格式
  const heatmapData = [];
  
  // 计算最大值，用于可视化比例
  let maxValue = 0;
  for (let i = 0; i < compareData.regions.length; i++) {
    // 使用三个指标的平均值作为热力图的值
    const avgValue = (compareData.avgPrice[i] + compareData.frequency[i] + compareData.consumers[i]) / 3;
    if (avgValue > maxValue) {
      maxValue = avgValue;
    }
    
    // 根据省份名称查找对应的坐标
    // 这里使用一个常见省份的坐标映射表
    const coordinates = getProvinceCoordinates(compareData.regions[i]);
    if (coordinates) {
      heatmapData.push({
        name: compareData.regions[i],
        value: [...coordinates, avgValue],
        // 自定义数据，用于tooltip展示
        customData: {
          avgPrice: compareData.avgPrice[i],
          frequency: compareData.frequency[i],
          consumers: compareData.consumers[i]
        }
      });
    }
  }
  
  // 使用map-utils.js中的函数渲染热力地图
  renderHeatMap('regionCompareChart', heatmapData, {
    title: {
      text: '区域消费力指数',
      left: 'center'
    },
    showLabel: false, // 不显示省份名称
    tooltip: {
      formatter: function(params) {
        return `${params.name}<br/>
                客单价指数: ${params.data.customData.avgPrice}<br/>
                购买频次指数: ${params.data.customData.frequency}<br/>
                消费者数量指数: ${params.data.customData.consumers}<br/>
                综合指数: ${Math.round(params.value[2])}`;
      }
    },
    maxValue: maxValue,
    visualMap: {
      min: 0,
      max: maxValue,
      calculable: true,
      inRange: {
        color: ['#50a3ba', '#eac736', '#d94e5d']
      },
      textStyle: {
        color: '#333'
      }
    }
  }).then(chart => {
    console.log('区域消费力对比图渲染完成');
  }).catch(error => {
    console.error('区域消费力对比图渲染失败:', error);
  });
}

// 获取省份坐标
function getProvinceCoordinates(province) {
  // 省份名称标准化映射
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
  
  // 标准化省份名称
  const standardizedProvince = provinceNameMap[province] || province;
  
  // 省份坐标映射表
  const coordinatesMap = {
    '北京市': [116.405285, 39.904989],
    '天津市': [117.190182, 39.125596],
    '河北省': [114.502461, 38.045474],
    '山西省': [112.549248, 37.857014],
    '内蒙古自治区': [111.670801, 40.818311],
    '辽宁省': [123.429096, 41.796767],
    '吉林省': [125.3245, 43.886841],
    '黑龙江省': [126.642464, 45.756967],
    '上海市': [121.472644, 31.231706],
    '江苏省': [118.767413, 32.041544],
    '浙江省': [120.153576, 30.287459],
    '安徽省': [117.283042, 31.86119],
    '福建省': [119.306239, 26.075302],
    '江西省': [115.892151, 28.676493],
    '山东省': [117.000923, 36.675807],
    '河南省': [113.665412, 34.757975],
    '湖北省': [114.298572, 30.584355],
    '湖南省': [112.982279, 28.19409],
    '广东省': [113.280637, 23.125178],
    '广西壮族自治区': [108.320004, 22.82402],
    '海南省': [110.33119, 20.031971],
    '重庆市': [106.504962, 29.533155],
    '四川省': [104.065735, 30.659462],
    '贵州省': [106.713478, 26.578343],
    '云南省': [102.712251, 25.040609],
    '西藏自治区': [91.132212, 29.660361],
    '陕西省': [108.948024, 34.263161],
    '甘肃省': [103.823557, 36.058039],
    '青海省': [101.778916, 36.623178],
    '宁夏回族自治区': [106.278179, 38.46637],
    '新疆维吾尔自治区': [87.617733, 43.792818],
    '香港特别行政区': [114.173355, 22.320048],
    '澳门特别行政区': [113.54909, 22.198951],
    '台湾省': [121.509062, 25.044332],
    // 区域坐标
    '华东': [119.5, 31.5],
    '华南': [112.5, 23.0],
    '华北': [115.0, 39.0],
    '华中': [113.0, 31.0],
    '西南': [104.0, 28.0],
    '西北': [101.0, 36.0],
    '东北': [125.0, 43.0]
  };
  
  // 返回省份坐标
  return coordinatesMap[standardizedProvince];
}

// 渲染城市消费特征分析图表
function renderCityFeatureChart(featureData) {
  // 构造地图散点数据
  const pointsData = [];
  const linesData = [];
  
  // 城市坐标映射表
  const cityCoordinates = {
    '北京': [116.405285, 39.904989],
    '上海': [121.472644, 31.231706],
    '广州': [113.280637, 23.125178],
    '深圳': [114.085947, 22.547],
    '杭州': [120.153576, 30.287459],
    '南京': [118.767413, 32.041544],
    '武汉': [114.298572, 30.584355],
    '成都': [104.065735, 30.659462],
    '重庆': [106.504962, 29.533155],
    '西安': [108.948024, 34.263161],
    '厦门': [118.11022, 24.490474],
    '福州': [119.306239, 26.075302],
    '天津': [117.190182, 39.125596],
    '青岛': [120.383428, 36.105215],
    '苏州': [120.619585, 31.299379],
    '长沙': [112.982279, 28.19409]
  };
  
  // 计算各城市特征的平均值（用于表示散点大小）
  featureData.forEach(item => {
    const city = item.city;
    const coordinates = cityCoordinates[city];
    
    if (coordinates) {
      // 计算特征的平均值，用于确定散点大小
      const avgFeature = item.values.reduce((sum, val) => sum + val, 0) / item.values.length;
      
      // 添加到散点数据
      pointsData.push({
        name: city,
        value: [...coordinates, avgFeature],
        symbolSize: avgFeature / 10,  // 调整大小比例
        itemStyle: {
          color: `rgba(${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, ${Math.floor(Math.random() * 255)}, 0.8)`
        }
      });
      
      // 添加从北京到该城市的飞线
      if (city !== '北京') {
        linesData.push({
          coords: [
            cityCoordinates['北京'],
            coordinates
          ],
          lineStyle: {
            width: avgFeature / 30,  // 调整线宽比例
            curveness: 0.2
          }
        });
      }
    }
  });
  
  // 使用map-utils.js中的函数渲染地图和飞线
  renderMapWithPointsAndLines('cityFeatureChart', pointsData, linesData, {
    title: {
      text: '城市消费特征分析',
      left: 'center'
    },
    showLabel: false, // 不显示省份名称
    tooltip: {
      formatter: function(params) {
        if (params.seriesType === 'effectScatter') {
          // 找到对应的城市数据
          const cityData = featureData.find(item => item.city === params.name);
          if (cityData) {
            return `${params.name}<br/>
                    品质关注度: ${cityData.values[0]}<br/>
                    价格敏感性: ${cityData.values[1]}<br/>
                    品牌忠诚度: ${cityData.values[2]}<br/>
                    消费频率: ${cityData.values[3]}<br/>
                    购买力: ${cityData.values[4]}<br/>
                    综合指数: ${Math.round(params.value[2])}`;
          }
        }
        return params.name;
      }
    }
  }).then(chart => {
    console.log('城市消费特征分析图表渲染完成');
  }).catch(error => {
    console.error('城市消费特征分析图表渲染失败:', error);
  });
}

// 加载模拟数据
function loadMockData() {
  console.log('加载模拟数据');
  // 生成模拟数据
  const mockData = generateMockData('7days');
  
  // 确保地图数据中的值都是数字类型
  if (mockData.charts && mockData.charts.regionMap) {
    mockData.charts.regionMap.forEach(item => {
      if (typeof item.value !== 'number') {
        console.warn(`修正${item.name}的值类型，从${typeof item.value}改为number`);
        item.value = Number(item.value) || 0;
      }
    });
  }
  
  console.log('模拟数据:', JSON.stringify(mockData.charts.regionMap));
  
  // 更新地域销售概览指标
  updateMetrics(mockData.metrics);
  
  // 更新图表
  updateCharts(mockData.charts);
}

// 生成模拟数据
function generateMockData(timeRange) {
  // 地域销售概览指标模拟数据
  const metrics = {
    provinceCount: Math.floor(Math.random() * 10) + 25,
    provinceTrend: (Math.random() * 10).toFixed(1),
    cityCount: Math.floor(Math.random() * 50) + 150,
    cityTrend: (Math.random() * 15).toFixed(1),
    avgRegionRate: (Math.random() * 20 + 30).toFixed(1),
    avgRegionTrend: (Math.random() * 8).toFixed(1),
    regionGrowth: (Math.random() * 10 + 5).toFixed(1),
    regionGrowthTrend: -((Math.random() * 3).toFixed(1))
  };
  
  // 生成省份数据
  const provinces = [
    '北京', '天津', '上海', '重庆', '河北', '山西', '辽宁', '吉林', '黑龙江',
    '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南',
    '广东', '广西', '海南', '四川', '贵州', '云南', '西藏', '陕西', '甘肃',
    '青海', '宁夏', '新疆'
  ];
  
  // 地域销售分布地图数据
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
  
  // 城市销售排名数据
  const cities = ['杭州', '北京', '上海', '广州', '深圳', '武汉', '成都', '南京', '福州', '厦门'];
  const cityValues = [];
  
  for (let i = 0; i < cities.length; i++) {
    cityValues.push(Math.floor(Math.random() * 80) + 20);
  }
  
  // 按销售额排序
  const cityRankData = {
    cities: [],
    values: []
  };
  
  const cityValuePairs = cities.map((city, index) => ({ city, value: cityValues[index] }));
  cityValuePairs.sort((a, b) => b.value - a.value);
  
  cityRankData.cities = cityValuePairs.map(pair => pair.city);
  cityRankData.values = cityValuePairs.map(pair => pair.value);
  
  // 地域销售趋势数据
  const regions = ['华东', '华南', '华北', '西南', '华中'];
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
      for (let i = days - 1; i >= 0; i -= 3) {
        const date = new Date(today);
        date.setDate(today.getDate() - i);
        dates.push(`${date.getMonth() + 1}/${date.getDate()}`);
      }
      break;
    case '90days':
      days = 90;
      for (let i = days - 1; i >= 0; i -= 9) {
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
  
  const regionValues = [];
  
  for (let i = 0; i < regions.length; i++) {
    const regionData = [];
    for (let j = 0; j < dates.length; j++) {
      regionData.push(Math.floor(Math.random() * 50) + 10);
    }
    regionValues.push(regionData);
  }
  
  // 区域消费力对比数据
  const compareRegions = ['华东', '华南', '华北', '西南', '华中', '东北', '西北'];
  const avgPrice = [];
  const frequency = [];
  const consumers = [];
  
  for (let i = 0; i < compareRegions.length; i++) {
    avgPrice.push(Math.floor(Math.random() * 40) + 60);
    frequency.push(Math.floor(Math.random() * 30) + 40);
    consumers.push(Math.floor(Math.random() * 50) + 30);
  }
  
  // 城市消费特征分析数据
  const featureCities = ['杭州', '北京', '上海', '广州', '深圳'];
  const cityFeatures = [];
  
  for (let i = 0; i < featureCities.length; i++) {
    cityFeatures.push({
      city: featureCities[i],
      values: [
        Math.floor(Math.random() * 20) + 80, // 品质关注度
        Math.floor(Math.random() * 30) + 50, // 价格敏感性
        Math.floor(Math.random() * 25) + 60, // 品牌忠诚度
        Math.floor(Math.random() * 20) + 70, // 消费频率
        Math.floor(Math.random() * 25) + 65  // 购买力
      ]
    });
  }
  
  return {
    metrics: metrics,
    charts: {
      regionMap: regionMap,
      cityRank: cityRankData,
      regionTrend: {
        regions: regions,
        dates: dates,
        values: regionValues
      },
      regionCompare: {
        regions: compareRegions,
        avgPrice: avgPrice,
        frequency: frequency,
        consumers: consumers
      },
      cityFeature: cityFeatures
    }
  };
}

// 模拟加载区域消费力对比数据
function loadRegionCompareData() {
  // 返回模拟数据，使用标准省份全名
  return {
    regions: ['北京市', '上海市', '广东省', '浙江省', '江苏省', '四川省', '湖北省', '山东省'],
    avgPrice: [90, 85, 80, 75, 78, 65, 60, 70],
    frequency: [80, 85, 70, 75, 65, 60, 65, 55],
    consumers: [95, 90, 85, 75, 70, 60, 55, 65]
  };
}

// 模拟加载城市消费特征数据
function loadCityFeatureData() {
  // 返回模拟数据
  return [
    { city: '北京', values: [85, 60, 90, 75, 95] },
    { city: '上海', values: [80, 65, 85, 80, 90] },
    { city: '广州', values: [75, 70, 75, 65, 80] },
    { city: '深圳', values: [70, 75, 70, 70, 85] },
    { city: '杭州', values: [75, 65, 80, 65, 75] },
    { city: '南京', values: [65, 60, 75, 60, 70] },
    { city: '武汉', values: [60, 65, 70, 55, 65] },
    { city: '成都', values: [70, 60, 65, 60, 70] },
    { city: '重庆', values: [65, 55, 60, 55, 65] },
    { city: '西安', values: [60, 60, 65, 50, 60] }
  ];
}

// 模拟加载区域销售数据
function loadRegionData() {
  // 返回模拟数据，使用标准省份全名
  return {
    mapData: [
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
    ],
    rankData: [
      { name: '北京市', value: 200 },
      { name: '上海市', value: 210 },
      { name: '广东省', value: 220 },
      { name: '浙江省', value: 190 },
      { name: '江苏省', value: 180 }
    ]
  };
} 