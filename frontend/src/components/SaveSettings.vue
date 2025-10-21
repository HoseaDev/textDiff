<template>
  <div class="save-settings">
    <!-- 保存设置标题 -->
    <div class="settings-section">
      <h3 class="section-title">保存设置</h3>

      <div class="setting-group">
        <label class="setting-label">保存模式</label>
        <select v-model="settings.saveMode" class="input" @change="updateSettings">
          <option value="manual">仅手动保存</option>
          <option value="auto">仅自动保存</option>
          <option value="hybrid">手动 + 自动保存（推荐）</option>
        </select>
        <p class="setting-help">
          手动模式需要点击保存按钮或按 Ctrl+S；自动模式会定期自动保存；混合模式两者都支持。
        </p>
      </div>

      <div v-if="settings.saveMode !== 'manual'" class="setting-group">
        <label class="setting-label">
          自动保存间隔：{{ settings.autoSaveInterval }} 秒
        </label>
        <input
          type="range"
          min="5"
          max="300"
          step="5"
          v-model.number="settings.autoSaveInterval"
          class="range-input"
          @change="updateSettings"
        />
        <div class="range-labels">
          <span>5秒</span>
          <span>300秒</span>
        </div>
      </div>

      <div class="setting-group">
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="settings.confirmBeforeSave"
            @change="updateSettings"
          />
          <span>手动保存前需要确认</span>
        </label>
      </div>

      <div class="setting-group">
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="settings.warnBeforeLeave"
            @change="updateSettings"
          />
          <span>离开页面前警告未保存的更改</span>
        </label>
      </div>
    </div>

    <!-- 界面设置 -->
    <div class="settings-section">
      <h3 class="section-title">界面设置</h3>

      <div class="setting-group">
        <label class="setting-label">加载动画样式</label>
        <select v-model="loadingType" class="input" @change="saveLoadingType">
          <option value="spinner">流畅圆环（推荐）</option>
          <option value="dots">弹跳圆点</option>
          <option value="pulse">脉冲扩散</option>
          <option value="gradient">渐变旋转</option>
        </select>
        <p class="setting-help">
          选择您喜欢的加载动画效果
        </p>
      </div>

      <!-- 动画预览 -->
      <div class="setting-group">
        <label class="setting-label">动画预览</label>
        <div class="animation-preview">
          <LoadingSpinner :type="loadingType" text="这是预览效果" />
        </div>
      </div>
    </div>

    <!-- 保存按钮 -->
    <div class="setting-group">
      <button class="btn btn-primary" @click="saveAndClose">
        保存全部设置
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useDocumentStore } from '@/stores/document'
import type { SaveSettings as SaveSettingsType } from '@/types'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

const documentStore = useDocumentStore()

const settings = reactive<SaveSettingsType>({ ...documentStore.saveSettings })
const loadingType = ref<'spinner' | 'dots' | 'pulse' | 'gradient'>('spinner')

// 从 localStorage 加载加载动画类型
onMounted(() => {
  const saved = localStorage.getItem('loadingAnimationType')
  if (saved && ['spinner', 'dots', 'pulse', 'gradient'].includes(saved)) {
    loadingType.value = saved as any
  }
})

function updateSettings() {
  documentStore.updateSaveSettings(settings)
}

function saveLoadingType() {
  localStorage.setItem('loadingAnimationType', loadingType.value)
}

function saveAndClose() {
  updateSettings()
  saveLoadingType()
  // 可以添加关闭模态框的逻辑
}
</script>

<style scoped lang="scss">
@import '@/assets/styles/variables.scss';

.save-settings {
  display: flex;
  flex-direction: column;
  gap: $spacing-xl;
}

.settings-section {
  display: flex;
  flex-direction: column;
  gap: $spacing-lg;
  padding-bottom: $spacing-lg;
  border-bottom: 1px solid var(--color-border);

  &:last-of-type {
    border-bottom: none;
  }
}

.section-title {
  font-size: $font-size-lg;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 $spacing-sm 0;
}

.setting-group {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.animation-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: $spacing-xl;
  background: var(--color-bg-tertiary);
  border-radius: $border-radius-md;
  min-height: 120px;
}

.setting-label {
  font-size: $font-size-sm;
  font-weight: 600;
  color: var(--color-text-primary);
}

.setting-help {
  font-size: $font-size-xs;
  color: var(--color-text-secondary);
  margin: 0;
  line-height: 1.5;
}

.input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--color-input-border);
  border-radius: $border-radius-md;
  font-size: $font-size-sm;
  background: var(--color-input-bg);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all $transition-fast;

  &:focus {
    outline: none;
    border-color: var(--color-input-focus-border);
    box-shadow: 0 0 0 2px var(--color-input-focus-shadow);
  }

  &:hover {
    border-color: var(--color-input-focus-border);
  }
}

.range-input {
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: var(--color-bg-tertiary);
  outline: none;
  -webkit-appearance: none;
  appearance: none;

  &::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--color-primary);
    cursor: pointer;
    transition: all $transition-fast;

    &:hover {
      background: var(--color-primary-hover);
      transform: scale(1.1);
    }
  }

  &::-moz-range-thumb {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--color-primary);
    cursor: pointer;
    border: none;
    transition: all $transition-fast;

    &:hover {
      background: var(--color-primary-hover);
      transform: scale(1.1);
    }
  }

  &::-webkit-slider-runnable-track {
    height: 6px;
    border-radius: 3px;
    background: var(--color-bg-tertiary);
  }

  &::-moz-range-track {
    height: 6px;
    border-radius: 3px;
    background: var(--color-bg-tertiary);
  }
}

.range-labels {
  display: flex;
  justify-content: space-between;
  font-size: $font-size-xs;
  color: var(--color-text-secondary);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  cursor: pointer;
  user-select: none;
  padding: $spacing-sm;
  border-radius: $border-radius-md;
  transition: background $transition-fast;

  &:hover {
    background: var(--color-bg-hover);
  }

  input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
    accent-color: var(--color-primary);
  }

  span {
    font-size: $font-size-sm;
    color: var(--color-text-primary);
  }
}
</style>
