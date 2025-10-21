<template>
  <div class="save-settings">
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

    <div class="setting-group">
      <button class="btn btn-primary" @click="saveAndClose">
        保存设置
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useDocumentStore } from '@/stores/document'
import type { SaveSettings as SaveSettingsType } from '@/types'

const documentStore = useDocumentStore()

const settings = reactive<SaveSettingsType>({ ...documentStore.saveSettings })

function updateSettings() {
  documentStore.updateSaveSettings(settings)
}

function saveAndClose() {
  updateSettings()
  // 可以添加关闭模态框的逻辑
}
</script>

<style scoped lang="scss">
@import '@/assets/styles/variables.scss';

.save-settings {
  display: flex;
  flex-direction: column;
  gap: $spacing-lg;
}

.setting-group {
  display: flex;
  flex-direction: column;
  gap: $spacing-sm;
}

.setting-label {
  font-size: $font-size-sm;
  font-weight: 600;
  color: $color-text-primary;
}

.setting-help {
  font-size: $font-size-xs;
  color: $color-text-secondary;
  margin: 0;
}

.range-input {
  width: 100%;
}

.range-labels {
  display: flex;
  justify-content: space-between;
  font-size: $font-size-xs;
  color: $color-text-secondary;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: $spacing-sm;
  cursor: pointer;
  user-select: none;

  input[type="checkbox"] {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }

  span {
    font-size: $font-size-sm;
  }
}
</style>
