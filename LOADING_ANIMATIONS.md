# 加载动画说明

## 更新时间
2025-10-21

## 新的加载动画组件

创建了一个全新的 `LoadingSpinner.vue` 组件,提供4种精美的加载动画样式。

## 可用的动画类型

### 1. **spinner** (默认 - 推荐)
三色旋转圆环,流畅的线条动画
- **特点**: 优雅、流畅、现代
- **适用**: 页面加载、数据获取
- **动画**: SVG路径动画,平滑的旋转和虚线效果

```vue
<LoadingSpinner type="spinner" text="加载中..." />
```

### 2. **dots**
三个弹跳的圆点
- **特点**: 轻快、活泼
- **适用**: 按钮内、小区域加载
- **动画**: 三个点依次弹跳缩放

```vue
<LoadingSpinner type="dots" text="处理中..." />
```

### 3. **pulse**
脉冲扩散的圆环
- **特点**: 柔和、舒缓
- **适用**: 等待提示、后台任务
- **动画**: 两个圆环从中心向外扩散

```vue
<LoadingSpinner type="pulse" text="请稍候..." />
```

### 4. **gradient**
渐变圆环旋转
- **特点**: 炫酷、现代
- **适用**: 品牌展示、特殊场景
- **动画**: 渐变色圆环旋转

```vue
<LoadingSpinner type="gradient" text="加载中..." />
```

## 使用方法

### 基本使用

```vue
<template>
  <div v-if="isLoading">
    <LoadingSpinner type="spinner" text="加载中..." />
  </div>
</template>

<script setup>
import LoadingSpinner from '@/components/LoadingSpinner.vue'
</script>
```

### 不显示文字

```vue
<LoadingSpinner type="dots" />
```

### 自定义文字

```vue
<LoadingSpinner type="pulse" text="正在保存您的数据..." />
```

## 已更新的位置

### 1. DocumentListView.vue
使用 `spinner` 类型显示文档列表加载状态

### 2. 全局样式 (global.scss)
更新了内联 `.loading` 类,改为更流畅的双边框旋转动画

### 3. AppLayout.vue
保存状态指示器中的小型旋转动画,改为透明边框样式

## 设计改进

### 之前的问题 ❌
- 单调的圆环旋转
- 视觉效果生硬
- 没有特色

### 现在的优势 ✅
- **4种精美样式**供选择
- **SVG动画**更流畅
- **主题适配**自动适应亮色/暗色主题
- **性能优化**使用CSS动画和SVG
- **可访问性**可配置文字提示

## 动画性能

所有动画都使用CSS3和SVG,性能优异:
- ✅ GPU加速 (transform, opacity)
- ✅ 无JavaScript计算
- ✅ 60fps流畅动画
- ✅ 低CPU占用

## 主题支持

所有加载动画完全支持主题切换:
- 亮色主题: 使用品牌主色调
- 暗色主题: 自动调整颜色对比度
- 颜色变量: `var(--color-primary)`, `var(--color-secondary)`

## 示例效果

### Spinner (三色旋转)
```
    ◡◡◡
   ◡   ◡
  ◡     ◡
   ◡   ◡
    ◡◡◡
```
流畅的圆环线条旋转,虚线长度动态变化

### Dots (弹跳点)
```
●  ●  ●
 ●●●
  ●  ●  ●
```
三个点依次弹跳,有节奏感

### Pulse (脉冲环)
```
    ○
   ◯
  〇
 ○
```
从中心向外扩散的波纹效果

### Gradient (渐变旋转)
```
   ◓
   ◑
   ◒
   ◐
```
渐变色圆环快速旋转

## 推荐使用场景

| 场景 | 推荐类型 | 理由 |
|------|---------|------|
| 页面初始加载 | spinner | 专业、流畅 |
| 数据列表加载 | spinner/pulse | 视觉舒适 |
| 按钮loading | dots | 体积小巧 |
| 提交表单 | spinner | 清晰明确 |
| 文件上传 | pulse | 持续感强 |
| 炫酷展示 | gradient | 视觉冲击 |

## 未来扩展

可以考虑添加:
- [ ] 进度条样式 (带百分比)
- [ ] 骨架屏样式
- [ ] 自定义颜色参数
- [ ] 尺寸参数 (small/medium/large)
