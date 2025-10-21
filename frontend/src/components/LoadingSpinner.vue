<template>
  <div class="loading-spinner" :class="`type-${type}`">
    <!-- 点状加载器 -->
    <div v-if="type === 'dots'" class="dots-loader">
      <div class="dot"></div>
      <div class="dot"></div>
      <div class="dot"></div>
    </div>

    <!-- 脉冲圆环 -->
    <div v-else-if="type === 'pulse'" class="pulse-loader">
      <div class="pulse-ring"></div>
      <div class="pulse-ring"></div>
    </div>

    <!-- 渐变旋转 -->
    <div v-else-if="type === 'gradient'" class="gradient-loader">
      <div class="gradient-spinner"></div>
    </div>

    <!-- 默认: 三色旋转 -->
    <div v-else class="spinner-loader">
      <svg class="spinner-svg" viewBox="0 0 50 50">
        <circle class="spinner-path" cx="25" cy="25" r="20" fill="none" stroke-width="4"></circle>
      </svg>
    </div>

    <!-- 加载文字 -->
    <p v-if="text" class="loading-text">{{ text }}</p>
  </div>
</template>

<script setup lang="ts">
interface Props {
  type?: 'spinner' | 'dots' | 'pulse' | 'gradient'
  text?: string
}

withDefaults(defineProps<Props>(), {
  type: 'spinner',
  text: ''
})
</script>

<style scoped lang="scss">
@import '@/assets/styles/variables.scss';

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: $spacing-md;
}

.loading-text {
  margin: 0;
  font-size: $font-size-sm;
  color: var(--color-text-secondary);
  font-weight: 500;
}

// ========== 类型1: 三色旋转圆环 (默认) ==========
.spinner-loader {
  .spinner-svg {
    width: 48px;
    height: 48px;
    animation: rotate 2s linear infinite;
  }

  .spinner-path {
    stroke: var(--color-primary);
    stroke-linecap: round;
    stroke-dasharray: 90, 150;
    stroke-dashoffset: 0;
    animation: dash 1.5s ease-in-out infinite;
  }
}

@keyframes rotate {
  100% {
    transform: rotate(360deg);
  }
}

@keyframes dash {
  0% {
    stroke-dasharray: 1, 150;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -35;
  }
  100% {
    stroke-dasharray: 90, 150;
    stroke-dashoffset: -124;
  }
}

// ========== 类型2: 弹跳点 ==========
.dots-loader {
  display: flex;
  gap: 8px;
  align-items: center;

  .dot {
    width: 12px;
    height: 12px;
    background: var(--color-primary);
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out both;

    &:nth-child(1) {
      animation-delay: -0.32s;
    }

    &:nth-child(2) {
      animation-delay: -0.16s;
    }
  }
}

@keyframes bounce {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

// ========== 类型3: 脉冲圆环 ==========
.pulse-loader {
  position: relative;
  width: 48px;
  height: 48px;

  .pulse-ring {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border: 3px solid var(--color-primary);
    border-radius: 50%;
    opacity: 0;
    animation: pulse 2s cubic-bezier(0.215, 0.61, 0.355, 1) infinite;

    &:nth-child(2) {
      animation-delay: 1s;
    }
  }
}

@keyframes pulse {
  0% {
    transform: scale(0.5);
    opacity: 1;
  }
  100% {
    transform: scale(1.3);
    opacity: 0;
  }
}

// ========== 类型4: 渐变旋转 ==========
.gradient-loader {
  .gradient-spinner {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: conic-gradient(
      from 0deg,
      var(--color-primary) 0%,
      var(--color-secondary) 50%,
      transparent 50%
    );
    animation: spin-gradient 1.2s linear infinite;
    position: relative;

    &::before {
      content: '';
      position: absolute;
      top: 4px;
      left: 4px;
      right: 4px;
      bottom: 4px;
      background: var(--color-bg-primary);
      border-radius: 50%;
    }
  }
}

@keyframes spin-gradient {
  to {
    transform: rotate(360deg);
  }
}
</style>
