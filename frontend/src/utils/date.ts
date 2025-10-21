/**
 * 时间格式化工具
 * 处理后端返回的 UTC 时间，转换为本地时区显示
 */
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

// 扩展 dayjs 插件
dayjs.extend(utc)
dayjs.extend(timezone)
dayjs.extend(relativeTime)

// 设置默认语言为中文
dayjs.locale('zh-cn')

// 默认时区：上海（东八区）
const DEFAULT_TIMEZONE = 'Asia/Shanghai'

/**
 * 格式化日期时间
 * @param date - 日期字符串或 Date 对象
 * @param format - 格式化模板，默认 'YYYY-MM-DD HH:mm:ss'
 * @returns 格式化后的时间字符串
 */
export function formatDate(date: string | Date | null | undefined, format = 'YYYY-MM-DD HH:mm:ss'): string {
  if (!date) return '-'

  // 后端已经返回带时区的 ISO 字符串，直接解析即可
  return dayjs(date).format(format)
}

/**
 * 格式化为相对时间
 * @param date - 日期字符串或 Date 对象
 * @returns 相对时间字符串，例如 "3分钟前"
 */
export function formatRelativeTime(date: string | Date | null | undefined): string {
  if (!date) return '-'

  return dayjs(date).fromNow()
}

/**
 * 格式化为短日期
 * @param date - 日期字符串或 Date 对象
 * @returns 格式化后的日期，例如 "2024-01-01"
 */
export function formatShortDate(date: string | Date | null | undefined): string {
  return formatDate(date, 'YYYY-MM-DD')
}

/**
 * 格式化为时间
 * @param date - 日期字符串或 Date 对象
 * @returns 格式化后的时间，例如 "14:30:00"
 */
export function formatTime(date: string | Date | null | undefined): string {
  return formatDate(date, 'HH:mm:ss')
}

/**
 * 格式化为友好的日期时间
 * 今天显示 "今天 HH:mm"
 * 昨天显示 "昨天 HH:mm"
 * 其他显示 "MM-DD HH:mm"
 * 超过一年显示 "YYYY-MM-DD"
 */
export function formatFriendly(date: string | Date | null | undefined): string {
  if (!date) return '-'

  const d = dayjs(date)
  const now = dayjs()

  // 判断是否是今天
  if (d.isSame(now, 'day')) {
    return `今天 ${d.format('HH:mm')}`
  }

  // 判断是否是昨天
  if (d.isSame(now.subtract(1, 'day'), 'day')) {
    return `昨天 ${d.format('HH:mm')}`
  }

  // 判断是否在今年
  if (d.isSame(now, 'year')) {
    return d.format('MM-DD HH:mm')
  }

  // 超过一年
  return d.format('YYYY-MM-DD')
}

/**
 * 判断是否是今天
 */
export function isToday(date: string | Date | null | undefined): boolean {
  if (!date) return false
  return dayjs(date).isSame(dayjs(), 'day')
}

/**
 * 判断是否是本周
 */
export function isThisWeek(date: string | Date | null | undefined): boolean {
  if (!date) return false
  return dayjs(date).isSame(dayjs(), 'week')
}

/**
 * 获取当前时间（本地时区）
 */
export function now(): Date {
  return new Date()
}

/**
 * 将本地时间转换为 UTC ISO 字符串（用于发送给后端）
 */
export function toUTCString(date: Date | string): string {
  return dayjs(date).utc().toISOString()
}
