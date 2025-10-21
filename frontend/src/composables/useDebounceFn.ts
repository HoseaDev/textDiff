/**
 * 防抖函数 Composable
 */
import { ref, onUnmounted } from 'vue'

export function useDebounceFn<T extends (...args: any[]) => any>(
  fn: T,
  delay: number = 300
) {
  const timeoutId = ref<number | null>(null)

  const debouncedFn = (...args: Parameters<T>) => {
    if (timeoutId.value !== null) {
      clearTimeout(timeoutId.value)
    }

    timeoutId.value = window.setTimeout(() => {
      fn(...args)
      timeoutId.value = null
    }, delay)
  }

  onUnmounted(() => {
    if (timeoutId.value !== null) {
      clearTimeout(timeoutId.value)
    }
  })

  return debouncedFn
}
