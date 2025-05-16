// 营销策略页面脚本

document.addEventListener('DOMContentLoaded', function() {
  // 页面加载时不自动加载策略
  // 显示初始提示信息
  document.getElementById('strategyEmpty').style.display = 'block';

  // 检查是否有模拟数据，如果有则加载
  if (DataService.hasSimulationData()) {
    loadSimulationData();
  }

  // 监听数据更新事件
  window.addEventListener('local_data_updated', function() {
    console.log('数据更新事件接收到，刷新页面数据');
    loadSimulationData();
  });

  // 刷新按钮
  document.getElementById('refreshStrategyBtn').addEventListener('click', function() {
    loadStrategy();
  });

  // 测试按钮
  document.getElementById('testStrategyBtn').addEventListener('click', function() {
    loadMockStrategy();
  });
  
  // 策略筛选
  const filterOptions = document.querySelectorAll('.filter-option');
  filterOptions.forEach(option => {
    option.addEventListener('click', function() {
      // 移除所有active类
      filterOptions.forEach(opt => opt.classList.remove('active'));
      // 添加当前项active类
      this.classList.add('active');
      // 筛选策略
      filterStrategies(this.getAttribute('data-filter'));
    });
  });
  
  // 确保营销策略菜单项始终可见
  ensureMarketingMenuVisible();
  
  // 初始化策略详情模态框
  initStrategyModal();
});

// 初始化策略详情模态框
function initStrategyModal() {
  const modal = document.getElementById('strategyModal');
  const closeBtn = modal.querySelector('.close');
  
  // 关闭模态框
  closeBtn.addEventListener('click', function() {
    modal.classList.remove('show');
  });
  
  // 点击模态框外部关闭
  window.addEventListener('click', function(event) {
    if (event.target === modal) {
      modal.classList.remove('show');
    }
  });
}

// 显示策略详情模态框
function showStrategyDetail(strategy) {
  const modal = document.getElementById('strategyModal');
  const title = document.getElementById('modalStrategyTitle');
  const content = document.getElementById('modalStrategyContent');
  
  title.textContent = strategy.tag;
  
  // 构建详情内容
  content.innerHTML = `
    <div class="strategy-container">
      <div class="strategy-summary">${strategy.strategy}</div>
      
      <div class="strategy-phases">
        <div class="phase-item">
          <div class="phase-header">
            <div class="phase-title">准备阶段</div>
          </div>
          <div class="phase-content">
            <ul>
              ${strategy.preparation ? strategy.preparation.map(item => `<li>${item}</li>`).join('') : `
                <li>分析目标市场和消费者需求，确定此策略的目标人群</li>
                <li>收集竞争对手相关数据，制定差异化策略</li>
                <li>评估当前资源状况，确保足够的预算和人力支持</li>
                <li>设定明确的KPI指标，包括销售增长、客流量增加、转化率等</li>
              `}
            </ul>
          </div>
        </div>
        
        <div class="phase-item">
          <div class="phase-header">
            <div class="phase-title">执行阶段</div>
          </div>
          <div class="phase-content">
            <ul>
              ${strategy.execution ? strategy.execution.map(item => `<li>${item}</li>`).join('') : `
                <li>制定详细的实施计划，明确各部门职责</li>
                <li>创建相关营销内容和物料，确保品牌一致性</li>
                <li>选择合适的营销渠道，确保触达目标人群</li>
                <li>制定紧急预案，应对可能出现的问题</li>
              `}
            </ul>
          </div>
        </div>
        
        <div class="phase-item">
          <div class="phase-header">
            <div class="phase-title">评估阶段</div>
          </div>
          <div class="phase-content">
            <ul>
              ${strategy.evaluation ? strategy.evaluation.map(item => `<li>${item}</li>`).join('') : `
                <li>收集并分析关键数据，评估活动效果</li>
                <li>对比活动前后的销售数据和消费者行为变化</li>
                <li>总结经验教训，记录成功因素和失败原因</li>
                <li>根据结果调整后续活动计划</li>
              `}
            </ul>
          </div>
        </div>
      </div>
      
      <div class="strategy-footer">
        <div class="strategy-tags">
          <div class="strategy-tag primary">${strategy.tag}</div>
          ${strategy.tags ? strategy.tags.map(tag => `<div class="strategy-tag">${tag}</div>`).join('') : ''}
        </div>
      </div>
      
      <div class="metrics-row">
        <div class="metric-box primary">
          <div class="metric-label">预期销售增长</div>
          <div class="metric-value">${strategy.expectedSales || '30%'}</div>
          <div class="metric-trend up">同比增长</div>
        </div>
        <div class="metric-box success">
          <div class="metric-label">客流量提升</div>
          <div class="metric-value">${strategy.expectedTraffic || '25%'}</div>
          <div class="metric-trend up">显著提升</div>
        </div>
        <div class="metric-box warning">
          <div class="metric-label">投资回报率</div>
          <div class="metric-value">${strategy.expectedROI || '180%'}</div>
          <div class="metric-trend up">高效收益</div>
        </div>
      </div>
      
      <div class="chart-wrapper" id="strategyEffectChart"></div>
    </div>
  `;
  
  // 显示模态框
  modal.classList.add('show');
  
  // 渲染图表
  setTimeout(() => {
    renderStrategyEffectChart(strategy);
  }, 100);
}

// 渲染策略效果预测图表
function renderStrategyEffectChart(strategy) {
  const chartDom = document.getElementById('strategyEffectChart');
  if (!chartDom) return;
  
  const myChart = echarts.init(chartDom);
  
  const option = {
    title: {
      text: '预期效果对比',
      left: 'center',
      top: 10,
      textStyle: {
        fontSize: 14
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['实施前', '实施后'],
      bottom: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '20%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['客流量', '销售额', '品牌知名度', '客户忠诚度', '转化率']
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '实施前',
        type: 'bar',
        data: [100, 100, 100, 100, 100],
        itemStyle: {
          color: '#bfbfbf'
        }
      },
      {
        name: '实施后',
        type: 'bar',
        data: [
          strategy.trafficIncrease || 130, 
          strategy.salesIncrease || 145, 
          strategy.brandIncrease || 125, 
          strategy.loyaltyIncrease || 138, 
          strategy.conversionIncrease || 140
        ],
        itemStyle: {
          color: '#1890ff'
        }
      }
    ]
  };
  
  myChart.setOption(option);
}

// 过滤策略
function filterStrategies(filter) {
  const strategyCards = document.querySelectorAll('.strategy-card');
  if (filter === 'all') {
    strategyCards.forEach(card => {
      card.style.display = '';
    });
    return;
  }
  
  strategyCards.forEach(card => {
    const cardFilter = card.getAttribute('data-filter');
    if (cardFilter === filter) {
      card.style.display = '';
    } else {
      card.style.display = 'none';
    }
  });
}

// 确保营销策略菜单项在侧边栏中始终可见
function ensureMarketingMenuVisible() {
  const allSidebarItems = document.querySelectorAll('.sidebar-menu li');
  const marketingMenuItem = document.querySelector('.sidebar-menu li a[href*="marketing"]').parentElement;
  
  if (marketingMenuItem) {
    marketingMenuItem.style.display = 'block';
    
    // 如果是当前页面，添加active类
    if (window.location.href.includes('marketing.html')) {
      marketingMenuItem.querySelector('a').classList.add('active');
    }
  }
}

// 加载策略建议（API）
async function loadStrategy() {
  showLoading();
  hideError();
  hideEmptyTip();
  try {
    // 假设API为 /api/marketing-strategy
    const response = await http.get('/api/marketing-strategy');
    renderStrategyList(response.data.strategies || []);
    hideLoading();
    // 显示策略列表
    document.getElementById('strategyList').style.display = 'grid';
    // 显示指标数据
    document.getElementById('metricsContainer').style.display = 'flex';
  } catch (error) {
    console.error('获取策略建议失败:', error);
    // API失败时也加载模拟数据
    loadMockStrategy();
  }
}

// 加载mock策略建议
function loadMockStrategy() {
  showLoading();
  hideError();
  hideEmptyTip();
  setTimeout(function() {
    const mockData = generateMockData();
    renderStrategyList(mockData);
    hideLoading();
    // 显示策略列表
    document.getElementById('strategyList').style.display = 'grid';
    // 显示指标数据
    document.getElementById('metricsContainer').style.display = 'flex';
  }, 800);
}

// 渲染策略建议列表
function renderStrategyList(list) {
  const container = document.getElementById('strategyList');
  container.innerHTML = '';
  if (!list || list.length === 0) {
    container.innerHTML = '<div style="text-align:center;color:#8c8c8c;font-size:16px;margin-top:40px;">暂无策略建议</div>';
    return;
  }
  list.forEach(item => {
    const card = document.createElement('div');
    card.className = 'strategy-card';
    card.setAttribute('data-filter', item.filter || 'all');
    
    card.innerHTML = `
      <div class="strategy-header">
        <div class="strategy-title">
          <span class="strategy-title-icon">${item.icon || '💡'}</span>
          ${item.tag ? item.tag : '策略建议'}
        </div>
        ${item.score ? `
          <div class="strategy-rating">
            <span class="rating-score">${item.score}</span>
            <span class="rating-stars">${getStars(item.score)}</span>
          </div>
        ` : ''}
      </div>
      <div class="strategy-container">
        <p class="strategy-summary">${item.strategy}</p>
        
        <div class="strategy-footer">
          <div class="strategy-tags">
            ${item.tags ? item.tags.map(tag => `<div class="strategy-tag">${tag}</div>`).join('') : ''}
          </div>
          <button class="refresh-btn" onclick="showStrategyDetail(${JSON.stringify(item).replace(/"/g, '&quot;')})">
            <i class="icon-placeholder icon-opportunity"></i> 查看详情
          </button>
        </div>
      </div>
    `;
    
    container.appendChild(card);
  });
}

// 根据评分获取星星
function getStars(score) {
  const fullStars = Math.floor(score);
  const halfStar = score - fullStars >= 0.5;
  let stars = '';
  
  // 添加实心星星
  for (let i = 0; i < fullStars; i++) {
    stars += '★';
  }
  
  // 添加半星
  if (halfStar) {
    stars += '☆';
  }
  
  return stars;
}

// 显示加载动画
function showLoading() {
  document.getElementById('strategyLoading').style.display = 'block';
}
// 隐藏加载动画
function hideLoading() {
  document.getElementById('strategyLoading').style.display = 'none';
}
// 显示错误
function showError() {
  document.getElementById('strategyError').style.display = 'block';
}
// 隐藏错误
function hideError() {
  document.getElementById('strategyError').style.display = 'none';
}

// 隐藏空提示
function hideEmptyTip() {
  document.getElementById('strategyEmpty').style.display = 'none';
}

// 生成模拟数据
function generateMockData() {
  // 品牌策略
  const brandStrategies = [
    {
      strategy: "针对年轻消费群体，推出联名IP茶饮和社交媒体互动活动，提升品牌年轻化形象。",
      tag: "品牌年轻化",
      score: 4.7,
      filter: "brand",
      icon: "🏆",
      preparation: [
        "分析18-35岁年轻消费者的喜好和消费习惯，了解他们关注的IP和社交媒体平台",
        "选择与目标人群契合度高的IP资源进行洽谈，确保合作方向符合品牌调性",
        "准备社交媒体投放资源，包括短视频平台、微博、微信公众号等",
        "设计符合年轻人审美的包装和视觉形象，突出联名特色"
      ],
      execution: [
        "推出限定款联名茶品，在重点城市核心商圈设立快闪店增强体验感",
        "与知名KOL合作推广，制作创意短视频和图文内容",
        "在社交媒体发起互动话题，鼓励用户分享品尝体验和创意搭配",
        "组织线下品鉴会，邀请目标人群体验新品并提供反馈",
        "在产品包装中加入AR互动元素，用户可通过扫码获得独特体验"
      ],
      evaluation: [
        "监测社交媒体互动量和话题热度，评估传播效果",
        "追踪联名产品销量和复购率，对比常规产品数据",
        "收集用户反馈，评估品牌形象年轻化转变程度",
        "分析活动前后品牌关注度和搜索量变化",
        "记录宣传成本和销售收入，计算ROI，评估活动性价比"
      ],
      tags: ["社交媒体", "IP联名", "年轻消费者"],
      expectedSales: "37%",
      expectedTraffic: "42%",
      expectedROI: "215%",
      trafficIncrease: 142,
      salesIncrease: 137,
      brandIncrease: 156,
      loyaltyIncrease: 128,
      conversionIncrease: 133
    },
    {
      strategy: "打造明星单品战略，将代表性茶品打造为品牌符号，集中营销资源提升知名度。",
      tag: "明星单品",
      score: 4.5,
      filter: "brand",
      icon: "⭐",
      preparation: [
        "分析现有产品线，筛选出最具潜力的1-2款代表性茶品",
        "收集市场反馈和消费者评价，确认产品差异化优势",
        "制定明星单品包装和视觉识别系统，确保一致性识别",
        "规划明星单品的专项营销预算和推广策略"
      ],
      execution: [
        "重新设计明星单品包装，突出产品独特性和品牌标识",
        "在各大媒体和销售渠道重点突出明星单品",
        "策划明星单品故事，包括茶园环境、制作工艺和品饮体验",
        "邀请行业专家和媒体进行品鉴评价，获取权威背书",
        "与高端餐饮场所合作，将明星单品纳入其茶单"
      ],
      evaluation: [
        "追踪明星单品销量和增长率，评估推广效果",
        "分析明星单品带动其他产品销售的关联效应",
        "收集消费者对明星单品的认知度调查",
        "评估明星单品对品牌整体形象提升的贡献",
        "监测竞争对手的反应和市场变化"
      ],
      tags: ["产品聚焦", "品牌标识", "资源集中"],
      expectedSales: "45%",
      expectedTraffic: "30%",
      expectedROI: "200%",
      trafficIncrease: 130,
      salesIncrease: 145,
      brandIncrease: 168,
      loyaltyIncrease: 135,
      conversionIncrease: 125
    },
    {
      strategy: "开展品牌文化传承活动，展示茶艺师技艺与茶道文化，强化品牌文化底蕴。",
      tag: "文化传承",
      score: 4.3,
      filter: "brand",
      icon: "🏛️",
      preparation: [
        "挖掘品牌历史和茶文化背景资料，整理品牌文化故事",
        "培训茶艺师团队，提升展示和传播能力",
        "设计茶文化体验活动流程和内容，强调沉浸式体验",
        "选择有文化氛围的场所作为活动地点"
      ],
      execution: [
        "举办'茶道文化体验周'活动，邀请消费者参与茶艺展示",
        "制作茶文化纪录片或短视频，在线上平台传播",
        "与文化场所（如博物馆、文化中心）合作举办茶文化展览",
        "开设茶艺课程，传授基础泡茶技巧和品茶礼仪",
        "出版茶文化书籍或手册，讲述品牌与茶文化的渊源"
      ],
      evaluation: [
        "统计文化活动参与人数和满意度，评估活动效果",
        "分析活动前后品牌文化认知度的变化",
        "追踪媒体报道和文化类KOL评价，评估文化传播广度",
        "评估文化活动对销售的间接拉动效果",
        "监测品牌高端形象建立情况"
      ],
      tags: ["茶文化", "品牌底蕴", "文化体验"],
      expectedSales: "25%",
      expectedTraffic: "35%",
      expectedROI: "150%",
      trafficIncrease: 135,
      salesIncrease: 125,
      brandIncrease: 172,
      loyaltyIncrease: 145,
      conversionIncrease: 120
    },
    {
      strategy: "开展品牌社会责任计划，支持茶农教育和环保项目，塑造负责任品牌形象。",
      tag: "社会责任",
      score: 4.4,
      filter: "brand",
      icon: "🌱",
      preparation: [
        "确定品牌社会责任重点领域，如茶农福利、环境保护或教育支持",
        "寻找合适的非营利组织或公益项目合作伙伴",
        "制定长期社会责任计划和投入预算",
        "设计公益项目执行方案和传播策略"
      ],
      execution: [
        "启动'茶园未来计划'，支持茶农子女教育",
        "实施可持续包装计划，减少塑料使用，采用环保材料",
        "组织员工参与茶园环境保护志愿活动",
        "发布企业社会责任年度报告，展示品牌影响力",
        "将部分产品收益投入到公益项目中，并在包装上标明"
      ],
      evaluation: [
        "统计公益项目受益人数和实际影响",
        "收集消费者对品牌社会责任形象的认知调查",
        "分析社会责任活动的媒体报道和口碑传播效果",
        "评估环保包装对成本和消费者接受度的影响",
        "监测负责任消费群体的购买行为变化"
      ],
      tags: ["公益项目", "环境保护", "可持续发展"],
      expectedSales: "22%",
      expectedTraffic: "28%",
      expectedROI: "135%",
      trafficIncrease: 128,
      salesIncrease: 122,
      brandIncrease: 165,
      loyaltyIncrease: 158,
      conversionIncrease: 118
    }
  ];
  
  // 产品策略
  const productStrategies = [
    {
      strategy: "结合健康养生趋势，主推无糖、低咖啡因茶产品，并与健康类KOL合作推广。",
      tag: "健康养生",
      score: 4.5,
      filter: "product",
      icon: "🍃",
      preparation: [
        "收集健康饮品市场数据，分析无糖低咖啡因茶产品的市场规模与发展趋势",
        "调研目标消费者（健康生活方式爱好者）的饮品偏好和消费习惯",
        "筛选合适的健康领域KOL，重点关注运动、营养和中医养生领域的意见领袖",
        "开发并测试无糖低咖啡因茶产品配方，确保口感和健康效果的平衡"
      ],
      execution: [
        "推出无糖低咖啡因茶产品系列，强调天然健康特性",
        "设计专业健康认证标签，突出产品的养生价值",
        "与健康类KOL共同策划内容，分享茶饮与健康生活的结合方式",
        "在瑜伽馆、健身中心等场所投放样品，直接触达目标消费群体",
        "开展茶疗养生讲座，邀请中医专家分享茶饮健康知识"
      ],
      evaluation: [
        "跟踪健康茶产品销售数据，与常规产品进行对比",
        "分析KOL内容的传播效果，包括浏览量、互动率和转化率",
        "收集消费者对产品健康概念接受度的反馈",
        "评估品牌健康形象建立情况，包括消费者认知调查",
        "监测同类竞品市场份额变化，评估市场竞争力"
      ],
      tags: ["健康生活", "低糖低咖啡因", "KOL合作"],
      expectedSales: "33%",
      expectedTraffic: "28%",
      expectedROI: "195%",
      trafficIncrease: 128,
      salesIncrease: 133,
      brandIncrease: 142,
      loyaltyIncrease: 139,
      conversionIncrease: 127
    },
    {
      strategy: "开发便携式即冲茶包，满足快节奏生活的消费需求，开拓办公室场景消费。",
      tag: "便捷产品",
      score: 4.4,
      filter: "product",
      icon: "⏱️",
      preparation: [
        "调研便携式茶产品市场规模和消费群体特征",
        "测试不同茶叶品类的即冲效果，确保口感品质",
        "开发创新包装技术，确保茶叶新鲜度和冲泡便捷性",
        "分析办公室、旅行等场景下的消费者痛点和需求"
      ],
      execution: [
        "推出系列即冲茶包产品，每款针对不同功能需求（提神、舒压、助消化等）",
        "设计简约时尚的包装，方便携带和储存",
        "制作直观的冲泡指南，降低使用门槛",
        "在写字楼、商务酒店等场所进行定向推广",
        "与旅行品牌合作，打造旅行茶礼盒"
      ],
      evaluation: [
        "追踪便携茶产品销售数据，分析与传统茶产品的互补性",
        "收集目标场景下消费者的使用体验反馈",
        "评估包装创新对产品保质期和口感的影响",
        "分析新场景开拓效果，如办公室消费转化率",
        "监测竞品动向和市场变化"
      ],
      tags: ["即冲茶包", "办公场景", "便携设计"],
      expectedSales: "38%",
      expectedTraffic: "45%",
      expectedROI: "210%",
      trafficIncrease: 145,
      salesIncrease: 138,
      brandIncrease: 125,
      loyaltyIncrease: 120,
      conversionIncrease: 150
    },
    {
      strategy: "推出高端礼盒定制服务，支持个性化组合和定制包装，满足送礼和收藏需求。",
      tag: "定制礼盒",
      score: 4.6,
      filter: "product",
      icon: "🎀",
      preparation: [
        "分析高端茶礼市场规模和消费者送礼心理",
        "调研个性化定制需求，包括包装、组合和个性化元素",
        "开发在线定制平台，支持茶品组合和包装选择",
        "培训专业定制顾问团队，提供一对一咨询服务"
      ],
      execution: [
        "推出线上+线下定制礼盒服务，支持多层次定制需求",
        "提供季节限定包装设计，增加收藏价值",
        "推出名家书法、国画定制服务，增加文化附加值",
        "针对企业客户，提供logo和祝福语个性化定制",
        "发布定制礼盒购买指南，引导消费者选择合适的组合"
      ],
      evaluation: [
        "统计定制礼盒销售额和客单价，评估高端市场拓展效果",
        "分析不同定制元素的受欢迎程度，优化定制选项",
        "收集赠送方和接收方的反馈，评估礼品满意度",
        "追踪企业客户的复购情况，建立长期合作关系",
        "评估定制服务对品牌高端形象的提升效果"
      ],
      tags: ["高端定制", "礼品市场", "个性化服务"],
      expectedSales: "42%",
      expectedTraffic: "26%",
      expectedROI: "185%",
      trafficIncrease: 126,
      salesIncrease: 142,
      brandIncrease: 148,
      loyaltyIncrease: 144,
      conversionIncrease: 130
    },
    {
      strategy: "开发创新调饮茶基底产品，满足年轻人DIY饮品需求，扩展家庭消费场景。",
      tag: "创新调饮",
      score: 4.2,
      filter: "product",
      icon: "🍹",
      preparation: [
        "研究年轻消费群体的饮品创新需求和DIY趋势",
        "开发适合调饮的浓缩茶基底产品，保证与果汁、奶制品等的调和效果",
        "测试多种调饮配方，整理创意茶饮食谱",
        "分析家庭饮品消费场景和购买决策因素"
      ],
      execution: [
        "推出系列调饮茶基底产品，包括不同风味和功能性产品线",
        "设计精美的调饮指南和创意食谱卡，随产品附赠",
        "通过短视频平台发布创意调饮教程，鼓励用户参与互动",
        "开发简单实用的调饮工具套装，降低制作门槛",
        "举办线上调饮大赛，收集和推广用户创意配方"
      ],
      evaluation: [
        "统计调饮产品销售数据，分析用户构成和购买频率",
        "收集用户分享的创意配方数量和质量，评估参与度",
        "分析社交媒体上用户分享的内容数量和互动率",
        "评估产品在家庭场景中的使用频率和满意度",
        "监测创新产品对年轻消费群体拓展效果"
      ],
      tags: ["DIY茶饮", "家庭场景", "年轻市场"],
      expectedSales: "36%",
      expectedTraffic: "47%",
      expectedROI: "175%",
      trafficIncrease: 147,
      salesIncrease: 136,
      brandIncrease: 132,
      loyaltyIncrease: 120,
      conversionIncrease: 155
    }
  ];

  // 推广策略
  const promotionStrategies = [
    {
      strategy: "在传统节日推出限量礼盒，强化文化认同感，吸引礼品消费人群。",
      tag: "节日营销",
      score: 4.3,
      filter: "promotion",
      icon: "🎁",
      preparation: [
        "分析往年传统节日销售数据，确定重点节日和礼盒预算",
        "进行礼品市场调研，了解不同价位礼品的需求和竞争状况",
        "设计符合传统文化元素的礼盒包装，突出中国茶文化特色",
        "确定限量版策略，制造稀缺感和收藏价值",
        "建立企业客户礼品定制渠道，扩大批量采购市场"
      ],
      execution: [
        "提前1-2个月开始预热，通过线上线下渠道宣传节日限定礼盒",
        "推出多个价位段的礼盒选择，满足不同消费能力的需求",
        "与文化机构合作，将传统文化元素融入产品设计和营销故事",
        "设置早鸟预订优惠，鼓励提前下单",
        "针对企业客户提供定制服务，加入企业logo和祝福语",
        "门店布置节日氛围，提供精美包装服务"
      ],
      evaluation: [
        "统计节日礼盒销售量和销售额，与普通产品和往年数据对比",
        "分析不同价位礼盒的销售情况，评估价格策略有效性",
        "收集礼品赠送者和接收者的反馈，了解满意度",
        "评估企业客户的复购率，建立长期合作关系",
        "计算礼盒生产成本和营销投入，评估利润率"
      ],
      tags: ["传统文化", "礼品市场", "限量版"],
      expectedSales: "48%",
      expectedTraffic: "35%",
      expectedROI: "220%",
      trafficIncrease: 135,
      salesIncrease: 148,
      brandIncrease: 132,
      loyaltyIncrease: 125,
      conversionIncrease: 145
    },
    {
      strategy: "结合季节变化推出主题营销活动，如春茶节、夏日冷泡茶、秋冬暖茶系列。",
      tag: "季节营销",
      score: 4.4,
      filter: "promotion",
      icon: "🍂",
      preparation: [
        "分析不同季节的茶叶特性和消费习惯变化",
        "规划全年季节性营销日历，确定关键时间节点",
        "开发季节限定产品，突出时令特性",
        "设计符合季节主题的视觉元素和营销语言"
      ],
      execution: [
        "春季：举办春茶首发品鉴会，突出新茶上市的新鲜感",
        "夏季：推广冷泡茶和冰茶饮品，提供解暑饮品解决方案",
        "秋季：推出果香调配茶，搭配秋季水果元素",
        "冬季：强调温暖功效和送礼需求，提供养生暖茶套装",
        "每季度更换店面陈列和包装设计，强化季节感"
      ],
      evaluation: [
        "分析各季节主题活动的销售转化率",
        "评估季节限定产品对常规产品销售的带动效果",
        "比较不同季节的客流量和客单价变化",
        "收集消费者对季节性产品的反馈，优化产品设计",
        "评估季节营销在平衡全年销售方面的效果"
      ],
      tags: ["季节限定", "时令产品", "主题营销"],
      expectedSales: "36%",
      expectedTraffic: "32%",
      expectedROI: "180%",
      trafficIncrease: 132,
      salesIncrease: 136,
      brandIncrease: 124,
      loyaltyIncrease: 130,
      conversionIncrease: 128
    },
    {
      strategy: "开展'茶知识普及计划'，通过内容营销提高消费者对茶品质的认知，增强购买信心。",
      tag: "知识营销",
      score: 4.2,
      filter: "promotion",
      icon: "📚",
      preparation: [
        "整理专业茶知识库，包括茶叶种类、产地特色、品鉴方法等",
        "设计简明易懂的知识内容框架，适合不同知识水平的消费者",
        "招募茶文化专家和资深茶师参与内容创作",
        "规划内容发布平台和频率，确保持续输出"
      ],
      execution: [
        "推出'每日一茶知识'系列短内容，在社交媒体定期更新",
        "制作茶品鉴指南和冲泡方法视频教程",
        "在产品包装中加入二维码，链接到详细的茶知识库",
        "举办线上线下茶知识讲座和工作坊",
        "推出互动型知识问答活动，增加消费者参与感"
      ],
      evaluation: [
        "统计知识内容的阅读量和分享率，评估传播效果",
        "分析知识内容与销售转化的关联性",
        "收集消费者知识水平和兴趣点变化，调整内容策略",
        "评估知识营销对品牌专业形象的提升效果",
        "监测消费者对产品理解深度的变化"
      ],
      tags: ["内容营销", "茶文化", "消费者教育"],
      expectedSales: "25%",
      expectedTraffic: "38%",
      expectedROI: "160%",
      trafficIncrease: 138,
      salesIncrease: 125,
      brandIncrease: 145,
      loyaltyIncrease: 152,
      conversionIncrease: 122
    },
    {
      strategy: "推出积分兑换和会员等级体系，奖励忠实客户，提高复购率。",
      tag: "积分激励",
      score: 4.5,
      filter: "promotion",
      icon: "🏅",
      preparation: [
        "设计会员等级体系和积分获取规则，确保公平性和激励性",
        "开发积分管理系统，支持多渠道积分累积和兑换",
        "规划丰富的积分兑换礼品和特权，满足不同消费者需求",
        "培训销售人员熟悉会员体系，能够向消费者清晰解释"
      ],
      execution: [
        "推出会员App或小程序，方便消费者查询积分和兑换礼品",
        "设置会员专属优惠，如生日礼遇、新品优先体验等特权",
        "定期推出限时积分翻倍活动，刺激消费",
        "发送个性化消费提醒和积分到期提醒",
        "高等级会员提供专属客服和定制服务"
      ],
      evaluation: [
        "分析会员复购率和客单价变化，评估忠诚度提升效果",
        "统计积分兑换率和兑换商品偏好，优化兑换选项",
        "评估会员等级晋升转化漏斗，找出关键激励点",
        "计算会员获取成本和会员终身价值(LTV)",
        "收集会员满意度调查，持续改进会员体验"
      ],
      tags: ["会员忠诚", "积分兑换", "复购激励"],
      expectedSales: "40%",
      expectedTraffic: "30%",
      expectedROI: "225%",
      trafficIncrease: 130,
      salesIncrease: 140,
      brandIncrease: 128,
      loyaltyIncrease: 165,
      conversionIncrease: 135
    }
  ];
  
  // 渠道策略
  const channelStrategies = [
    {
      strategy: "通过数字化技术，为每款茶品配备溯源码，消费者可追溯茶园种植环境，提高产品信任度。",
      tag: "科技溯源",
      score: 4.2,
      filter: "channel",
      icon: "📱",
      preparation: [
        "构建完整的茶品溯源体系，记录从茶园到成品的全过程",
        "开发溯源技术平台，包括二维码生成和后台管理系统",
        "收集茶园、采摘、制作工艺的高质量图片和视频资料",
        "制定数据安全和隐私保护策略，确保系统安全可靠",
        "培训茶园和生产人员使用溯源系统记录生产数据"
      ],
      execution: [
        "在每款茶品包装上加入专属溯源码，连接到产品信息页面",
        "通过H5页面展示茶品从种植、采摘到加工的全过程",
        "加入茶园环境数据，如海拔、气候、土壤等影响茶品质量的关键因素",
        "提供制茶工艺视频和泡茶指南，增强产品使用体验",
        "鼓励消费者扫码分享，通过社交媒体传播产品溯源故事",
        "举办'科技赋能传统茶业'主题活动，提升品牌创新形象"
      ],
      evaluation: [
        "统计溯源码扫描率和页面浏览时长，评估消费者参与度",
        "收集消费者对溯源信息的反馈，了解最受关注的内容",
        "追踪溯源产品与普通产品的销售对比，评估溯源价值",
        "分析社交媒体分享量和传播效果，评估口碑营销效果",
        "监测产品信任度和品牌认知度提升情况，评估长期价值"
      ],
      tags: ["数字化", "产品溯源", "透明生产"],
      expectedSales: "28%",
      expectedTraffic: "32%",
      expectedROI: "165%",
      trafficIncrease: 132,
      salesIncrease: 128,
      brandIncrease: 145,
      loyaltyIncrease: 142,
      conversionIncrease: 138
    },
    {
      strategy: "扩展线上专卖店渠道，优化电商平台体验，提供个性化产品推荐。",
      tag: "电商优化",
      score: 4.4,
      filter: "channel",
      icon: "🛒",
      preparation: [
        "分析现有电商平台表现，找出用户体验痛点和转化瓶颈",
        "研究行业领先电商的最佳实践，确定优化方向",
        "开发智能推荐算法，基于用户购买历史和偏好推荐产品",
        "优化产品展示页面，突出产品价值和差异化特点"
      ],
      execution: [
        "重新设计电商平台界面，优化用户浏览和购买流程",
        "添加详细的产品描述和高质量图片，增强购买信心",
        "实施个性化推荐系统，提高相关产品曝光率",
        "优化移动端体验，确保跨设备一致性",
        "提供在线咨询服务，解答客户的产品问题"
      ],
      evaluation: [
        "分析电商平台的转化率和跳出率变化",
        "统计平均停留时间和浏览页面数的变化",
        "评估个性化推荐的点击率和转化效果",
        "收集用户对新界面的满意度反馈",
        "比较优化前后的客单价和复购率变化"
      ],
      tags: ["用户体验", "个性化推荐", "转化优化"],
      expectedSales: "45%",
      expectedTraffic: "38%",
      expectedROI: "210%",
      trafficIncrease: 138,
      salesIncrease: 145,
      brandIncrease: 126,
      loyaltyIncrease: 132,
      conversionIncrease: 148
    },
    {
      strategy: "开拓高端商务酒店和餐厅渠道，提供专业茶饮解决方案和员工培训。",
      tag: "商务渠道",
      score: 4.3,
      filter: "channel",
      icon: "🏨",
      preparation: [
        "研究高端商务酒店和餐厅市场规模和茶品需求",
        "开发针对商务场所的茶饮解决方案，包括产品组合和展示方式",
        "设计专业培训课程，提升服务人员的茶知识和服务能力",
        "准备商务合作方案和价格策略，增强渠道吸引力"
      ],
      execution: [
        "与目标高端酒店和餐厅建立合作关系，成为其指定茶品供应商",
        "提供定制茶单和茶品展示柜，提升品牌曝光",
        "为合作伙伴的服务人员提供专业茶艺培训",
        "设计符合商务场所的茶具和服务流程",
        "在酒店房间提供精美茶礼，提升入住体验"
      ],
      evaluation: [
        "统计商务渠道销售额和增长率，评估渠道拓展效果",
        "收集终端消费者在商务场所的品牌体验反馈",
        "分析培训后服务人员的专业度提升和推荐销售能力",
        "评估商务渠道对品牌高端形象的助推作用",
        "监测商务客户转化为零售客户的情况"
      ],
      tags: ["高端市场", "B2B合作", "服务培训"],
      expectedSales: "35%",
      expectedTraffic: "25%",
      expectedROI: "190%",
      trafficIncrease: 125,
      salesIncrease: 135,
      brandIncrease: 150,
      loyaltyIncrease: 140,
      conversionIncrease: 128
    },
    {
      strategy: "发展社区茶艺体验中心，结合线下体验和线上购买，打造全渠道营销模式。",
      tag: "体验中心",
      score: 4.5,
      filter: "channel",
      icon: "🏮",
      preparation: [
        "选择高客流的社区商圈，评估开设体验中心的可行性",
        "设计沉浸式茶艺体验空间，创造舒适的品茗环境",
        "开发线上线下一体化系统，支持体验中心预约和线上复购",
        "培训体验中心员工，提升服务水平和专业知识"
      ],
      execution: [
        "在目标社区开设茶艺体验中心，提供免费品鉴和茶艺展示",
        "举办社区茶文化活动，如茶艺培训班、茶会等",
        "通过小程序提供预约服务和会员管理",
        "实施线下体验、线上购买的全渠道营销模式",
        "收集顾客反馈和喜好，提供个性化产品推荐"
      ],
      evaluation: [
        "统计体验中心客流量和转化率，评估运营效果",
        "分析体验后的线上复购率和客单价变化",
        "评估社区活动的参与度和品牌影响力",
        "计算体验中心的投入成本和回报周期",
        "比较不同社区体验中心的表现差异，优化选址策略"
      ],
      tags: ["线下体验", "社区营销", "全渠道"],
      expectedSales: "42%",
      expectedTraffic: "48%",
      expectedROI: "175%",
      trafficIncrease: 148,
      salesIncrease: 142,
      brandIncrease: 138,
      loyaltyIncrease: 155,
      conversionIncrease: 140
    }
  ];

  // 客户策略
  const customerStrategies = [
    {
      strategy: "基于高端茶爱好者消费数据，开发定制化茶产品与线下品鉴活动，强化品牌忠诚度。",
      tag: "会员营销",
      score: 4.6,
      filter: "customer",
      icon: "👑",
      preparation: [
        "分析高端茶爱好者的消费行为和偏好，建立精准用户画像",
        "设计会员等级体系，提供差异化会员权益",
        "筛选优质茶园资源，为定制产品做准备",
        "培训专业茶艺师团队，提升品鉴活动专业度",
        "选择高端场所作为品鉴活动场地，确保环境匹配目标群体期望"
      ],
      execution: [
        "推出会员专属的定制茶品系列，提供个性化定制服务",
        "定期举办小型精品茶席活动，限定高级会员参与",
        "邀请茶文化专家分享知识，提升品鉴体验的文化内涵",
        "建立茶品收藏家社群，促进会员间交流与分享",
        "提供茶园溯源和定制采摘体验，增强会员与品牌的情感联系",
        "开发专属APP，记录会员品茗历程和收藏"
      ],
      evaluation: [
        "追踪会员复购率和客单价变化，评估忠诚度提升情况",
        "分析品鉴活动参与率和满意度，优化活动体验",
        "统计会员推荐新客户的数量，评估口碑传播效果",
        "监测高端定制产品的销售情况，评估产品策略",
        "计算会员终身价值(LTV)，分析会员营销的长期收益"
      ],
      tags: ["高端市场", "茶文化", "定制服务"],
      expectedSales: "40%",
      expectedTraffic: "25%",
      expectedROI: "180%",
      trafficIncrease: 125,
      salesIncrease: 140,
      brandIncrease: 135,
      loyaltyIncrease: 160,
      conversionIncrease: 130
    },
    {
      strategy: "建立茶爱好者社群，组织线上线下交流活动，增强用户黏性和品牌认同感。",
      tag: "社群营销",
      score: 4.3,
      filter: "customer",
      icon: "👥",
      preparation: [
        "研究目标茶爱好者社群特征和兴趣点",
        "设计社群运营方案，包括内容规划和活动日历",
        "搭建社群平台，如微信群、小程序社区或专属论坛",
        "招募和培训社群运营人员，确保专业回应和内容输出"
      ],
      execution: [
        "启动'茶友会'社群，邀请核心用户加入",
        "定期发布专业茶知识和品鉴技巧内容",
        "组织线上品茗直播和线下茶会，增强社群互动",
        "邀请资深茶师和茶文化专家进行问答交流",
        "鼓励用户分享品茶心得和茶器收藏，打造UGC内容"
      ],
      evaluation: [
        "监测社群活跃度和用户留存率变化",
        "分析社群用户的购买转化率和客单价",
        "评估社群用户对新品的接受度和反馈速度",
        "统计用户自发内容的数量和质量，评估社群健康度",
        "比较社群用户与普通用户的品牌忠诚度差异"
      ],
      tags: ["茶友社群", "用户互动", "内容运营"],
      expectedSales: "32%",
      expectedTraffic: "35%",
      expectedROI: "170%",
      trafficIncrease: 135,
      salesIncrease: 132,
      brandIncrease: 144,
      loyaltyIncrease: 165,
      conversionIncrease: 128
    },
    {
      strategy: "开发个性化推荐系统，根据用户口味偏好和购买历史提供定制化产品建议。",
      tag: "个性化推荐",
      score: 4.5,
      filter: "customer",
      icon: "🔍",
      preparation: [
        "收集和分析用户口味偏好、购买历史和浏览行为数据",
        "开发推荐算法，支持基于内容和协同过滤的推荐方式",
        "设计用户口味测试问卷，帮助新用户快速建立偏好档案",
        "制定数据安全和隐私保护策略，确保合规使用用户数据"
      ],
      execution: [
        "在线上平台实施个性化推荐系统，显示'为您推荐'产品",
        "发送定制化产品推荐邮件，根据用户偏好提供相关产品",
        "提供'口味探索'功能，帮助用户发现新的可能喜欢的茶品",
        "实施A/B测试，优化推荐算法和展示方式",
        "收集用户对推荐产品的反馈，持续优化推荐准确度"
      ],
      evaluation: [
        "分析推荐产品的点击率和转化率变化",
        "评估用户探索新品类的比例和满意度",
        "统计推荐系统对客单价和购买频率的影响",
        "监测用户体验满意度变化，特别是对'被理解'感受的提升",
        "计算个性化推荐对用户终身价值的贡献"
      ],
      tags: ["数据分析", "精准营销", "用户体验"],
      expectedSales: "38%",
      expectedTraffic: "30%",
      expectedROI: "195%",
      trafficIncrease: 130,
      salesIncrease: 138,
      brandIncrease: 125,
      loyaltyIncrease: 148,
      conversionIncrease: 142
    },
    {
      strategy: "针对重要节日和用户生日，设计个性化祝福和专属优惠，增强情感连接。",
      tag: "情感营销",
      score: 4.4,
      filter: "customer",
      icon: "🎂",
      preparation: [
        "收集用户生日和重要纪念日数据，建立客户关系管理系统",
        "设计不同节日的祝福内容和视觉元素，确保个性化和诚意",
        "规划节日和生日专属优惠策略，平衡促销力度和盈利空间",
        "准备小型惊喜礼品，作为特殊订单的附赠增值服务"
      ],
      execution: [
        "在用户生日当月发送个性化祝福和专属优惠券",
        "重要节日前推送应景礼品推荐和限时折扣",
        "为VIP客户准备手写祝福卡片，增加人情味",
        "节日期间为订单添加应景包装和小惊喜，提升开箱体验",
        "鼓励用户分享收到的祝福和礼品，扩大社交传播"
      ],
      evaluation: [
        "分析生日营销活动的转化率和投资回报率",
        "评估不同节日活动的参与度和销售提升效果",
        "收集用户对个性化祝福的反馈和社交分享情况",
        "比较接收祝福用户与普通用户的忠诚度差异",
        "监测情感营销对品牌好感度的长期影响"
      ],
      tags: ["节日营销", "客户关怀", "个性化服务"],
      expectedSales: "35%",
      expectedTraffic: "28%",
      expectedROI: "185%",
      trafficIncrease: 128,
      salesIncrease: 135,
      brandIncrease: 130,
      loyaltyIncrease: 155,
      conversionIncrease: 132
    }
  ];

  return [...brandStrategies, ...productStrategies, ...promotionStrategies, ...channelStrategies, ...customerStrategies];
}

// 加载模拟数据
function loadSimulationData() {
  showLoading();
  hideError();
  hideEmptyTip();
  
  // 尝试从DataService获取策略数据
  var strategies = DataService.getMarketingStrategies();
  
  if (strategies) {
    // 如果有策略数据，直接渲染
    renderStrategyList(strategies);
    // 更新指标数据
    updateMetricsFromSimulation();
  } else {
    // 没有策略数据，但有模拟数据，生成通用策略
    loadMockStrategy();
  }
  
  // 显示策略列表和指标
  document.getElementById('strategyList').style.display = 'grid';
  document.getElementById('metricsContainer').style.display = 'flex';
  hideLoading();
}

// 从模拟数据更新指标
function updateMetricsFromSimulation() {
  // 获取数据
  var salesIncrease = DataService.getExpectedSalesIncrease();
  var trafficIncrease = DataService.getExpectedTrafficIncrease();
  var brandReputation = DataService.getBrandReputationIncrease();
  var customerLoyalty = DataService.getCustomerLoyaltyIncrease();
  
  // 更新显示
  document.getElementById('salesIncrease').textContent = typeof salesIncrease === 'number' ? salesIncrease.toFixed(1) : salesIncrease;
  document.getElementById('trafficIncrease').textContent = typeof trafficIncrease === 'number' ? trafficIncrease.toFixed(1) : trafficIncrease;
  document.getElementById('brandReputation').textContent = typeof brandReputation === 'number' ? brandReputation.toFixed(1) : brandReputation;
  document.getElementById('customerLoyalty').textContent = typeof customerLoyalty === 'number' ? customerLoyalty.toFixed(1) : customerLoyalty;
} 