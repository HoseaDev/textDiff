<template>
  <div class="settings-page">
    <div class="settings-container">
      <div class="settings-header">
        <h1>设置</h1>
        <p class="subtitle">管理您的偏好和应用配置</p>
      </div>

      <div class="settings-content">
        <!-- 保存设置 -->
        <section class="settings-section">
          <h2 class="section-title">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z" stroke-width="2"/>
              <polyline points="17 21 17 13 7 13 7 21" stroke-width="2"/>
              <polyline points="7 3 7 8 15 8" stroke-width="2"/>
            </svg>
            保存设置
          </h2>

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
        </section>

        <!-- 界面设置 -->
        <section class="settings-section">
          <h2 class="section-title">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <rect x="3" y="3" width="18" height="18" rx="2" stroke-width="2"/>
              <path d="M9 3v18M15 3v18M3 9h18M3 15h18" stroke-width="2"/>
            </svg>
            界面设置
          </h2>

          <div class="setting-group">
            <label class="setting-label">主题模式</label>
            <div class="theme-selector">
              <button
                class="theme-option"
                :class="{ active: themeStore.mode === 'light' }"
                @click="themeStore.setTheme('light')"
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <circle cx="12" cy="12" r="5" stroke-width="2"/>
                  <path d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" stroke-width="2"/>
                </svg>
                <span>亮色</span>
              </button>
              <button
                class="theme-option"
                :class="{ active: themeStore.mode === 'dark' }"
                @click="themeStore.setTheme('dark')"
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" stroke-width="2"/>
                </svg>
                <span>暗色</span>
              </button>
            </div>
            <p class="setting-help">选择您喜欢的主题模式</p>
          </div>

          <div class="setting-group">
            <label class="setting-label">加载动画样式</label>
            <div class="animation-selector">
              <button
                v-for="type in animationTypes"
                :key="type.value"
                class="animation-option"
                :class="{ active: loadingType === type.value }"
                @click="selectAnimation(type.value)"
              >
                <div class="animation-icon">{{ type.icon }}</div>
                <span>{{ type.label }}</span>
              </button>
            </div>
            <p class="setting-help">选择您喜欢的加载动画效果</p>
          </div>

          <div class="setting-group">
            <label class="setting-label">动画预览</label>
            <div class="animation-preview">
              <LoadingSpinner :type="loadingType" text="这是预览效果" />
            </div>
          </div>
        </section>

        <!-- 保存按钮 -->
        <div class="settings-actions">
          <button class="btn btn-secondary" @click="resetSettings">
            重置为默认值
          </button>
          <button class="btn btn-primary" @click="saveAllSettings">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="20 6 9 17 4 12" stroke-width="2"/>
            </svg>
            保存所有设置
          </button>
        </div>

        <!-- 保存提示 -->
        <div v-if="showSaveSuccess" class="save-notification">
          ✓ 设置已保存
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useDocumentStore } from '@/stores/document'
import { useThemeStore } from '@/stores/theme'
import type { SaveSettings as SaveSettingsType } from '@/types'
import LoadingSpinner from '@/components/LoadingSpinner.vue'

const documentStore = useDocumentStore()
const themeStore = useThemeStore()

const settings = reactive<SaveSettingsType>({
  saveMode: 'hybrid',
  autoSaveInterval: 30,
  confirmBeforeSave: false,
  warnBeforeLeave: true
})

const loadingType = ref<'spinner' | 'dots' | 'pulse' | 'gradient'>('spinner')
const showSaveSuccess = ref(false)

const animationTypes = [
  { value: 'spinner', label: '流畅圆环', icon: '◐' },
  { value: 'dots', label: '弹跳圆点', icon: '⋯' },
  { value: 'pulse', label: '脉冲扩散', icon: '◎' },
  { value: 'gradient', label: '渐变旋转', icon: '◑' }
] as const

onMounted(() => {
  // 加载保存设置
  documentStore.loadSaveSettings()
  Object.assign(settings, documentStore.saveSettings)

  // 加载加载动画类型
  const saved = localStorage.getItem('loadingAnimationType')
  if (saved && ['spinner', 'dots', 'pulse', 'gradient'].includes(saved)) {
    loadingType.value = saved as any
  }
})

function updateSettings() {
  documentStore.updateSaveSettings(settings)
}

function selectAnimation(type: 'spinner' | 'dots' | 'pulse' | 'gradient') {
  loadingType.value = type
}

function saveLoadingType() {
  localStorage.setItem('loadingAnimationType', loadingType.value)
}

function saveAllSettings() {
  updateSettings()
  saveLoadingType()

  // 显示保存成功提示
  showSaveSuccess.value = true
  setTimeout(() => {
    showSaveSuccess.value = false
  }, 2000)
}

function resetSettings() {
  if (confirm('确定要重置所有设置为默认值吗?')) {
    settings.saveMode = 'hybrid'
    settings.autoSaveInterval = 30
    settings.confirmBeforeSave = false
    settings.warnBeforeLeave = true
    loadingType.value = 'spinner'
    themeStore.setTheme('light')
    saveAllSettings()
  }
}
</script>

<style scoped lang="scss">
@import '@/assets/styles/variables.scss';

.settings-page {
  min-height: calc(100vh - 60px);
  background: var(--color-bg-primary);
  padding: $spacing-xl $spacing-lg;

  @include mobile {
    padding: $spacing-md;
  }
}

.settings-container {
  max-width: 800px;
  margin: 0 auto;
}

.settings-header {
  margin-bottom: $spacing-2xl;

  h1 {
    font-size: $font-size-2xl;
    font-weight: 700;
    color: var(--color-text-primary);
    margin: 0 0 $spacing-xs 0;
  }

  .subtitle {
    font-size: $font-size-base;
    color: var(--color-text-secondary);
    margin: 0;
  }
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: $spacing-2xl;
}

.settings-section {
  background: var(--color-card-bg);
  border: 1px solid var(--color-card-border);
  border-radius: $border-radius-lg;
  padding: $spacing-xl;
  box-shadow: var(--color-card-shadow);

  @include mobile {
    padding: $spacing-lg;
  }
}

.section-title {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  font-size: $font-size-lg;
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 $spacing-lg 0;

  svg {
    color: var(--color-primary);
  }
}

.setting-group {
  margin-bottom: $spacing-lg;

  &:last-child {
    margin-bottom: 0;
  }
}

.setting-label {
  display: block;
  font-size: $font-size-sm;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: $spacing-sm;
}

.setting-help {
  margin: $spacing-xs 0 0 0;
  font-size: $font-size-xs;
  color: var(--color-text-secondary);
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
}

.range-labels {
  display: flex;
  justify-content: space-between;
  font-size: $font-size-xs;
  color: var(--color-text-secondary);
  margin-top: $spacing-xs;
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

// 主题选择器
.theme-selector {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: $spacing-md;
  margin-bottom: $spacing-xs;
}

.theme-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-lg;
  border: 2px solid var(--color-border);
  border-radius: $border-radius-md;
  background: var(--color-bg-secondary);
  cursor: pointer;
  transition: all $transition-fast;

  svg {
    color: var(--color-text-secondary);
  }

  span {
    font-size: $font-size-sm;
    font-weight: 500;
    color: var(--color-text-primary);
  }

  &:hover {
    border-color: var(--color-primary);
    transform: translateY(-2px);
  }

  &.active {
    border-color: var(--color-primary);
    background: var(--color-primary-light);

    svg {
      color: var(--color-primary);
    }
  }
}

// 动画选择器
.animation-selector {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: $spacing-md;
  margin-bottom: $spacing-xs;

  @include mobile {
    grid-template-columns: repeat(2, 1fr);
  }
}

.animation-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-sm;
  padding: $spacing-lg $spacing-md;
  border: 2px solid var(--color-border);
  border-radius: $border-radius-md;
  background: var(--color-bg-secondary);
  cursor: pointer;
  transition: all $transition-fast;
  min-height: 100px;

  .animation-icon {
    font-size: 32px;
    color: var(--color-text-secondary);
    transition: all $transition-fast;
  }

  span {
    font-size: $font-size-xs;
    font-weight: 500;
    color: var(--color-text-primary);
  }

  &:hover {
    border-color: var(--color-primary);
    transform: translateY(-2px);

    .animation-icon {
      color: var(--color-primary);
      transform: scale(1.1);
    }
  }

  &.active {
    border-color: var(--color-primary);
    background: var(--color-primary-light);

    .animation-icon {
      color: var(--color-primary);
    }
  }
}

.animation-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: $spacing-2xl;
  background: var(--color-bg-tertiary);
  border-radius: $border-radius-md;
  min-height: 150px;
}

// 操作按钮
.settings-actions {
  display: flex;
  justify-content: flex-end;
  gap: $spacing-md;
  padding-top: $spacing-lg;

  @include mobile {
    flex-direction: column-reverse;
  }

  .btn {
    display: flex;
    align-items: center;
    gap: $spacing-xs;
    padding: $spacing-sm $spacing-lg;
    font-size: $font-size-base;
    font-weight: 600;
    border-radius: $border-radius-md;
    cursor: pointer;
    transition: all $transition-fast;
    border: none;

    @include mobile {
      width: 100%;
      justify-content: center;
    }
  }

  .btn-primary {
    background: var(--color-primary);
    color: white;

    &:hover {
      background: var(--color-primary-hover);
      transform: translateY(-1px);
      box-shadow: 0 4px 12px var(--color-shadow);
    }
  }

  .btn-secondary {
    background: var(--color-button-secondary-bg);
    color: var(--color-button-secondary-text);
    border: 1px solid var(--color-border);

    &:hover {
      background: var(--color-button-secondary-hover);
    }
  }
}

// 保存提示
.save-notification {
  position: fixed;
  bottom: $spacing-xl;
  right: $spacing-xl;
  padding: $spacing-md $spacing-lg;
  background: var(--color-success);
  color: white;
  border-radius: $border-radius-md;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  font-size: $font-size-sm;
  font-weight: 500;
  animation: slideInRight 0.3s ease-out;
  z-index: 1000;

  @include mobile {
    bottom: $spacing-md;
    right: $spacing-md;
    left: $spacing-md;
    text-align: center;
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(100px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>
