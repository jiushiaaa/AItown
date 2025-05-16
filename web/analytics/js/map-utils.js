/**
 * 地图可视化工具函数
 * 用于在数据概览和地域分析页面中显示中国地图
 */

// 初始化地图所需数据
let chinaMapData = null;

// 加载中国地图 GeoJSON 数据，增加重试机制
async function loadChinaMapData(retries = 3) {
  if (chinaMapData !== null) {
    return chinaMapData;
  }
  
  try {
    // 直接获取ECharts全局注册的地图
    console.log('检查已加载的地图数据');
    if (echarts.getMap('china')) {
      console.log('中国地图数据已加载');
      return {};
    } else {
      console.log('未找到中国地图数据，尝试从assets加载');
      
      // 尝试多种路径和重试机制
      const possiblePaths = [
        '../Assets/map.json',
        './Assets/map.json',
        '/Assets/map.json',
        '/web/Assets/map.json'
      ];
      
      let loadError = null;
      
      // 尝试每个路径
      for (const path of possiblePaths) {
        for (let i = 0; i < retries; i++) {
          try {
            console.log(`尝试从 ${path} 加载地图数据, 第 ${i+1} 次尝试`);
            const response = await fetch(path, {
              cache: 'force-cache', // 使用缓存减少加载时间
              timeout: 10000 // 设置10秒超时
            });
            
            if (response.ok) {
              chinaMapData = await response.json();
              console.log(`从 ${path} 成功加载地图数据`);
              // 注册地图数据
              echarts.registerMap('china', chinaMapData);
              return chinaMapData;
            }
          } catch (err) {
            console.warn(`从 ${path} 加载失败, 尝试次数 ${i+1}/${retries}:`, err);
            loadError = err;
            // 短暂延迟后重试
            await new Promise(resolve => setTimeout(resolve, 300));
          }
        }
      }
      
      // 所有路径尝试失败，抛出最后一个错误
      throw loadError || new Error('无法加载地图数据');
    }
  } catch (error) {
    console.error('检查地图数据失败:', error);
    
    // 尝试使用硬编码的初始化地图数据作为后备
    try {
      console.log('尝试使用内置测试数据初始化地图');
      // 如果有预定义的地图数据，可以在这里添加
      // 这里只是模拟一个简单的测试数据结构，实际项目中可能需要完整的数据
      const fallbackData = {"type":"FeatureCollection","features":[]};
      echarts.registerMap('china', fallbackData);
      return fallbackData;
    } catch (fallbackError) {
      console.error('内置数据初始化失败:', fallbackError);
      return null;
    }
  }
}

// 页面加载时预加载地图数据
document.addEventListener('DOMContentLoaded', function() {
  console.log('预加载地图数据');
  loadChinaMapData().catch(err => console.error('预加载地图数据失败:', err));
});

/**
 * 渲染中国地图
 * @param {string} containerId - 地图容器的DOM ID
 * @param {Array} data - 地图数据，格式为 [{name: '省份名', value: 数值}]
 * @param {Object} options - 配置选项
 */
async function renderChinaMap(containerId, data, options = {}) {
  console.log('初始化地图容器', containerId);
  const container = document.getElementById(containerId);
  if (!container) {
    console.error(`找不到容器: ${containerId}`);
    return;
  }
  
  // 显示加载中状态
  container.classList.add('loading');
  
  try {
    // 确保地图数据已加载
    await loadChinaMapData();
    
    // 创建地图实例
    const chart = echarts.init(container);
    console.log('地图实例创建成功');
    
    // 确保数据格式正确
    console.log('原始数据:', JSON.stringify(data));
    const processedData = Array.isArray(data) ? data.map(item => {
      // 确保每个数据项都有正确的格式和有效的数值
      if (!item) return { name: '', value: 0 };
      
      return {
        name: item.name || '',
        value: typeof item.value === 'number' && !isNaN(item.value) ? item.value : (parseInt(item.value) || 0),
        // 保留原始数据的其他属性
        ...(item.originalName ? { originalName: item.originalName } : {})
      };
    }) : [];
    console.log('处理后的数据:', JSON.stringify(processedData));
    
    // 检查地图数据中的省份是否都有对应的值
    try {
      const mapGeoData = echarts.getMap('china').geoJSON;
      if (mapGeoData && mapGeoData.features) {
        console.log(`地图包含 ${mapGeoData.features.length} 个地理特征`);
        
        // 获取地图中所有的省份名称
        const mapProvinceNames = mapGeoData.features.map(feature => 
          feature.properties && feature.properties.name || '未知'
        );
        
        console.log('地图省份:', mapProvinceNames.join(', '));
        
        // 检查数据中的省份是否都在地图中
        const dataProvinceNames = processedData.map(item => item.name);
        console.log('数据省份:', dataProvinceNames.join(', '));
        
        // 记录未匹配的省份
        const unmatchedProvinces = dataProvinceNames.filter(name => 
          !mapProvinceNames.includes(name)
        );
        if (unmatchedProvinces.length > 0) {
          console.warn('未匹配的省份:', unmatchedProvinces.join(', '));
        }
      }
    } catch (e) {
      console.error('检查省份匹配时出错:', e);
    }
    
    // 默认配置
    const defaultOptions = {
      title: {
        text: options.title || '',
        left: 'center',
        textStyle: {
          color: '#333',
          fontSize: 16
        }
      },
      tooltip: {
        trigger: 'item',
        formatter: options.tooltipFormatter || function(params) {
          // 调试输出参数结构
          console.log('地图tooltip参数类型:', typeof params);
          console.log('地图tooltip参数:', JSON.stringify(params, null, 2));
          
          // 强制从params.data中获取value
          let value = 0;
          try {
            if (params.data && params.data.value !== undefined) {
              value = params.data.value;
              console.log(`成功从params.data.value获取值: ${value}`);
            } else if (Array.isArray(params.value) && params.value.length > 0) {
              value = params.value[params.value.length - 1];
              console.log(`从params.value数组获取值: ${value}`);
            } else if (typeof params.value === 'number') {
              value = params.value;
              console.log(`从params.value获取值: ${value}`);
            } else {
              console.log('无法获取有效的值，使用默认值0');
            }
          } catch (e) {
            console.error('获取值时出错:', e);
          }
          
          return `${params.name}<br/>数值: ${value}`;
        }
      },
      visualMap: {
        type: 'piecewise',
        pieces: [
          {min: 100, label: '100以上'},
          {min: 50, max: 100, label: '50-100'},
          {min: 20, max: 50, label: '20-50'},
          {min: 10, max: 20, label: '10-20'},
          {min: 5, max: 10, label: '5-10'},
          {max: 5, label: '5以下'}
        ],
        inRange: {
          color: ['#e0f3f8', '#abd9e9', '#74add1', '#4575b4', '#313695']
        },
        left: 'left',
        top: 'bottom'
      },
      series: [{
        name: options.seriesName || '数值',
        type: 'map',
        map: 'china',
        roam: true, // 允许缩放和平移
        data: processedData, // 使用处理后的数据
        label: {
          show: false, // 默认不显示省份名称
          fontSize: 10
        },
        emphasis: {
          label: {
            show: false // 鼠标悬停时也不显示
          },
          itemStyle: {
            areaColor: '#ffd700'
          }
        }
      }]
    };
    
    // 合并自定义选项，但保留我们处理过的数据
    const mergedOptions = {...defaultOptions, ...options};
    mergedOptions.series[0].data = processedData;
    
    // 如果options中指定了要显示标签，则使用options中的设置
    if (options.showLabel !== undefined) {
      mergedOptions.series[0].label.show = options.showLabel;
      // 只有在主动选择显示标签时，悬停高亮才显示标签
      if (options.showLabel) {
        mergedOptions.series[0].emphasis.label.show = true;
      }
    }
    
    console.log('设置地图配置', mergedOptions);
    
    // 设置图表配置
    chart.setOption(mergedOptions);
    
    // 绑定窗口大小变化事件
    window.addEventListener('resize', function() {
      chart.resize();
    });
    
    // 返回图表实例，以便进一步自定义
    return chart;
  } catch (error) {
    console.error('渲染中国地图失败:', error);
    // 创建错误提示
    container.innerHTML = `<div class="chart-error">
      <p>加载地图失败</p>
      <p class="error-details">${error.message}</p>
    </div>`;
  } finally {
    // 移除加载中状态
    container.classList.remove('loading');
  }
}

/**
 * 渲染热力地图
 * @param {string} containerId - 地图容器的DOM ID
 * @param {Array} data - 地图数据
 * @param {Object} options - 配置选项
 */
async function renderHeatMap(containerId, data, options = {}) {
  console.log('初始化热力地图容器', containerId);
  const container = document.getElementById(containerId);
  if (!container) {
    console.error(`找不到容器: ${containerId}`);
    return;
  }
  
  // 显示加载中状态
  container.classList.add('loading');
  
  try {
    // 确保地图数据已加载
    await loadChinaMapData();
    
    // 创建地图实例
    const chart = echarts.init(container);
    console.log('热力地图实例创建成功');
    
    // 默认配置
    const defaultOptions = {
      title: {
        text: options.title || '',
        left: 'center'
      },
      tooltip: {
        trigger: 'item'
      },
      visualMap: {
        min: 0,
        max: options.maxValue || 100,
        calculable: true,
        inRange: {
          color: ['#50a3ba', '#eac736', '#d94e5d']
        },
        textStyle: {
          color: '#333'
        }
      },
      geo: {
        map: 'china',
        roam: true,
        label: {
          show: false, // 不显示省份名称
          fontSize: 10
        },
        itemStyle: {
          areaColor: '#eee',
          borderColor: '#ccc'
        },
        emphasis: {
          label: {
            show: false // 高亮时也不显示
          },
          itemStyle: {
            areaColor: '#ffd700'
          }
        }
      },
      series: [
        {
          name: options.seriesName || '热力值',
          type: 'heatmap',
          coordinateSystem: 'geo',
          data: data
        }
      ]
    };
    
    // 合并自定义选项
    const mergedOptions = {...defaultOptions, ...options};
    
    // 如果options中指定了要显示标签，则使用options中的设置
    if (options.showLabel !== undefined) {
      mergedOptions.geo.label.show = options.showLabel;
      // 只有在主动选择显示标签时，悬停高亮才显示标签
      if (options.showLabel) {
        mergedOptions.geo.emphasis.label.show = true;
      }
    }
    
    console.log('设置热力地图配置');
    
    // 设置图表配置
    chart.setOption(mergedOptions);
    
    // 绑定窗口大小变化事件
    window.addEventListener('resize', function() {
      chart.resize();
    });
    
    // 返回图表实例，以便进一步自定义
    return chart;
  } catch (error) {
    console.error('渲染热力地图失败:', error);
    // 创建错误提示
    container.innerHTML = `<div class="chart-error">
      <p>加载地图失败</p>
      <p class="error-details">${error.message}</p>
    </div>`;
  } finally {
    // 移除加载中状态
    container.classList.remove('loading');
  }
}

/**
 * 渲染带有标记点和飞线的地图
 * @param {string} containerId - 地图容器的DOM ID
 * @param {Array} pointsData - 点数据
 * @param {Array} linesData - 线数据
 * @param {Object} options - 配置选项
 */
async function renderMapWithPointsAndLines(containerId, pointsData, linesData, options = {}) {
  console.log('初始化带有标记点和飞线的地图容器', containerId);
  const container = document.getElementById(containerId);
  if (!container) {
    console.error(`找不到容器: ${containerId}`);
    return;
  }
  
  // 显示加载中状态
  container.classList.add('loading');
  
  try {
    // 确保地图数据已加载
    await loadChinaMapData();
    
    // 创建地图实例
    const chart = echarts.init(container);
    console.log('带有标记点和飞线的地图实例创建成功');
    
    // 飞机路径图标
    const planePath = 'path://M1705.06,1318.313v-89.254l-319.9-221.799l0.073-208.063c0.521-84.662-26.629-121.796-63.961-121.491c-37.332-0.305-64.482,36.829-63.961,121.491l0.073,208.063l-319.9,221.799v89.254l330.343-157.288l12.238,241.308l-134.449,92.931l0.531,42.034l175.125-42.917l175.125,42.917l0.531-42.034l-134.449-92.931l12.238-241.308L1705.06,1318.313z';
    
    // 默认配置
    const defaultOptions = {
      title: {
        text: options.title || '',
        left: 'center'
      },
      tooltip: {
        trigger: 'item'
      },
      geo: {
        map: 'china',
        roam: true,
        label: {
          show: false, // 不显示省份名称
          fontSize: 10,
          color: '#fff'
        },
        itemStyle: {
          areaColor: '#0E2152',
          borderColor: '#5089EC',
          borderWidth: 1
        },
        emphasis: {
          label: {
            show: false // 高亮时也不显示
          },
          itemStyle: {
            areaColor: '#2386AD'
          }
        }
      },
      series: [
        {
          // 散点系列数据
          type: 'effectScatter',
          coordinateSystem: 'geo',
          effectType: 'ripple',
          showEffectOn: 'render',
          rippleEffect: {
            period: 4,
            scale: 4,
            brushType: 'fill'
          },
          zlevel: 1,
          data: pointsData,
          symbol: 'circle',
          symbolSize: 6,
          itemStyle: {
            color: '#00EEFF'
          }
        },
        {
          // 线条系列数据
          type: 'lines',
          zlevel: 2,
          symbol: ['none', 'arrow'],
          symbolSize: 10,
          effect: {
            show: true,
            period: 6,
            trailLength: 0,
            symbol: planePath,
            symbolSize: 15
          },
          lineStyle: {
            normal: {
              color: '#93EBF8',
              width: 2.5,
              opacity: 0.6,
              curveness: 0.2
            }
          },
          data: linesData
        }
      ]
    };
    
    // 合并自定义选项
    const mergedOptions = {...defaultOptions, ...options};
    
    // 如果options中指定了要显示标签，则使用options中的设置
    if (options.showLabel !== undefined) {
      mergedOptions.geo.label.show = options.showLabel;
      // 只有在主动选择显示标签时，悬停高亮才显示标签
      if (options.showLabel) {
        mergedOptions.geo.emphasis.label.show = true;
      }
    }
    
    console.log('设置带有标记点和飞线的地图配置');
    
    // 设置图表配置
    chart.setOption(mergedOptions);
    
    // 绑定窗口大小变化事件
    window.addEventListener('resize', function() {
      chart.resize();
    });
    
    // 返回图表实例，以便进一步自定义
    return chart;
  } catch (error) {
    console.error('渲染地图失败:', error);
    // 创建错误提示
    container.innerHTML = `<div class="chart-error">
      <p>加载地图失败</p>
      <p class="error-details">${error.message}</p>
    </div>`;
  } finally {
    // 移除加载中状态
    container.classList.remove('loading');
  }
} 